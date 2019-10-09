#=============================
# Author: Will Fenton
# Date:   October 7 2019
#=============================

import sqlite3

#=============================

db = sqlite3.connect("tweets.db")

result = db.execute("SELECT body FROM tweet;")

with open("tweets.txt", 'w') as f:
    while True:
        try:
            text = result.fetchone()[0]
            f.write(text)
            f.write("\n\n<|endoftext|>\n\n")
        except:
            break

db.close()