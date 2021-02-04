import redis

redis_cli = redis.StrictRedis(
    host="localhost", port=6379, password="", decode_responses=True
)
