#=============================
# Author: Will Fenton
# Date:   October 4 2019
#=============================

import json
import time
import sqlite3
import tweepy

#=============================

with open("api_key.txt", 'r') as f:
    api_key = f.read().strip()

with open("api_secret.txt", 'r') as f:
    api_secret = f.read().strip()

auth = tweepy.OAuthHandler(api_key, api_secret)
api = tweepy.API(auth)

#=============================

hashtag = "ExtinctionRebellion"

query = "%23{}+-filter:retweets".format(hashtag)

db = sqlite3.connect("tweets.db")

# determine the highest and lowest tweet id in the database
# so that we can avoid duplicate tweets
count = int(db.execute("SELECT COUNT(DISTINCT id) FROM Hashtag WHERE hashtag=? COLLATE NOCASE;", [hashtag]).fetchone()[0])
if count > 0:
    min_id = int(db.execute("SELECT MIN(id) FROM Hashtag WHERE hashtag=? COLLATE NOCASE;", [hashtag]).fetchone()[0]) - 1
    max_id = int(db.execute("SELECT MAX(id) FROM Hashtag WHERE hashtag=? COLLATE NOCASE;", [hashtag]).fetchone()[0]) + 1

#=============================

# this method handles the twitter api's rate limit
# sleeps for 15 minutes on an error
def limit_handled(cursor, db):
    while True:
        try:
            db.commit()
            yield cursor.next()
        except Exception as e:
            db.commit()
            print(e)
            print("Sleeping for 15 minutes")
            time.sleep(15 * 60)

def insert_tweet(tweet, db):
    tweet_id = tweet.id_str
    tweet_text = tweet.full_text

    print(tweet_id)

    db.execute("INSERT INTO Tweet VALUES (?, ?);", [tweet_id, tweet_text])

    entities = tweet.entities

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

#=============================

# keep getting pages of tweets and adding them to the database
if count > 0:
    for tweet in limit_handled(tweepy.Cursor(api.search, q=query, max_id=min_id, since=max_id, count=100, result_type="recent", tweet_mode="extended").items(), db):
        insert_tweet(tweet, db)
else:
    for tweet in limit_handled(tweepy.Cursor(api.search, q=query, count=100, result_type="recent", tweet_mode="extended").items(), db):
        insert_tweet(tweet, db)

#=============================

db.commit()
db.close()
