"""Single source of truth for role -> document-collection access.

This mapping is what gets turned into a metadata filter (`access_roles`) at
the vector-store query layer once Components 1-3 are implemented, so that
restricted chunks are never returned to the application in the first place -
RBAC is enforced at retrieval, not by filtering results after the fact.
"""
from dataclasses import dataclass

ALL_ROLES = ["doctor", "nurse", "billing_executive", "technician", "admin"]

SQL_RAG_ROLES = {"billing_executive", "admin"}


@dataclass(frozen=True)
class CollectionInfo:
    name: str
    label: str
    description: str
    roles: tuple[str, ...]


COLLECTIONS: dict[str, CollectionInfo] = {
    "general": CollectionInfo(
        name="general",
        label="General",
        description="Staff handbook, leave policy, code of conduct, general FAQs.",
        roles=tuple(ALL_ROLES),
    ),
    "clinical": CollectionInfo(
        name="clinical",
        label="Clinical",
        description="Treatment protocols, drug formulary, diagnostic reference.",
        roles=("doctor", "admin"),
    ),
    "nursing": CollectionInfo(
        name="nursing",
        label="Nursing",
        description="ICU nursing procedures, infection control guidelines.",
        roles=("nurse", "doctor", "admin"),
    ),
    "billing": CollectionInfo(
        name="billing",
        label="Billing & Insurance",
        description="Insurance billing codes, claim submission guide.",
        roles=("billing_executive", "admin"),
    ),
    "equipment": CollectionInfo(
        name="equipment",
        label="Equipment",
        description="Equipment operation & maintenance manual.",
        roles=("technician", "admin"),
    ),
}


def is_valid_role(role: str) -> bool:
    return role in ALL_ROLES


def get_accessible_collections(role: str) -> list[str]:
    return [c.name for c in COLLECTIONS.values() if role in c.roles]


def can_access_collection(role: str, collection: str) -> bool:
    info = COLLECTIONS.get(collection)
    return info is not None and role in info.roles


def can_use_sql_rag(role: str) -> bool:
    return role in SQL_RAG_ROLES


def restricted_collections_for(role: str) -> list[str]:
    return [c.name for c in COLLECTIONS.values() if role not in c.roles]
