#=============================
# Author: Will Fenton
# Date:   October 7 2019
#=============================

import sqlite3
from parse import get_hashtag_string

#=============================

# hashtags = ["WorldMentalHealthDay", "WorldMentalHealthDay2019", "MentalHealthAwarenessDay"]
# hashtags = ["TuesdayThoughts"]
# hashtags = ["WednesdayWisdom"]
hashtags = ["HipHopAwards"]
# hashtags = ["cdnpoli", "elxn43", "leadersdebate2019"]

#=============================

db = sqlite3.connect("tweets.db")

hashtag_string = get_hashtag_string(hashtags)

tweets = db.execute(f"SELECT body FROM [Tweets-{hashtag_string}];")

with open(f"dataset/{hashtag_string}.txt", 'w') as f:
    while True:
        try:
            text = tweets.fetchone()[0]
            f.write(text)
            f.write("\n\n<|endoftext|>\n\n")
        except:
            break

db.close()

#=============================
