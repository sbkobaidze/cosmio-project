import datetime
from typing import Optional, TypedDict

from boto3 import resource

users_table = resource('dynamodb').Table('users')


class User(TypedDict):
    email: str
    password: str
    created_at: str


def create_user(user: User):
    try:
        user['sign_in_dates'] = [datetime.datetime.now().isoformat()]
        user['sign_in_count'] = 0
        respone = users_table.put_item(Item=user)
        print(respone)
    except Exception as e:
        print(e)
        raise e


def get_user(email: str, showPassword: Optional[bool] = False):
    try:
        projection = 'email, sign_in_dates, sign_in_count, #r' + (', password' if showPassword else '')

        response = users_table.get_item(Key={'email': email}, ProjectionExpression=projection, ExpressionAttributeNames={'#r': 'role'})

        return response.get('Item')
    except Exception as e:
        print(e)
        raise e


def update_user(email: str, sign_in_dates: list[str], sign_in_count: int):
    try:
        response = users_table.update_item(Key={'email': email}, UpdateExpression='SET sign_in_dates = :dates, sign_in_count = :count', ExpressionAttributeValues={':dates': sign_in_dates, ':count': sign_in_count})
        print(response)
    except Exception as e:
        print(e)
        raise e


def get_all_users():
    try:
        response = users_table.scan(ProjectionExpression='email, sign_in_dates, sign_in_count, #r', FilterExpression='sign_in_count > :count', ExpressionAttributeNames={'#r': 'role'}, ExpressionAttributeValues={':count': 0})
        return response.get('Items', [])
    except Exception as e:
        print(e)
        raise e
