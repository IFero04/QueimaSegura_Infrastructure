from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()


@router.get('/types', status_code=status.HTTP_200_OK)
def get_types():
    from api.static import get_types
    return get_types()

@router.get('/reasons', status_code=status.HTTP_200_OK)
def get_reasons():
    from api.static import get_reasons
    return get_reasons()

@router.get('/controller', status_code=status.HTTP_200_OK)
def get_controller():
    from api.static import get_controller
    return get_controller()
