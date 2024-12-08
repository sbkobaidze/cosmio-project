import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, 
from pydantic import ValidationError
from utils.db import create_user, get_user, update_user
from utils.schemas import APIResponse, UserLogin, UserRegister
from utils.socket import get_socketio
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth_blueprint', __name__)


@auth.route('/login', methods=['POST'], endpoint='func1')
def login():
    try:
        user_data = UserLogin(**request.get_json())
        user = get_user(user_data.email, True)

        if not user or not check_password_hash(user['password'], user_data.password):
            error_response = APIResponse(success=False, message="Invalid credentials", errors=[{"message": "Invalid email or password"}])
            return jsonify(error_response.dict()), 401

        access_token = create_access_token(identity=user['email'])
        refresh_token = create_refresh_token(identity=user['email'])

        response = jsonify(APIResponse(success=True, message="Login successful").dict())
        (
            socketio,
            emit_global,
        ) = get_socketio()

        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        update_user(user['email'], user['sign_in_dates'] + [datetime.datetime.now().isoformat()], user['sign_in_count'] + 1)

        emit_global()

        return response, 200

    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.errors()}), 400


@auth.route('/register', methods=['POST'], endpoint='func2')
def register():
    try:
        user_data = UserRegister(**request.get_json())
        check_user = get_user(user_data.email)

        if check_user:
            error_response = APIResponse(success=False, message="User with same email already exists", errors=[{"message": "User already exists"}])
            return jsonify(error_response.dict()), 400

        password_hash = generate_password_hash(user_data.password, method='pbkdf2:sha256')
        create_user({'email': user_data.email, 'password': password_hash})

        response = jsonify(APIResponse(success=True, message="Registration successful").dict())

        return response, 201

    except ValidationError as e:
        error_response = APIResponse(success=False, message="Validation error", errors=[{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()])
        return jsonify(error_response.dict()), 400

    except Exception as e:
        print(e)
        error_response = APIResponse(success=False, message="Unexpected error occurred", errors=[{"message": str(e)}])
        return jsonify(error_response.dict()), 500


@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    response = jsonify({'msg': 'Token refreshed successfully'})
    set_access_cookies(response, access_token)
    return response, 200


@auth.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'Logout successful'})
    unset_jwt_cookies(response)
    return response, 200


@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    print('test')
    current_user = get_jwt_identity()
    print(current_user, 'test123')
    return jsonify(APIResponse(success=True, message="User authenticated successfully", data={"email": current_user}).dict()), 200
