# See: https://auth0.com/docs/quickstart/backend/python/01-authorization#validate-access-tokens
import os

import requests
from jose import jwt
from rest_framework.authentication import BaseAuthentication

from users.models import User

"""
TODO: make sure the API returns whatever status code is set in the 
exception. The below code passes in 401, but Postman is getting 500
"""


class AuthError(Exception):
    pass


# TODO: test
class DRFAuth0Authentication(BaseAuthentication):
    def authenticate(self, request):
        auth0_domain = os.getenv('DJANGO_AUTH0_DOMAIN')
        api_audience = os.getenv('DJANGO_AUTH0_AUDIENCE')
        algorithms = ["RS256"]

        token = get_token_auth_header(request)
        r = requests.get(f"https://{auth0_domain}/.well-known/jwks.json")
        jwks = r.json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=algorithms,
                    audience=api_audience,
                    issuer="https://" + auth0_domain + "/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                     "incorrect claims,"
                                     "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                     "Unable to parse authentication"
                                     " token."}, 401)

            user_email = payload.get('https://recipes/email')
            (user, _) = User.objects.get_or_create(email=user_email, defaults={
                'username': user_email,
            })
            return user, True
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)


# Format error response and append status code
def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)

    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be Bearer token"}, 401)

    token = parts[1]
    return token
