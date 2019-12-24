import pandas as pd
import requests
import json
import time
import datetime

# This was adapted from https://medium.com/@RareLoot/using-pushshifts-api-to-extract-reddit-submissions-fb517b286563

jsonDir = "../raw/"
subreddit = ["GoogleMaps", "applemaps"]
# subreddit = ["waze", "GoogleMaps", "applemaps"]
# subreddit = ["applemaps"]
startDate = "1514764800" # Jan 1, 2018
subStats = []
comments = []
textOnly = []

def getPushshiftData(after, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?size=1000&after='+str(after)+'&subreddit='+str(sub)
    print(url)
    r = requests.get(url)
    data = json.loads(r.text)
    return data['data']

def getPushshiftDataComments(after, sub, subm_id):
    url = 'https://api.pushshift.io/reddit/search/comment/?size=1000&after='+str(after)+'&subreddit='+str(sub)+'&link_id='+str(subm_id)
    print(url)
    r = requests.get(url)
    data = json.loads(r.text)
    return data['data']

def collectCommentData(comm):
    body = comm['body']
    author = comm['author']
    comm_id = comm['id']
    score = comm['score']
    created = datetime.datetime.fromtimestamp(comm['created_utc']) #1520561700.0
    parent_id = comm['parent_id']
    permalink = comm['permalink']

    textOnly.append({
        "id": comm_id,
        "body": body
    })
    
    return {
        "subreddit": subreddit,
        "comm_id": comm_id,
        "body": body,
        "author": author,
        "score": score,
        "created": str(created.year) + "-" + str(created.month) + "-" + str(created.day),
        "permalink": permalink,
        "parent_id": parent_id
    }

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

    if selftext:
        textOnly.append({
        "id": sub_id,
        "body": selftext
    })

    comments = []
    raw_comments = getPushshiftDataComments(startDate, subreddit, sub_id)
    print(sub_id + ": " + str(len(raw_comments)))
    for entry in raw_comments:
        comments.append(collectCommentData(entry))

    print(str(len(comments)))
    
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
        "selftext": selftext,
        "comments": comments
    })

def collectPerSubreddit(sub):
    data = getPushshiftData(startDate, sub)

    # Will run until all posts have been gathered 
    # from the 'after' date up until before date
    while len(data) > 0:
        for submission in data:
            collectSubData(submission)
        # Calls getPushshiftData() with the created date of the last submission
        print(len(data))
        print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
        after = data[-1]['created_utc']
        data = getPushshiftData(after, sub)

    jsonName = "raw_submissions_" + sub + "_2019.json"
    with open(jsonDir + jsonName, "w+") as jsonFile:
        json.dump(subStats, jsonFile)

    textOnlyName = "raw_textonly_" + sub + "_2019.json"
    with open(jsonDir + textOnlyName, "w+") as jsonFile:
        json.dump(textOnly, jsonFile)

for sub in subreddit:
    startDate = "1514764800" # Jan 1, 2018
    collectPerSubreddit(sub)
    subStats = []
    textOnly = []
