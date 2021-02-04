import tweepy
from utils import settings

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token("access_token", "access_token_secret")

twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
