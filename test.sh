#!/usr/bin/bash

#=============================
# Author: Will Fenton
# Date:   October 6 2019
#=============================

echo "Deleting database"
rm tweets.db

echo "Creating database"
sqlite3 tweets.db < create-tables.sql

echo "Scraping tweets"
python3 parse.py

echo "Done!"
