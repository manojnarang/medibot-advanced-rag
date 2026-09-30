"""Component 4: SQL RAG over mediassist.db (claims, maintenance_tickets).

Three explicit steps, per the assignment brief:
  1. Translate the question into SQL with an LLM, given the real schema as
     context (app.db.sqlite.get_schema_summary()).
  2. Clean the raw LLM output down to just the SQL statement - LLMs often
     wrap it in a ```sql fence or add explanatory text.
  3. Execute the cleaned SQL, then pass the result back to the LLM to
     produce a natural language answer.

Only ever called for roles permitted to use SQL RAG (billing_executive,
admin) - see app.rbac.access_matrix.can_use_sql_rag, enforced in
app.chat.service before this function is reached.
"""
import logging
import re
import sqlite3

from fastapi import HTTPException, status

from app.db.sqlite import get_connection, get_schema_summary
from app.rag.llm import generate

logger = logging.getLogger(__name__)

_SQL_FENCE_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)

_SQL_SYSTEM_PROMPT_TEMPLATE = """You translate natural language questions into a single SQLite \
SELECT query for the MediAssist Health Network database.

Schema:
{schema}

Rules:
- Output ONLY the SQL query, wrapped in a ```sql code fence. No explanation, no commentary.
- Write exactly one SELECT statement. Never write INSERT, UPDATE, DELETE, DROP, or any other \
statement that modifies data.
- Use only the tables and columns listed above.
- Stored text values (department, status, category, etc.) are lowercase with underscores, e.g. \
'cardiology', 'in_progress'. Always compare with LOWER(column) = LOWER('value') rather than \
guessing the exact case, since a case mismatch silently returns zero rows instead of an error.
- If the question is broad or asks for a general summary/overview (e.g. "tell me about X",
"summarize Y") rather than one specific fact, write an aggregate query (COUNT, GROUP BY, AVG,
MAX/MIN, etc.) that directly answers it. Never write a raw "SELECT *" that just dumps individual
rows - only a small sample of those rows is ever shown back to you afterward, so any statistic you
stated from them would be a guess from a partial sample, not a real computed answer.
- For a breakdown by category (status, department, etc.), use "GROUP BY that_column" rather than
manually listing categories with CASE/WHEN - you don't reliably know every value that column
actually contains, and GROUP BY returns whatever real values exist instead of you guessing them.
"""

_ANSWER_SYSTEM_PROMPT = (
    "You are MediBot, an assistant for MediAssist Health Network staff. Given a question and "
    "the SQL query results that answer it, write a concise, natural language answer. All monetary "
    "amounts in this database are in Indian Rupees - format them with the ₹ symbol, not $. If the "
    "results are empty, say so plainly rather than guessing. Only state numbers that literally "
    "appear in the query results below - never compute, estimate, or add any figure (a count, an "
    "average, a duration, a category not present in the results) that the SQL query didn't already "
    "return. If the results don't fully answer the question, say what's missing rather than filling "
    "the gap with an invented number.\n\n"
    "If the question was broad or open-ended (asking for a general summary rather than one specific "
    "fact) and the query grouped the data by a particular dimension (e.g. status, department, claim "
    "type), end your answer with one short sentence naming the dimension it was grouped by and "
    "inviting a more specific follow-up - for example: \"This groups claims by department and status; "
    "ask for a breakdown by claim type or a specific department instead if you want a different view.\" "
    "Skip this sentence entirely for a narrow question that already has one clear answer."
)

_MAX_ROWS_IN_PROMPT = 20


def _clean_sql(raw_sql: str) -> str:
    """Extract just the SQL statement from raw LLM output."""
    match = _SQL_FENCE_RE.search(raw_sql)
    sql = match.group(1) if match else raw_sql
    sql = sql.strip()
    if ";" in sql:
        sql = sql.split(";")[0]
    return sql.strip()


def _llm_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Analytics is temporarily unavailable. Please try again shortly.",
    )


def sql_rag_chain(question: str) -> str:
    # Step 1: NL -> SQL
    system_prompt = _SQL_SYSTEM_PROMPT_TEMPLATE.format(schema=get_schema_summary())
    try:
        raw_sql = generate(system_prompt=system_prompt, user_prompt=question, temperature=0.0)
    except Exception:
        logger.exception("SQL generation failed (LLM provider unavailable)")
        raise _llm_unavailable()

    # Step 2: clean the raw LLM output down to just the SQL statement
    sql = _clean_sql(raw_sql)
    if not sql.upper().startswith("SELECT"):
        return (
            "I couldn't safely answer that as a database query - the generated query wasn't a "
            "plain SELECT statement."
        )

    # Step 3: execute, then turn the result back into a natural language answer.
    # sqlite3.Error here means the *generated SQL* was bad (a normal, expected
    # outcome worth explaining in plain language) - different in kind from the
    # LLM provider itself being unreachable, which is a real service outage.
    try:
        with get_connection() as conn:
            rows = [dict(row) for row in conn.execute(sql).fetchall()]
    except sqlite3.Error as exc:
        return f"I couldn't run that query against the database ({exc})."

    row_count = len(rows)
    preview = rows[:_MAX_ROWS_IN_PROMPT]
    truncated_note = f" (showing first {_MAX_ROWS_IN_PROMPT} of {row_count})" if row_count > _MAX_ROWS_IN_PROMPT else ""
    result_summary = f"Query: {sql}\nRows returned: {row_count}{truncated_note}\n{preview}"

    try:
        return generate(
            system_prompt=_ANSWER_SYSTEM_PROMPT,
            user_prompt=f"Question: {question}\n\n{result_summary}",
            temperature=0.0,
        )
    except Exception:
        logger.exception("SQL answer generation failed (LLM provider unavailable)")
        raise _llm_unavailable()
