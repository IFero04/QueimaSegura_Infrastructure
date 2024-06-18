import re

def check_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not(re.match(email_pattern, email)):
        raise Exception('Invalid email')

def check_password(password):
    if len(password) != 32:
        raise Exception('Password must be a MD5 hash')

def check_full_name(full_name):
    if len(full_name) < 3:
        raise Exception('Full name must have at least 3 characters')
    if not full_name.replace(" ", "").isalpha():
        raise Exception('Full name must have only letters')

def check_nif(nif):
    if len(nif) != 9:
        raise Exception('NIF must have 9 digits')
    if not nif.isdigit():
        raise Exception('NIF must have only digits')
    if nif[0] in ('4','7'):
        raise Exception('Invalid NIF')
    
def check_type(type):
    if type not in (0, 1, 2):
        raise Exception('Invalid type')
