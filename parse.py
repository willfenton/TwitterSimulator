import json
import sqlite3
import tweepy

with open("api_key.txt", 'r') as f:
    api_key = f.read().strip()

with open("api_secret.txt", 'r') as f:
    api_secret = f.read().strip()

# print(api_key)
# print(api_secret)

auth = tweepy.OAuthHandler(api_key, api_secret)
api = tweepy.API(auth)

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet.text)

tweets = api.search(q="%23ImpeachDonaldTrumpNOW+-filter:retweets", count=100, result_type="recent", tweet_mode="extended")
for tweet in tweets:
    tweet_id = tweet.id_str
    tweet_text = tweet.full_text


db = sqlite3.connect("tweets.db")

with open("query.json", 'r') as f:
    json = json.load(f)

for tweet in json["statuses"]:
    if "retweeted_status" not in tweet.keys():

        tweet_id = tweet["id_str"]
        tweet_text = tweet["full_text"] 

        db.execute("INSERT INTO Tweet VALUES (?, ?);", [tweet_id, tweet_text])

        entities = tweet["entities"]

        for hashtag in entities["hashtags"]:
            text = hashtag["text"].lower()
            start, end = hashtag["indices"]
            db.execute("INSERT INTO Hashtag VALUES (?, ?, ?, ?);", [tweet_id, text, start, end])

        for url in entities["urls"]:
            text = url["url"].lower()
            start, end = url["indices"]
            db.execute("INSERT INTO Url VALUES (?, ?, ?, ?);", [tweet_id, text, start, end])

        for mention in entities["user_mentions"]:
            name = mention["screen_name"].lower()
            start, end = mention["indices"]
            db.execute("INSERT INTO Mention VALUES (?, ?, ?, ?);", [tweet_id, name, start, end])

db.commit()
db.close()