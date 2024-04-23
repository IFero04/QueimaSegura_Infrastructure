import time
from flask import Flask, request
from flask_cors import CORS
from util.db import check_db
from const import API_PORT, PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/users/register', methods=['POST'])
def new_user():
    from api.users import new_user
    data = request.get_json() 
    return new_user(data)

@app.route('/api/users/login', methods=['POST'])
def login():
    from api.users import login
    data = request.get_json()
    return login(data)

@app.route('/api/users/logout/<user_id>/<session_id>', methods=['DELETE'])
def logout():
    from api.users import logout
    args = request.args
    return logout(args)

@app.route('/api/users/update', methods=['PATCH'])
def update_user():
    from api.users import update_user
    data = request.get_json()
    return update_user(data)
     

def main():
    from api.users import new_user, login, logout, update_user

    try:
        data = {
            'user': {
                #'id': '0dbf7879-1704-42f8-aec8-2e945a64f601',
                #'session_id': 'f856d66d-826d-44ba-bf8a-ba972e379bc0',
                #'full_name': 'Teste',
                'email': 'af12@gmail.com',
                'password': 'e10adc3949ba59abbe56e057f20f883e',
                #'NIF': '223456789',
            }
        }
        result = login(data)
        print(result)
    except Exception as e:
        print('Error: ', e)

if __name__ == '__main__':
    print("Loading DataBase ...")
    while not check_db(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD):
        print("Retrying in 15 seconds ...")
        time.sleep(15)

    print("DataBase loaded.")
    main()
    #app.run(host="0.0.0.0", port=API_PORT)
