# See: https://auth0.com/docs/quickstart/backend/python/01-authorization#validate-access-tokens
import os
import logging

import requests
from jose import jwt
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve

from users.models import User



class AuthError(Exception):
    pass


class RecipeDetailsAuthentication(object):
    """
    This authentication class returns an AnonymousUser when
    GETting a single Recipe to view, since viewing single Recipes
    should be publically available.
    """
    def authenticate(self, request):
        url_name = resolve(request.path).url_name
        # Note: 'recipes-detail' is created by DRF's SimpleRouter.
        # This must be updated if the "recipes" basename changes.
        if url_name == 'recipes-detail' and request.method == 'GET':
            return AnonymousUser, None
        return None


# TODO: test
class DRFAuth0Authentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            self._authenticate(request)
        except AuthError as e:
            logging.error(e)
            return None

    def _authenticate(self, request):
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
                    issuer=f"https://{auth0_domain}/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError("token is expired")
            except jwt.JWTClaimsError:
                raise AuthError("incorrect claims, please check the audience and issuer")
            except Exception:
                raise AuthError("Unable to parse authentication token.")

            user_email = payload.get('https://recipes/email')
            (user, _) = User.objects.get_or_create(email=user_email, defaults={
                'username': user_email,
            })
            return user, True
        raise AuthError("Unable to find appropriate key")


# Format error response and append status code
def get_token_auth_header(request):
    """
    Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)

    if not auth:
        raise AuthError("Authorization header is expected")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError("Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise AuthError("Token not found")
    elif len(parts) > 2:
        raise AuthError("Authorization header must be Bearer token")

    token = parts[1]
    return token
