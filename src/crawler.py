import pandas as pd
import requests
import json
import time
import datetime

# This was adapted from https://medium.com/@RareLoot/using-pushshifts-api-to-extract-reddit-submissions-fb517b286563

jsonDir = "../raw/"
subreddit = ["waze", "GoogleMaps", "applemaps"]
startDate = "1514764800" # Jan 1, 2018
subStats = []

def getPushshiftData(after, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?size=1000&after='+str(after)+'&subreddit='+str(sub)
    print(url)
    r = requests.get(url)
    data = json.loads(r.text)
    return data['data']

def collectSubData(subm):
    title = subm['title']
    url = subm['url']
    try:
        flair = subm['link_flair_text']
    except KeyError:
        flair = "NaN"    
    author = subm['author']
    sub_id = subm['id']
    score = subm['score']
    created = datetime.datetime.fromtimestamp(subm['created_utc']) #1520561700.0
    numComms = subm['num_comments']
    permalink = subm['permalink']
    selftext = subm['selftext']
    subreddit = subm["subreddit"]
    
    subStats.append({
        "subreddit": subreddit,
        "sub_id": sub_id,
        "title": title,
        "url": url,
        "author": author,
        "score": score,
        "created": str(created.year) + "-" + str(created.month) + "-" + str(created.day),
        "numComms": numComms,
        "permalink": permalink,
        "flair": flair,
        "selftext": selftext
    })
    # subStats[sub_id] = subData

def collectPerSubreddit(sub):
    data = getPushshiftData(startDate, sub)

    subCount = 0
    # Will run until all posts have been gathered 
    # from the 'after' date up until before date
    while len(data) > 0:
        for submission in data:
            collectSubData(submission)
            subCount+=1
        # Calls getPushshiftData() with the created date of the last submission
        print(len(data))
        print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
        after = data[-1]['created_utc']
        data = getPushshiftData(after, sub)

    jsonName = "raw_submissions_" + sub + ".json"
    with open(jsonDir + jsonName, "w+") as jsonFile:
        json.dump(subStats, jsonFile)

for sub in subreddit:
    collectPerSubreddit(sub)
    subStats = []
