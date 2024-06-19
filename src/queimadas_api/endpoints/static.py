from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()


@router.get('/types', status_code=status.HTTP_200_OK)
def get_types():
    from api.static import get_types
    return get_types()