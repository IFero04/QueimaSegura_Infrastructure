from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()


@router.get('', status_code=status.HTTP_202_ACCEPTED)
def get_location(user_id: str, session_id: str, search: str):
    from api.location import handle_location_response
    return handle_location_response(user_id, session_id, search)

@router.get('/map', status_code=status.HTTP_202_ACCEPTED)
def get_zip_code_lat_lng(user_id: str, session_id: str, lat: float, lng: float):
    from api.location import get_zip_code_by_lat_lng_response
    return get_zip_code_by_lat_lng_response(user_id, session_id, lat, lng)