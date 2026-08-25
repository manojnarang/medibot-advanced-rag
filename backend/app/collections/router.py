from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.core.config import get_settings
from app.rbac.access_matrix import COLLECTIONS, get_accessible_collections, is_valid_role

router = APIRouter(tags=["collections"])
settings = get_settings()


class CollectionOut(BaseModel):
    name: str
    label: str
    description: str
    documents: list[str]


class CollectionsResponse(BaseModel):
    role: str
    accessible_collections: list[CollectionOut]


def _documents_in(collection: str) -> list[str]:
    """Best-effort listing of source documents on disk for a collection.
    Purely informational (filesystem listing) - no parsing/AI involved."""
    folder = settings.mediassist_data_path / collection
    if not folder.is_dir():
        return []
    return sorted(p.name for p in folder.iterdir() if p.is_file())


@router.get("/collections/{role}", response_model=CollectionsResponse)
def list_collections(role: str, current_user: CurrentUser = Depends(get_current_user)) -> CollectionsResponse:
    if not is_valid_role(role):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown role: {role}")

    # A caller may only inspect their own role's collections, unless they're an admin.
    if current_user.role != "admin" and current_user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only view collections for your own role.",
        )

    accessible_names = get_accessible_collections(role)
    accessible = [
        CollectionOut(
            name=COLLECTIONS[name].name,
            label=COLLECTIONS[name].label,
            description=COLLECTIONS[name].description,
            documents=_documents_in(name),
        )
        for name in accessible_names
    ]
    return CollectionsResponse(role=role, accessible_collections=accessible)
