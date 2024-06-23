import re
import requests
from nltk.corpus import stopwords
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings


NUMBER_RESULTS = 100
STOP_WORDS = set(stopwords.words('portuguese'))

## QUERY
def __build_query(rows: list, number_results: int):
    base_query = f"""
            SELECT *
            FROM zip_codes
    """
    if rows:
        where_strings = []
        for row in rows:
            if row['isNumber']:
                where_strings.append(f""" {row['row']} = %s """)
            elif row['isPerfect']:
                where_strings.append(f""" {row['row']} = %s """)
            else:
                where_strings.append(f""" {row['row']} ILIKE %s """)
        where_string = " AND ".join(where_strings)

        where_query = f""" {base_query} WHERE {where_string} """
    else:
        where_query = f""" {base_query} """
            
    if number_results > 0:
        return f""" {where_query} LIMIT {number_results}; """
    
    return f""" {where_query}""";

## IDENTIFICATION
def __remove_numbers(text):
    return re.sub(r'\d+', '', text)

def __group_by_stopwords(tokens: list):
    groups = []
    i = 0
    while i < len(tokens):
        if tokens[i].lower() in STOP_WORDS:
            start = max(i - 1, 0)
            end = min(i + 2, len(tokens))
            group = ' '.join(tokens[start:end])
            if group:
                groups.append(group)
            i = end 
        else:
            i += 1

    i = 0
    while i < len(groups) - 1:
        if groups[i].split()[-1] == groups[i + 1].split()[0]:
            groups[i] = ' '.join([groups[i], groups[i + 1].split(' ', 1)[1]])
            del groups[i + 1]
        else:
            i += 1

    used_words = set(word for group in groups for word in group.split())
    unused_words = [word for word in tokens if word not in used_words]

    return groups + unused_words   

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

def __only_numbers(search_string: str):
    return search_string.isdigit()

def __only_numbers_with_hifen(search_string: str):
    tokens = search_string.split('-')
    return all(token.isdigit() for token in tokens if token != '')

def __find_zip_code(search_string: str):
    zip_code_pattern = re.compile(r'\b\d{4}-\d{3}\b')
    zip_code_match = zip_code_pattern.search(search_string)
    if zip_code_match:
        return zip_code_match.group()
    return None


    return groups

def __find_location_name(search_string: str):
    str_no_numbers = __remove_numbers(search_string)
    str_no_numbers = str_no_numbers.replace(',', '')
    tokens = str_no_numbers.split()
    group_tokens = __group_by_stopwords(tokens)
    probably_locations = []
    for token in group_tokens:
        result = __fetch_data((f'%{token}%', ), [{
            'row': 'location_name',
            'isNumber': False,
            'isPerfect': False
        }], 1)
        if result:
            probably_locations.append(result['location_name'])
    return probably_locations

## FETCH DATA
def __fetch_data(parameters: set, rows: list, number_results: int):
    multi = number_results != 1

    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = __build_query(rows, number_results)

        result = db.execute_query(query, parameters, multi=multi)
        if result:
            if multi:
                return [{
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
                } for r in result]
            return {
                'id': result[0],
                'location_code': result[1],
                'location_name': result[2],
                'ART_code': result[3],
                'ART_name': result[4],
                'tronco': result[5],
                'client': result[6],
                'zip_code': result[7],
                'zip_name': result[8],
                'county_id': result[9]
            }
        return []

## ITERATIONS
def __match_zip_code(search_string: str, zip_code: str):
    search_string = search_string.replace(zip_code, "")
    locations = []
    hasZipCode = False
    result = __fetch_data((zip_code, ), [{
        'row': 'zip_code',
        'isNumber': False,
        'isPerfect': True
    }], 1)
    if result:
        hasZipCode = True
        location_name = result['location_name']
        if location_name in search_string:
            search_string = search_string.replace(location_name, "")

    groups_of_words = [word.strip() for word in search_string.split(',') if word.strip()]
    if groups_of_words:
        for group in groups_of_words:
            if not hasZipCode:
                paramsters = (f'%{group}%', )
                locations.extend(__fetch_data(paramsters, [
                    {
                        'row': 'art_name',
                        'isNumber': False,
                        'isPerfect': False
                    }
                ], NUMBER_RESULTS))
            else:
                paramsters = (zip_code, f'%{group}%', )
                locations.extend(__fetch_data(paramsters, [
                    {
                        'row': 'zip_code',
                        'isNumber': False,
                        'isPerfect': True
                    },
                    {
                        'row': 'art_name',
                        'isNumber': False,
                        'isPerfect': False
                    }
                ], 0))
    if locations:
        return locations
    elif hasZipCode:
        return __fetch_data((zip_code, ), [{
            'row': 'zip_code',
            'isNumber': False,
            'isPerfect': True
        }], 0)
    return []

