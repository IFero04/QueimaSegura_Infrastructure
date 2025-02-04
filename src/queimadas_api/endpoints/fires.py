from pydantic import BaseModel
from typing import Union
from fastapi import APIRouter, status

router = APIRouter()

class Fire(BaseModel):
    date: str
    typeId: int
    reasonId: int
    zipCodeId: int
    location: Union[str, None] = None
    observations: Union[str, None] = None


@router.post('/{user_id}', status_code=status.HTTP_201_CREATED)
def new_fire(user_id: str, session_id: str, fire: Fire):
    from api.fires import create_fire
    return create_fire(user_id, session_id, fire)

@router.get('/{user_id}', status_code=status.HTTP_200_OK)
def get_fires_by_user(user_id: str, session_id: str):
    from api.fires import get_user_fires
    return get_user_fires(user_id, session_id)

@router.get('/{user_id}/{fire_id}', status_code=status.HTTP_200_OK)
def get_fire_detail(user_id: str, session_id: str, fire_id: str):
    from api.fires import get_fire_detail
    return get_fire_detail(user_id, session_id, fire_id)

@router.delete('/{user_id}/{fire_id}', status_code=status.HTTP_200_OK)
def delete_fire(user_id: str, session_id: str, fire_id: str):
    from api.fires import delete_fire
    return delete_fire(user_id, session_id, fire_id)