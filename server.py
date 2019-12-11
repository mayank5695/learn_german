from flask import Flask, request, jsonify
from flask.helpers import send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.serving import run_simple

from model import User,Assignment,get_all_assignments

# import routes

app = Flask(__name__)

CORS(app, supports_credentials=True)
login_manager = LoginManager()
login_manager.init_app(app)
SECRET_KEY = b'\x06c\xcf\xa3\x07su\xdc8tn\xdc\x1b\xf4\xdd\x1a\xd2\xd7\xd8\xe0\xec\xc9\xfc1'

app.secret_key = SECRET_KEY

@app.before_request
def log_request():
    pass


@login_manager.user_loader
def user_loader(session_token):
    return User.get_user_from_session_token(session_token)


@app.route('/user/login', methods=['POST'])
def login():
    email = request.values.get('email')
    password = request.values.get('password')
    user = User.objects(email=email).first()
    if user:
        if check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            response = jsonify({
                'success': True,
                'user': {
                    'session_token': user.session_token,
                    'role': user.role,
                    'level': user.level
                }
            })
            response.status_code = 200
        else:
            response = jsonify({
                'success': False,
                'errorMessage': 'Incorrect password. Please try again.'
            })
    else:
        response = jsonify({
            'success': False,
            'errorMessage': 'Email not found. Please try again.'
        })
    return response


@app.route('/user/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    response = jsonify({
        'success': True
    })
    response.status_code = 200
    return response

@app.route('/user/assignments',methods=["GET"])
def get_assignments():

    response=get_all_assignments()
    return response

@app.route('/user/create_assignment',methods=["POST"])
def create_assignment():
    header=request.values.get('header')
    tag=request.values.get('tag')
    day=request.values.get('day')

    if not header and not tag and not day:
        return jsonify({
            'success':False,
            'errorMessage':'Missing Params.'
        })
    assign=Assignment.create(header,tag,day)

    if assign:
        return jsonify({
            'success':True,
            'Message':'Assignment created.'
        })




@app.route('/',methods=["POST","GET"])
def main():

    return "Hello World"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)