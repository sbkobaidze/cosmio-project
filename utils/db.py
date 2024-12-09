import datetime
from typing import Optional, TypedDict

from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key

users_table = resource('dynamodb').Table('users')
sign_ins_table = resource('dynamodb').Table('sign_ins')


class User(TypedDict):
    email: str
    password: str
    created_at: str


def create_user(user: User):
    try:
        user['sign_in_count'] = 0
        respone = users_table.put_item(Item=user)
        print(respone)
    except Exception as e:
        print(e)
        raise e


def get_user(email: str, showPassword: Optional[bool] = False, count: int = 2, from_date: Optional[str] = None, to_date: Optional[str] = None, page: int = 0):
    try:
        projection = 'email, sign_in_count' + (', password' if showPassword else '')
        response = users_table.get_item(
            Key={'email': email},
            ProjectionExpression=projection,
        )

        user = response.get('Item', {})
        if not user:
            return None

        user_data = {**user, 'sign_in_count': float(user['sign_in_count'])}

        if not showPassword:
            sign_ins = get_user_logins(email, count, from_date, to_date, page)
            return {'user': user_data, 'sign_ins': sign_ins}

        return user_data

    except Exception as e:
        print(e)
        raise e


def get_user_logins(email: Optional[str] = None, count: int = 2, from_date: Optional[str] = None, to_date: Optional[str] = None, page: int = 0):
    base_params = {'Limit': count}

    if email:
        query_params = {
            **base_params,
            'ScanIndexForward': False,
            'ProjectionExpression': '#d',
            'ExpressionAttributeNames': {'#d': 'date'},
        }

        key_condition = Key('email').eq(email)
        if from_date or to_date:
            if from_date and to_date:
                key_condition = key_condition & Key('date').between(from_date, to_date)
            elif from_date:
                key_condition = key_condition & Key('date').gte(from_date)
            elif to_date:
                key_condition = key_condition & Key('date').lte(to_date)

        query_params['KeyConditionExpression'] = key_condition

        if page > 0:
            for _ in range(page):
                response = sign_ins_table.query(**query_params)
                last_key = response.get('LastEvaluatedKey')
                if not last_key:
                    break
                query_params['ExclusiveStartKey'] = last_key

        return sign_ins_table.query(**query_params).get('Items', [])

    scan_params = base_params.copy()
    if from_date or to_date:
        filter_conditions = []
        expression_values = {}

        if from_date:
            filter_conditions.append('#date >= :from_date')
            expression_values[':from_date'] = from_date
        if to_date:
            filter_conditions.append('#date <= :to_date')
            expression_values[':to_date'] = to_date

        scan_params.update({'FilterExpression': ' AND '.join(filter_conditions), 'ExpressionAttributeNames': {'#date': 'date'}, 'ExpressionAttributeValues': expression_values})

    if page > 0:
        for _ in range(page):
            response = sign_ins_table.scan(**scan_params)
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            scan_params['ExclusiveStartKey'] = last_key

    return sign_ins_table.scan(**scan_params).get('Items', [])


def update_user(email: str, sign_in_count: int):
    try:
        print("issue here?")
        response = users_table.update_item(Key={'email': email}, UpdateExpression='SET sign_in_count = :count', ExpressionAttributeValues={':count': int(sign_in_count)})
        res = sign_ins_table.put_item(Item={'email': email, 'date': datetime.datetime.now().isoformat()})
    except Exception as e:
        print(e)
        raise e


def get_all_users(count: int = 2, from_date: Optional[str] = None, to_date: Optional[str] = None, page: int = 0):
    try:
        response = users_table.scan(ProjectionExpression='sign_in_count', FilterExpression='sign_in_count > :count', ExpressionAttributeValues={':count': 0})
        users = response.get('Items', [])
        total_sign_ins = sum(float(user['sign_in_count']) for user in users)

        sign_ins = get_user_logins(None, count, from_date, to_date, page)

        return {
            'total_sign_ins': total_sign_ins,
            'dates': sign_ins,
        }
    except Exception as e:
        print(e)
        raise e