def __match_search_string(search_string: str):
    perfect_match = __fetch_data((search_string, ), [{
        'row': 'art_name',
        'isNumber': False,
        'isPerfect': True
    }], 0)
    if perfect_match:
        return perfect_match
    perfect_match = __fetch_data((search_string, ), [{
        'row': 'location_name',
        'isNumber': False,
        'isPerfect': True
    }], 0)
    if perfect_match:
        return perfect_match

    location_name = ''
    numbers = [int(s) for s in search_string.split() if s.isdigit()]
    if numbers:
        for number in numbers:
            temp = __fetch_data((f'%{number}%', ), [{
                'row': 'zip_code',
                'isNumber': False,
                'isPerfect': False
            }], 1)
            if temp:
                search_string = search_string.replace(str(number), "")
                location_name = temp['location_name']
                if location_name in search_string:
                    search_string = search_string.replace(location_name, "")
    
    locations = []
    if location_name:
        groups_of_words = [word.strip() for word in search_string.split(',') if word.strip()]
        if groups_of_words:
            for group in groups_of_words:
                parameters = (f'%{group}%', location_name, )
                locations.extend(__fetch_data(parameters, [
                    {
                        'row': 'art_name',
                        'isNumber': False,
                        'isPerfect': False
                    },
                    {
                        'row': 'location_name',
                        'isNumber': False,
                        'isPerfect': True
                    }
                ], NUMBER_RESULTS))
        else:
            print(f"Location Name: {location_name}")
            return __fetch_data((location_name, ), [{
                'row': 'location_name',
                'isNumber': False,
                'isPerfect': True
            }], 0)
    else:
        probably_locations = __find_location_name(search_string)
        if probably_locations:
            print(f"Probably Locations: {probably_locations}")
            for location_name in probably_locations:
                if location_name in search_string:
                    new_search_string_group = search_string.split(location_name)
                    new_search_string = ",".join(new_search_string_group)
                    groups_of_words = [word.strip() for word in new_search_string.split(',') if word.strip()]
                    if groups_of_words:
                        for group in groups_of_words:
                            parameters = (f'%{group}%', location_name, )
                            locations.extend(__fetch_data(parameters, [
                                {
                                    'row': 'art_name',
                                    'isNumber': False,
                                    'isPerfect': False
                                },
                                {
                                    'row': 'location_name',
                                    'isNumber': False,
                                    'isPerfect': True
                                }
                            ], NUMBER_RESULTS))
    if not locations:
        str_no_numbers = __remove_numbers(search_string)
        groups_of_words = [word.strip() for word in str_no_numbers.split(',') if word.strip()]
        new_group = __group_by_stopwords(' '.join(groups_of_words).split())
        if new_group:
            for group in new_group:
                parameters = (f'%{group}%', )
                locations.extend(__fetch_data(parameters, [
                    {
                        'row': 'art_name',
                        'isNumber': False,
                        'isPerfect': False
                    }
                ], NUMBER_RESULTS))

    return locations

## LOCATION
def get_location_by_probability(search: str):
    locations = []
    search_probabilities = __calculate_probabilities(search)
    order = [key for key in sorted(search_probabilities, key=search_probabilities.get, reverse=True) if search_probabilities[key] > 0.0]

    for i in range(len(order)):
        number_fetch = int(NUMBER_RESULTS * search_probabilities[order[i]])
        locations.extend(__fetch_data((f'%{search}%', ), [{
            'row': order[i],
            'isNumber': False,
            'isPerfect': False
        }], number_fetch))
    
    return locations

def get_location(search: str):
    locations = []
    search_string = search.strip()
    zip_code = __find_zip_code(search_string)
    if zip_code:
        locations = __match_zip_code(search_string, zip_code)
    elif (__only_numbers(search_string) or __only_numbers_with_hifen(search_string)):
        parameters = (f'%{search_string}%', )
        locations = __fetch_data(parameters, [{
            'row': 'zip_code',
            'isNumber': False,
            'isPerfect': False
        }], NUMBER_RESULTS)
    else:
        locations = __match_search_string(search_string)

    if locations:
        return locations

def handle_location_response(search: str):
    search_string = search.strip()
    locations = get_location(search_string)
    if locations:
        return {
            'status': 'OK!',
            'message': 'Location retrived successfully!',
            'result': locations
        }
    locations = get_location_by_probability(search_string)
    if locations:
        return {
            'status': 'OK!',
            'message': 'Location retrived successfully!',
            'result': locations
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')

def get_zip_code_by_lat_lng_response(lat, lng):
    url = f'https://geocode.maps.co/reverse?lat={lat}&lon={lng}&api_key={settings.geo_api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        address = response.json()['address']

        postcode = address.get('postcode')
        county = address.get('county')
        road = address.get('road')
        village = address.get('village')

        print(f"Postcode: {postcode}")
        print(f"County: {county}")
        print(f"Road: {road}")
        print(f"Village: {village}")
    except Exception as _:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Map is unavailable at the moment. Please try again later.")