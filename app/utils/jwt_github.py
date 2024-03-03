import time

import jwt
from jwt import JWT

from app.core import settings


def get_token():
    signing_key = jwt.jwk_from_dict(settings.SIGNING_KEY)

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': settings.APP_ID
    }

    return JWT().encode(payload, signing_key, alg='RS256')
