from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import const
from model import User

teacher_routes= Blueprint('root',__name__)

@teacher_routes.route('/user/all',methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'errorMessage': 'You must be logged in as root to view all users'
        })
    users = []
    for user in User.objects(email__ne=current_user.email):  # we do not want to return the calling user
        users.append(user.dictify())
    return jsonify({
        'success': True,
        'users': users
    })

@teacher_routes.route('/user/create', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'errorMessage': "You must be logged in as root to create new users"
        })

    email = request.values.get("email")
    password = request.values.get("password")
    role = request.values.get("role")
    level = request.values.get("level")

    if User.objects(email=email).first() is not None:
        return jsonify({
            'success': False,
            'errorMessage': 'This email is already registered'
        })
    if role not in const.User.roles:
        return jsonify({
            'success': False,
            'errorMessage': 'Invalid value for role: ' + role
        })
    if level not in const.User.levels:
        return jsonify({
            'success': False,
            'errorMessage': 'Invalid value for level: ' + level
        })
    User.create(email=email, password=password, role=role, level=level)
    response = jsonify({
        'success': True,
        'message': "New user created: " + email
    })
    response.status_code = 200
    return response
