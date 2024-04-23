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

@app.route('/api/users/logout/<id>/<session_id>', methods=['DELETE'])
def logout():
    from api.users import logout
    args = request.args
    return logout(args)

     
def main():
    from api.users import new_user, login, logout

    try:
        data = {
            'user': {
                'full_name': 'Teste',
                'email': 'af1213@gmail.com',
                'password': 'e10adc3949ba59abbe56e057f20f883e',
                'NIF': '123456789',
            }
        }
        #new_user(data)
        data1 = {
            'args': {
                'id': 'f98418b2-bbf7-40f2-bd1e-a57c2bd8ad7e',
                'session_id': '8870262d-9ad9-482f-9166-a1a19f33d42c',
            }
        }
        result = logout()
        print(result)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    print("Loading DataBase ...")
    while not check_db(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD):
        print("Retrying in 30 seconds ...")
        time.sleep(30)

    print("DataBase loaded.")
    main()
    #app.run(host="0.0.0.0", port=API_PORT)
