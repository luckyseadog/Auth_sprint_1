from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import hmac
import json
import time
import datetime


SECRET_KEY = b"PRACTIX" # TODO: should be in ENV
ACCESS_MIN = 15 # TODO: should be in ENV
REFRESH_WEEKS = 2 # TODO: should be in ENV



class TokenService:
    def __init__(self) -> None:
        self.secret_key = SECRET_KEY

    def _sign_data(self, data: str) -> str:
        hmac_obj = hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256)
        signature = hmac_obj.digest()
        signature_b64 = urlsafe_b64encode(signature).rstrip(b'=')

        return signature_b64.decode('utf-8')
    
    def _validate_data(self, data: str, sign: str) -> bool:
        return self._sign_data(data) == sign


class AccessTokenService(TokenService):
    def generate_token(self, iss, sub, role):
        header = json.dumps({"alg": "HS256", "typ": "JWT"})
        header_b64 = urlsafe_b64encode(header.encode('utf-8')).rstrip(b'=').decode('utf-8')

        iat = int(time.time())
        exp = int(time.time() + datetime.timedelta(minutes=ACCESS_MIN).total_seconds())
        payload = json.dumps({"iss": iss, "sub": sub, "iat": iat, "exp": exp, "role": role})
        payload_b64 = urlsafe_b64encode(payload.encode('utf-8')).rstrip(b'=').decode('utf-8')

        for_sign = header_b64 + "." + payload_b64
        sign = self._sign_data(for_sign)
        
        token = header_b64 + "." + payload_b64 + "." + sign

        return token


class RefreshTokenService(TokenService):
    def generate_token(self, iss, sub):
        header = json.dumps({"alg": "HS256", "typ": "JWT"})
        header_b64 = urlsafe_b64encode(header.encode('utf-8')).rstrip(b'=').decode('utf-8')

        iat = int(time.time())
        exp = int(time.time() + datetime.timedelta(weeks=REFRESH_WEEKS).total_seconds())
        payload = json.dumps({"iss": iss, "sub": sub, "iat": iat, "exp": exp})
        payload_b64 = urlsafe_b64encode(payload.encode('utf-8')).rstrip(b'=').decode('utf-8')

        for_sign = header_b64 + "." + payload_b64
        sign = self._sign_data(for_sign)
        
        token = header_b64 + "." + payload_b64 + "." + sign

        return token
