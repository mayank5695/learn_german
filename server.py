from flask import Flask, request, jsonify
from flask.helpers import send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.serving import run_simple

from model import User,Assignment,get_all_assignments,Post,get_all_posts


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

@login_required
@app.route('/user/assignments',methods=["GET"])
def get_assignments():

    response=get_all_assignments()
    return response

@login_required
@app.route('/user/submit',methods=["POST"])
def submit_assignments():
    text = request.values.get('text')
    assignment_id = request.values.get('assignment_id')
    if not text and not assignment_id:
        return jsonify({
            'success': False,
            'errorMessage': 'Missing Params.'
        })

    response=Post.submit_assigment(text,assignment_id)
    if response:
        return jsonify({
            'success': True,
            'Message': 'Submission done.'
        })


@login_required
@app.route('/user/get_post',methods=["GET"])
def get_posts():
    assignment_id=request.values.get('assignment_id')
    if not assignment_id:
        return jsonify({
            'success': False,
            'errorMessage': 'Missing Params.'
        })
    response=get_all_posts(assignment_id)
    if response:
        return response
    else:
        return jsonify({
            'success': True,
            'Message': 'No response.'
        })

@login_required
@app.route('/user/add_comment',methods=["POST"])
def comments():
    post_id=request.values.get('submission_id')
    comment=request.values.get('comment')

    if not post_id or not comment:
        return jsonify({
            'success': False,
            'errorMessage': 'Missing Params.'
        })

    post=Post.add_comments(post_id,comment)
    if post:
        return jsonify({
            'success': True,
            'Message': 'Comment added.'
        })


@login_required
@app.route('/user/reaction',methods=["GET"])
def get_reactions():
    post_id=request.values.get('post_id')
    hilarious=request.values.get('hilarious')
    well=request.values.get('well_written')
    amazing=request.values.get('amazing_story')

    if not post_id or (not hilarious or not well or not amazing):
        return jsonify({
            'success': False,
            'errorMessage': 'Missing Params.'
        })

    val=""
    if hilarious:
        val=Post.add_reaction(post_id=post_id,hilarious=hilarious)
    if well:
        val = Post.add_reaction(post_id=post_id,well_written=well)
    if amazing:
        val=Post.add_reaction(post_id=post_id,amazing=amazing)

    if val:
        return jsonify({
            'success': True,
            'Message': 'Reaction added.'
        })





@login_required
@app.route('/user/create_assignment',methods=["POST"])
def create_assignment():
    header=request.values.get('header')
    tag=request.values.get('keywords')
    day=request.values.get('day')

    if not current_user.is_admin():
        return jsonify({
            'success':False,
            'errorMessage':'User is not authorized to create assignment.'
        })

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


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)