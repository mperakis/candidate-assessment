import datetime
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils import redis_cli, twitter_api
import config

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
api = Api(app)
auth = HTTPBasicAuth()

from models import User


# helper functions
def json_formatter(data):
    ...

def csv_formatter(data):
    ...

# when user registers we use generate_password_hash
# to encrypt password before store it in database
# not implemeted yet
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if username and check_password_hash(user.password, password):
        return username

# class decorator to decorate all methods
@auth.login_required
class TwitterWords(Resource):

    response_format_map = {
        "json": json_formatter,
        "csv": csv_formatter
    }

    def get(self):
        hashtag = request.args.get("hashtag")
        word_count = request.args.get("wordcount")
        response_format = request.args.get("format")

        if not hashtag:
            return {"msg": "Missing hashtag query parameter", }, 404

        time_now = datetime.datetime.utcnow()
        yesterday = time_now.date() - datetime.timedelta(days=1)
        tweets = {
            "word_cloud": "",
            "topic": hashtag,
            "first_tweet_at": "",
            "last_tweet_at": ""
        }
        cached_data_exists = redis_cli.exists(hashtag)
        if cached_data_exists:
            # gets all keys, values stored in redis hash
            # and returns a python dict
            tweets = redis_cli.hgetall(hashtag)
        else:
            data = twitter_api.search(q=hashtag, since=yesterday)
            tweets["word_cloud"] = " ".join([tweet.text for tweet in tweets]),
            tweets["first_tweet_at"] = tweets[0].time,  # if it's in descending order
            tweets["last_tweet_at"] = tweets[1].time

            # key expiration is in seconds (24h), I think
            redis_cli.hmset(hashtag, tweets, ex=86400)

        if word_count:
            tweets["word_cloud"] = " ".join(
                tweets["word_cloud"].split(" ")[:int(word_count)]
            )

        if response_format:
            return self.response_format_map[response_format.lower()](tweets), 200

        return self.response_format_map["json"](tweets), 200

api.add_resource(TwitterWords, '/twitterwords')

if __name__ == '__main__':
    app.run(debug=True)
