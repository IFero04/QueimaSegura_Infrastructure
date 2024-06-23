from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()


@router.get('', status_code=status.HTTP_202_ACCEPTED)
def get_location(search: str):
    from api.location import handle_location_response
    return handle_location_response(search)