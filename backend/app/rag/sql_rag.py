"""Component 4: SQL RAG over mediassist.db (claims, maintenance_tickets).

TODO - implement `sql_rag_chain` as a plain Python function with three
explicit steps:
  1. Translate `question` into a SQL query using an LLM (app.rag.llm.generate),
     giving it the schema from app.db.sqlite.get_schema_summary() as context.
  2. Clean the raw LLM output to extract only the SQL statement (LLMs often
     wrap SQL in ```sql fences or prefix it with explanation text) before
     executing it.
  3. Execute the cleaned SQL against the database via
     app.db.sqlite.get_connection(), then pass the result back to the LLM to
     produce a natural language answer.

This is only ever called for roles permitted to use SQL RAG
(billing_executive, admin) - see app.rbac.access_matrix.can_use_sql_rag,
enforced in app.chat.service before this function is reached.
"""


def sql_rag_chain(question: str) -> str:
    raise NotImplementedError(
        "Implement the 3-step SQL RAG chain: NL -> SQL (LLM), clean SQL, "
        "execute against mediassist.db, then NL answer (LLM)."
    )
