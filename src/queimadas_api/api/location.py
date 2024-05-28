import uuid
import re
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings


## IDENTIFICATION
def __calculate_probabilities(search_string: str):
        search_string = search_string.lower()
        tokens_by_space = search_string.split()
        tokens = []
        for token in tokens_by_space:
            tokens.extend(token.split('-'))
        zip_code_pattern = re.compile(r'^\d{4}-\d{3}$')
        look_for_words = ["rua", "avenida", "praça", "praca", "travessa", "largo", "urbanização", "urbanizacão", "urbanizacao"]
        
        probabilities = {"zip_code": 0.0, "location_name": 0.0, "ART_name": 0.0}
        
        # Perfect ZIP Code Match
        if zip_code_pattern.match(search_string):
            probabilities["zip_code"] = 1.0
            return probabilities

        # Look for Specific Words
        if any(word in look_for_words for word in tokens):
            probabilities["ART_name"] = 0.8
            probabilities["location_name"] = 0.2
            return probabilities
        
        # Only Numbers
        if search_string.isdigit():
            if len(search_string) <=4:
                probabilities["zip_code"] = 0.9
                probabilities["ART_name"] = 0.1
                return probabilities
            else:
                probabilities["ART_name"] = 0.7
                probabilities["location_name"] = 0.3
                return probabilities
        
        if all(token.isdigit() for token in tokens):
            if len(tokens) == 2:
                if len(tokens[0]) == 4 and len(tokens[1]) <= 3:
                    probabilities["zip_code"] = 0.8
                    probabilities["ART_name"] = 0.2
                    return probabilities
                
            probabilities["ART_name"] = 0.7
            probabilities["location_name"] = 0.3
            return probabilities
        
        if any(char.isdigit() for char in search_string) and any(char.isalpha() for char in search_string):
            probabilities["ART_name"] = 0.7
            probabilities["location_name"] = 0.3
            return probabilities
        
        if len(tokens) == 1: 
            probabilities["location_name"] = 0.7
            probabilities["ART_name"] = 0.3
            return probabilities
        elif len(tokens) <= 3:
            probabilities["location_name"] = 0.6
            probabilities["ART_name"] = 0.4
            return probabilities
        
        probabilities["ART_name"] = 0.8
        probabilities["location_name"] = 0.2
        return probabilities

## ITERATIONS



## ZIPCODE
def get_location(search: str):
    number_results = 50
    search_probabilities = __calculate_probabilities(search)
    order = [key for key in sorted(search_probabilities, key=search_probabilities.get, reverse=True) if search_probabilities[key] > 0.0]
    for i in range(len(order)):
        print(f"Searching by {order[i]}: {search_probabilities[order[i]]}")

    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, location_code, location_name, ART_code, ART_name, tronco, client, zip_code, zip_name, county_id
                FROM zip_codes
                WHERE zip_code LIKE %s;
            """
            parameters = (search, )
            result = db.execute_query(query, parameters, multi=True)
            if not result:
                raise HTTPException(status_code=404, detail='Location not found')
            result_json = []
            for r in result:
                id, location_code, location_name, ART_code, ART_name, tronco, client, zip_code, zip_name, county_id = r
                result_json.append({
                    'id': id,
                    'location_code': location_code,
                    'location_name': location_name,
                    'ART_code': ART_code,
                    'ART_name': ART_name,
                    'tronco': tronco,
                    'client': client,
                    'zip_code': zip_code,
                    'zip_name': zip_name,
                    'county_id': county_id
                })
                
            return {
                    'status': 'OK!',
                    'message': 'User created successfully!',
                    'result': result_json
                }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))