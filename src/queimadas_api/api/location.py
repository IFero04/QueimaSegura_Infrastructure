import uuid
import re
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings

## QUERY
def __build_query(row: str, number_results: int, limit: bool = True, isNumber: bool = False, perfect: bool = True):
    base_query = f"""
            SELECT *
            FROM zip_codes
    """
    if isNumber:
        where_query = f""" {base_query} WHERE {row} = %s """
    else:
        if perfect:
            where_query = f""" {base_query} WHERE {row} LIKE %s """
        else:
            where_query = f""" {base_query} WHERE {row} ILIKE %s """
    
    if limit:
        return f""" {where_query} LIMIT {number_results}; """
    
    return f""" {where_query}; """

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

## FETCH DATA
def __search_data(search_string: str,row:str, number_results: int, limit: bool = True, isNumber: bool = False, multi: bool = True):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = __build_query(row, number_results, limit, isNumber, perfect=False)

        parameters = (f"%{search_string}%", )
        result = db.execute_query(query, parameters, multi=True)
        result_json = []
        for r in result:
            result_json.append({
                'id': r[0],
                'location_code': r[1],
                'location_name': r[2],
                'ART_code': r[3],
                'ART_name': r[4],
                'tronco': r[5],
                'client': r[6],
                'zip_code': r[7],
                'zip_name': r[8],
                'county_id': r[9]
            })
        if result_json and not multi:
            return result_json[0]
        return result_json

def __fetch_data(search_string: str, row: str, number_results: int, limit: bool = True, isNumber: bool = False, multi: bool = True):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = __build_query(row, number_results, limit, isNumber, perfect=False)

        parameters = (search_string, )
        result = db.execute_query(query, parameters, multi=True)
        result_json = []
        for r in result:
            result_json.append({
                'id': r[0],
                'location_code': r[1],
                'location_name': r[2],
                'ART_code': r[3],
                'ART_name': r[4],
                'tronco': r[5],
                'client': r[6],
                'zip_code': r[7],
                'zip_name': r[8],
                'county_id': r[9]
            })
        if result_json and not multi:
            return result_json[0]
        return result_json

## ITERATIONS
def __find_location_name(tokens: list):
    for token in tokens:
        result = __fetch_data(token, 'location_name', 1, multi=False)
        if result:
            return token, result['location_code']
    return None, None

def __find_perfect_match(search_string: str, tokens: list, data: list):
    keys = ['zip_code', 'location_name']
    for token in tokens:
        for item in data:
            for key in keys:
                if search_string.lower() in item[key].lower():
                    return key, token
    return None


## LOCATION
def get_location(search: str):
    tokens = re.split(r'[ ,\-]+', search)
    locations = []
    number_results = 100
    perfect_match_key = None

    location_name, location_code = __find_location_name(tokens)
    if location_name:
        tokens.remove(location_name)
    
    if location_code and len(tokens) == 0:
        locations = __fetch_data(location_code, 'location_code', number_results, limit=False, isNumber=True)
        if locations:
            return {
                'status': 'OK!',
                'message': 'Location retrived successfully!',
                'result': locations
            }

    search_probabilities = __calculate_probabilities(search)
    order = [key for key in sorted(search_probabilities, key=search_probabilities.get, reverse=True) if search_probabilities[key] > 0.0]
    
    if search_probabilities['zip_code'] == 1:
        locations = __fetch_data(search, 'zip_code', number_results, limit=False)
        if locations:
            return {
                'status': 'OK!',
                'message': 'Location retrived successfully!',
                'result': locations
            }

    for i in range(len(order)):
        print(f"Searching by {order[i]}: {search_probabilities[order[i]]}")
        number_fetch = int(number_results * search_probabilities[order[i]])
        try:
            result = __fetch_data(search, order[i], number_fetch)
            if result:
                perfect_match_key = __find_perfect_match(search, tokens, result)
                if perfect_match_key:
                    break;
                locations.extend(result)
                
        except Exception as e:
            continue
    
    if perfect_match_key:
        print(f"Perfect Match: {perfect_match_key}")
        locations = __fetch_data(search, perfect_match_key, 0, limit=False)

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