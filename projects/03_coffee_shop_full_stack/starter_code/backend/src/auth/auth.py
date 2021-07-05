import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

import inspect

AUTH0_DOMAIN = "gzs-fsnd.eu.auth0.com"
ALGORITHMS = ['RS256']
API_AUDIENCE = "coffeeshop"

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    # print("auth: ", auth)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    # print(len(parts))
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    # print('alles gut mit get token')
    return token


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        print('Error: no permissions found in JWT')
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        print('Error: Permission not found')
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Specific permission not found.'
        }, 403)
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    # print(unverified_header)

    # we verify that we have a kid id
    if 'kid' not in unverified_header:
        print("error: 'kid' is not in header")
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # pick the needed key from jwks and structure the rsa_key
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # print('rsa_key: ', rsa_key)
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            # print('PL: ', payload)
            return payload

        except jwt.ExpiredSignatureError:
            print('error: expired signature')
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            print('error: claims error')
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. \
                                Please, check the audience and issuer.'
            }, 401)
        except Exception:
            print("error: exception")
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    # print("error outside, no rsa_key")
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                # print("Token: ", token)
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
                return f(payload, *args, **kwargs)
            except Exception as e:
                print('something went wrong: ', e)
                if isinstance(e, AuthError):
                    abort(e.status_code)
                else:
                    abort(e)

        return wrapper
    return requires_auth_decorator
