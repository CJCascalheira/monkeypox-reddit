''' 
The following script was used to extract all the comments from May 1, 2022
@ 12:00am UTC until the current date and time (October 13, 2022) from the 
subreddit: r/lgbt

The term "Reddit Scraping" is used when computer programs (known as web
scrapers) are used to extract publicly available data from the Reddit website.
This same script was used in order to scrape the subreddit comments (from the
same time frame of May 1, 2022 @ 12:00am UTC until the current date & time)
from the following subreddits: 
r/gaymers
r/ainbow
r/askgaybros
r/asktransgender
r/MtF
r/NonBinary
Note: These subreddits are the nine most popular subreddits among LGBTQ+ people.

The only change that was made to this script to extract comments from those
specified subreddits was changing the argument of the last line to the 
according to the specific subreddit.
Example: For r/gaymers, the line was changed to
    extract_reddit_data(subreddit="gaymers",type="comment")
    
This code was taken from:
https://www.osrsbox.com/blog/2019/03/18/watercooler-scraping-an-entire-subreddit-2007scape/
and modified accordingly for this project.
'''
import requests
import json
import re
import time

PUSHSHIFT_REDDIT_URL = "http://api.pushshift.io/reddit"

def fetchObjects(**kwargs):
    # Default paramaters for API query
    params = {
        "sort_type":"created_utc",
        "sort":"asc",
        "size":1000
        }

    # Add additional paramters based on function arguments
    for key,value in kwargs.items():
        params[key] = value

    # Print API query paramaters
    print(params)

    # Set the type variable based on function input
    # The type can be "comment" or "submission", default is "comment"
    type = "comment"
    if 'type' in kwargs and kwargs['type'].lower() == "submission":
        type = "submission"
    
    # Perform an API request
    r = requests.get(PUSHSHIFT_REDDIT_URL + "/" + type + "/search/", params=params, timeout=30)

    # Check the status code, if successful, process the data
    if r.status_code == 200:
        response = json.loads(r.text)
        data = response['data']
        sorted_data_by_id = sorted(data, key=lambda x: int(x['id'],36))
        return sorted_data_by_id

def extract_reddit_data(**kwargs):
    # Speficify the start timestamp
    max_created_utc = 1651363200 # 05/01/2022 @ 12:00am (UTC)
    max_id = 0

    # Open a file for JSON output
    file = open("comments.json","a")

    # While loop for recursive function
    while 1:
        nothing_processed = True
        # Call the recursive function
        objects = fetchObjects(**kwargs,after=max_created_utc)
        
        # Loop the returned data, ordered by date
        for object in objects:
            id = int(object['id'],36)
            if id > max_id:
                nothing_processed = False
                created_utc = object['created_utc']
                max_id = id
                if created_utc > max_created_utc: max_created_utc = created_utc
                # Output JSON data to the opened file
                print(json.dumps(object,sort_keys=True,ensure_ascii=True),file=file)
        
        # Exit if nothing happened
        if nothing_processed: return
        max_created_utc -= 1

        # Sleep a little before the next recursive function call
        time.sleep(.5)

# Start program by calling function with:
# 1) Subreddit specified
# 2) The type of data required (comment or submission)
extract_reddit_data(subreddit="lgbt",type="comment")