import requests

api_key = '6678996f5c699277549377exz48811d'
def get_zip_code_by_lat_lng_response(lat, lng):
    url = f'https://geocode.maps.co/reverse?lat={lat}&lon={lng}&api_key={api_key}'
    try:
        response = requests.get(url)
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        zip_code = response.text
        
        return zip_code
    except requests.RequestException as e:
        print(f"Error fetching ZIP code: {e}")
        return None

lat = 41.4581409
lng = -8.5464625
zip_code = get_zip_code_by_lat_lng_response(lat, lng)
print(f"The ZIP code for latitude {lat} and longitude {lng} is: {zip_code}")