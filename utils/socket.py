from flask import Blueprint, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from utils.db import get_all_users, get_user


def get_socketio():
    socketio = current_app.extensions['socketio']

    def emit_global_update():
        users = get_all_users()
        users = [{**user, 'sign_in_count': float(user['sign_in_count'])} for user in users]
        total_sign_ins = sum(user['sign_in_count'] for user in users)

        socketio.emit(
            'global_update',
            {'users': users},
        )
        if total_sign_ins % 5 == 0:
            socketio.emit(
                'notification',
                {
                    'message': f'Milestone reached: {total_sign_ins} total sign-ins!',
                },
            )

    return (
        socketio,
        emit_global_update,
    )


def emit_initial_update(socketio):
    @socketio.on('connect')
    def handle_connect():
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            users = get_all_users()
            personal = get_user(current_user)

            personal = {**personal, 'sign_in_count': float(personal['sign_in_count'])}
            users = [{**user, 'sign_in_count': float(user['sign_in_count'])} for user in users]
            socketio.emit('users', {'global': users, 'personal': personal})
            return True
        except Exception as e:
            print('Failed to emit initial data:', str(e))
            return False
