import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from core.config import settings
from functools import lru_cache

class TokenService:
    def __init__(self) -> None:
        self.secret_key = settings.secret_key.encode('utf-8')

    def _sign_data(self, data: str) -> str:
        hmac_obj = hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256)
        signature = hmac_obj.digest()
        signature_b64 = urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        return signature_b64

    def _validate_data(self, data: str, sign: str) -> bool:
        return self._sign_data(data) == sign

    def decode_b64(self, data: str):
        length = len(data) + (4 - (len(data) % 4))
        data_padded = data.ljust(length, '=')
        return urlsafe_b64decode(data_padded).decode('utf-8')

    def validate_token(self, token):
        try:
            header, payload, sign = token.split('.')
            return self._validate_data(f'{header}.{payload}', sign)
        except ValueError:
            return False


class AccessTokenService(TokenService):
    def __init__(self):
        super().__init__()
        self.access_token_min = settings.access_token_min

    def generate_token(self, iss: str, sub: str, roles: list[str]):
        header = json.dumps({'alg': 'HS256', 'typ': 'JWT'})
        header_b64 = urlsafe_b64encode(header.encode('utf-8')).decode('utf-8').rstrip('=')

        iat = int(time.time())
        exp = iat + self.access_token_min * 60
        payload = json.dumps({'iss': iss, 'sub': sub, 'iat': iat, 'exp': exp, 'roles': roles})
        payload_b64 = urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8').rstrip('=')

        for_sign = header_b64 + '.' + payload_b64
        sign = self._sign_data(for_sign)

        token = header_b64 + '.' + payload_b64 + '.' + sign

        return token, exp


class RefreshTokenService(TokenService):
    def __init__(self):
        super().__init__()
        self.refresh_token_weeks = settings.refresh_token_weeks

    def generate_token(self, iss: str, sub: str):
        header = json.dumps({'alg': 'HS256', 'typ': 'JWT'})
        header_b64 = urlsafe_b64encode(header.encode('utf-8')).decode('utf-8').rstrip('=')

        iat = int(time.time())
        exp = iat + self.refresh_token_weeks * 7 * 24 * 60 * 60
        payload = json.dumps({'iss': iss, 'sub': sub, 'iat': iat, 'exp': exp})
        payload_b64 = urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8').rstrip('=')

        for_sign = header_b64 + '.' + payload_b64
        sign = self._sign_data(for_sign)

        token = header_b64 + '.' + payload_b64 + '.' + sign

        return token, exp


@lru_cache
def get_access_token_service() -> AccessTokenService:
    return AccessTokenService()


@lru_cache
def get_refresh_token_service() -> RefreshTokenService:
    return RefreshTokenService()
