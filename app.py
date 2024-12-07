import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from routes.auth import auth
from utils.socket import emit_initial_update


class Config:
    JWT_SECRET_KEY = 'test-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"], "supports_credentials": True}})

    socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173", manage_session=False, cors_credentials=True)

    app.register_blueprint(auth, url_prefix='/auth')
    emit_initial_update(socketio)

    return app, socketio


# Create the application
server_app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(server_app, host='localhost', port=3434, debug=True, allow_unsafe_werkzeug=True)
