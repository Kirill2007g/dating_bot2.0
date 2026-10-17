import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
async def save_ten_ankets_in_redis(ten_ankets: list):
