#=============================
# Author: Will Fenton
# Date:   October 4 2019
#=============================

import json
import time
import sqlite3
import tweepy

#=============================

hashtags = ["TuesdayThoughts"]
# hashtags = ["HipHopAwards"]
# hashtags = ["cdnpoli", "elxn43", "leadersdebate2019"]

#=============================

def get_tables(db):
    results = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in results.fetchall()]
    return tables

def get_hashtag_string(hashtags):
    if len(hashtags) == 0:
        raise Exception("Need at least 1 hashtag")
    else:
        return '-'.join(sorted([hashtag.lower() for hashtag in hashtags]))

def create_tables(hashtags, db):
    hashtag_string = get_hashtag_string(hashtags)

    tweet_table_name = f"Tweets-{hashtag_string}"
    hashtag_table_name = f"Hashtags-{hashtag_string}"
    url_table_name = f"Urls-{hashtag_string}"
    mention_table_name = f"Mentions-{hashtag_string}"

    table_names = [tweet_table_name, hashtag_table_name, url_table_name, mention_table_name]
    tables = get_tables(db)

    for table_name in table_names:
        if table_name in tables:
            return

    db.execute(f"CREATE TABLE [{tweet_table_name}] \
        (id INTEGER, body TEXT, PRIMARY KEY(id));")
    db.execute(f"CREATE TABLE [{hashtag_table_name}] \
        (id INTEGER, hashtag TEXT, start_index INTEGER, end_index INTEGER, FOREIGN KEY(id) REFERENCES Tweet);")
    db.execute(f"CREATE TABLE [{url_table_name}] \
        (id INTEGER, url TEXT, start_index INTEGER, end_index INTEGER, FOREIGN KEY(id) REFERENCES Tweet);")
    db.execute(f"CREATE TABLE [{mention_table_name}] \
        (id INTEGER, mention TEXT, start_index INTEGER, end_index INTEGER, FOREIGN KEY(id) REFERENCES Tweet);")

def get_api_keys():
    with open("api_key.txt", 'r') as f:
        api_key = f.read().strip()

    with open("api_secret.txt", 'r') as f:
        api_secret = f.read().strip()

    return api_key, api_secret

def get_count(hashtag_string, db):
    return db.execute(f"SELECT COUNT(DISTINCT id) FROM [Tweets-{hashtag_string}];").fetchone()[0]

def get_cursor(hashtags, db, num_tweets=100, result_type="recent", tweet_mode="extended"):
    s = "+OR+%23".join(sorted([hashtag.lower() for hashtag in hashtags]))
    query = f"%23{s}+-filter:retweets"

    print(query)
    
    hashtag_string = get_hashtag_string(hashtags)

    count = get_count(hashtag_string, db)
    if count == 0:
        cursor = tweepy.Cursor(
            api.search, q=query, count=num_tweets, result_type=result_type, tweet_mode=tweet_mode)
    else:
        min_id = db.execute(f"SELECT MIN(id) FROM [Tweets-{hashtag_string}];").fetchone()[0] - 1
        max_id = db.execute(f"SELECT MAX(id) FROM [Tweets-{hashtag_string}];").fetchone()[0] + 1
        cursor = tweepy.Cursor(
            api.search, q=query, max_id=min_id, since=max_id, count=num_tweets, result_type=result_type, tweet_mode=tweet_mode)

    return cursor

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

def insert_tweet(tweet, hashtag_string, db):
    tweet_id = tweet.id_str
    tweet_text = tweet.full_text

    print(tweet_id)

    db.execute(f"INSERT INTO [Tweets-{hashtag_string}] VALUES (?, ?);", [tweet_id, tweet_text])

    entities = tweet.entities

    for hashtag in entities["hashtags"]:
        text = hashtag["text"].lower()
        start, end = hashtag["indices"]
        db.execute(f"INSERT INTO [Hashtags-{hashtag_string}] VALUES (?, ?, ?, ?);", [tweet_id, text, start, end])

    for url in entities["urls"]:
        text = url["url"].lower()
        start, end = url["indices"]
        db.execute(f"INSERT INTO [Urls-{hashtag_string}] VALUES (?, ?, ?, ?);", [tweet_id, text, start, end])

    for mention in entities["user_mentions"]:
        name = mention["screen_name"].lower()
        start, end = mention["indices"]
        db.execute(f"INSERT INTO [Mentions-{hashtag_string}] VALUES (?, ?, ?, ?);", [tweet_id, name, start, end])

#=============================

hashtag_string = get_hashtag_string(hashtags)

db = sqlite3.connect("tweets.db")
create_tables(hashtags, db)

api_key, api_secret = get_api_keys()
auth = tweepy.OAuthHandler(api_key, api_secret)
api = tweepy.API(auth)

cursor = get_cursor(hashtags, db)

for tweet in limit_handled(cursor.items(), db):
    insert_tweet(tweet, hashtag_string, db)

db.commit()
db.close()

#=============================
