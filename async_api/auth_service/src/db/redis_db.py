import datetime
from redis.asyncio import Redis
from core.config import settings

ACCESS_TOKEN_BANNED = 'banned_tokens'
REFRESH_TOKENS_VALID = 'valid_refresh'
LAST_LOGOUT_ALL_LIST = 'last_logout_all'

TOKEN_SEP = '<TOKEN_SEP>'
MIN_TIME = datetime.datetime(1971, 1, 1, 0, 0, 0).timestamp()


# class RedisTokenStorage:
#
#     def __init__(self, redis_instance: Redis):
#         self._redis = redis_instance
#
#     async def _add_token(self, redis_key: str, user_id: str, token: str) -> int:
#         tokens = await self._redis.hgetall(redis_key)
#         tokens = {key.decode('utf-8'): value.decode('utf-8') for key, value in tokens.items()}
#         if not tokens.get(user_id, ''):
#             tokens[user_id] = token
#         else:
#             tokens[user_id] += TOKEN_SEP + token
#         rows_affected = await self._redis.hset(redis_key, mapping=tokens)
#
#         return rows_affected
#
#     async def _tokens_tidy(self, redis_key: str) -> int:
#         tokens = await self._redis.hgetall(redis_key)
#         tokens = {key.decode('utf-8'): value.decode('utf-8') for key, value in tokens.items()}
#
#         for user_id, user_tokens in tokens.items():
#             user_tokens_tidied = []
#             if user_tokens == '':
#                 continue
#             for token in user_tokens.split(TOKEN_SEP):
#                 payload_encoded = token.split('.')[1]
#                 payload = json.loads(urlsafe_b64decode(payload_encoded).decode('utf-8'))
#
#                 if payload['exp'] > time.time():
#                     user_tokens_tidied.append(token)
#
#             tokens[user_id] = TOKEN_SEP.join(user_tokens_tidied)
#
#         rows_affected = await self._redis.hset(redis_key, mapping=tokens)
#
#         return rows_affected
#
#     async def _check_token(self, redis_key: str, user_id: str, token: str):
#         tokens = await self._redis.hgetall(redis_key)
#         tokens = {key.decode('utf-8'): value.decode('utf-8') for key, value in tokens.items()}
#         if user_id not in tokens:
#             return False
#         else:
#             return token in tokens[user_id].split(TOKEN_SEP)
#
#     async def add_banned_atoken(self, user_id: str, token: str) -> int:
#         return await self._add_token(ACCESS_TOKEN_BANNED, user_id, token)
#
#     async def add_valid_rtoken(self, user_id: str, token: str) -> int:
#         return await self._add_token(REFRESH_TOKENS_VALID, user_id, token)
#
#     async def banned_atokens_tidy(self) -> int:
#         return await self._tokens_tidy(ACCESS_TOKEN_BANNED)
#
#     async def valid_rtokens_tidy(self) -> int:
#         return await self._tokens_tidy(REFRESH_TOKENS_VALID)
#
#     async def check_banned_atoken(self, user_id: int, token: str):
#         return await self._check_token(ACCESS_TOKEN_BANNED, user_id, token)
#
#     async def check_valid_rtoken(self, user_id: int, token: str):
#         return await self._check_token(REFRESH_TOKENS_VALID, user_id, token)
#
#     async def set_user_last_logout_all(self, user_id):
#         last_logouts = await self._redis.hgetall(LAST_LOGOUT_ALL_LIST)
#         last_logouts = {key.decode('utf-8'): value.decode('utf-8') for key, value in last_logouts.items()}
#         last_logouts[user_id] = time.time()
#         rows_affected = await self._redis.hset(LAST_LOGOUT_ALL_LIST, mapping=last_logouts)
#
#         return rows_affected
#
#     async def get_user_last_logout_all(self, user_id):
#         last_logouts = await self._redis.hgetall(LAST_LOGOUT_ALL_LIST)
#         last_logouts = {key.decode('utf-8'): value.decode('utf-8') for key, value in last_logouts.items()}
#         return last_logouts.get(user_id, MIN_TIME)
#
#     async def bgsave(self):
#         return await self._redis.bgsave()
#
#     async def close(self):
#         return await self._redis.close()
#
#     async def delete_refresh(self, user_id: str, refresh_token: str):
#         tokens = await self._redis.hgetall('valid_refresh')
#         tokens = {key.decode('utf-8'): value.decode('utf-8') for key, value in tokens.items()}
#         if user_id in tokens:
#             user_tokens = tokens[user_id].split(TOKEN_SEP)
#             try:
#                 user_tokens.remove(refresh_token)  # TODO: now works O(n)
#             except ValueError:
#                 pass
#
#             tokens[user_id] = TOKEN_SEP.join(user_tokens)
#
#         rows_affected = await self._redis.hset('valid_refresh', mapping=tokens)
#
#         return rows_affected
#
#     async def delete_refresh_all(self, user_id: str):
#         tokens = await self._redis.hgetall('valid_refresh')
#         tokens = {key.decode('utf-8'): value.decode('utf-8') for key, value in tokens.items()}
#         user_tokens = tokens.get(user_id, '')
#         user_tokens = ''
#         tokens[user_id] = user_tokens
#         # tokens[user_id] = TOKEN_SEP.join(user_tokens)
#
#         rows_affected = await self._redis.hset('valid_refresh', mapping=tokens)
#
#         return rows_affected


# redis: Optional[RedisTokenStorage] = None
# redis_session = Redis(host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True)
#
# cache: Optional[Redis] = None
#
#
# async def get_redis() -> Redis:
#     return redis_session


redis_session = Redis(host=settings.redis_host, port=settings.redis_port, ssl=False)

redis: Redis | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis_session
