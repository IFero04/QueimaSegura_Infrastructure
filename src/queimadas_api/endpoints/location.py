from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()


@router.get('', status_code=status.HTTP_202_ACCEPTED)
def get_location(search: str):
    from api.location import handle_location_response
    return handle_location_response(search)

@router.get('/zip_code', status_code=status.HTTP_202_ACCEPTED)
def get_zip_code_lat_lng(lat: float, lng: float):
    from api.location import get_zip_code_by_lat_lng_response
    return get_zip_code_by_lat_lng_response(lat, lng)