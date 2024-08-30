import os
import requests

from django.core.cache import cache


def get_new_access_token_from_api():
    url = 'https://api.gsv-gundernhausen.de/v1.0/auth'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "username": os.environ.get('MEMBER_API_USER'),
        "refresh_token": os.environ.get('MEMBER_API_REFRESH_TOKEN')
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return None
    token = response.json().get("access_token")
    cache.set('access_token', token, timeout=3600 * 24)
    return token


def get_access_token(force_new_access_token):
    if not force_new_access_token:
        token = cache.get('access_token')

        if token is None:
            token = get_new_access_token_from_api()
    else:
        return get_new_access_token_from_api()

    return token


def get_user_info(user_id, force_new_access_token: bool = False):
    url = 'https://api.gsv-gundernhausen.de/v1.0/terminal/member'
    access_token = get_access_token(force_new_access_token)
    if access_token is None:
        access_token = get_access_token(True)
        if access_token is None:
            return "not authorized", None, None, None, None, None
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    data = {
        'uid': user_id
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        if not force_new_access_token:
            return get_user_info(user_id, True)
        return None, None, None, None, None, None
    else:
        email = response.json().get('email')
        gender = response.json().get('gender')
        street = response.json().get('strasse')
        plz = response.json().get('plz')
        city = response.json().get('stadt')
        name = response.json().get('mitglied')
        return name, email, gender, street, plz, city
