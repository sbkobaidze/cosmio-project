from datetime import datetime

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_socketio import disconnect, join_room, leave_room
from utils.db import get_all_users, get_user
from utils.schemas import IncomingFilterMessage


def get_socketio():
    socketio = current_app.extensions['socketio']

    def emit_global_update(email: str):
        users = get_all_users()
        socketio.emit(
            'increment_global',
            {'email': email, 'date': datetime.now().isoformat()},
        )

        if users['total_sign_ins'] % 5 == 0:

            socketio.emit(
                'notification',
                {'message': f"Milestone reached: {users['total_sign_ins']} total sign-ins!"},
            )

    return (
        socketio,
        emit_global_update,
    )


def emit_initial_update(socketio):

    @socketio.on("update_filters")
    def handle_update_filters(data: IncomingFilterMessage):
        type = data['type']
        from_date = data.get('from')
        to_date = data.get('to')
        count = data['pageSize']
        page = data.get('pageIndex', 0)

        if type == 'personal':
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            user = get_user(current_user, False, count, from_date, to_date, page)
            socketio.emit(
                'personal_update',
                {
                    'dates': user['sign_ins'],
                },
            )
        elif type == 'global':
            print('page:', page)
            users = get_all_users(count, from_date, to_date, page)
            socketio.emit(
                'global_update',
                {**users},
            )

    @socketio.on('connect')
    def handle_connect():
        try:
            sid = request.sid

            socketio.sleep(0.5)
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            users = get_all_users()
            user = get_user(current_user)
            dates = user['sign_ins']

            print(f'New connection with SID: {sid}')

            join_room(request.sid)

            socketio.emit(
                'users',
                {
                    'personal': {
                        'dates': dates,
                        'total_sign_ins': user['user']['sign_in_count'],
                    },
                    'global': users,
                },
                room=request.sid,
            )
            return True

        except Exception as e:
            print(f'Failed to emit initial data: {str(e)}')
            return False
