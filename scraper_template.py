"""
Sources::
https://towardsdatascience.com/scraping-reddit-data-1c0af3040768
https://github.com/reddit-archive/reddit/wiki/OAuth2
https://www.storybench.org/how-to-scrape-reddit-with-python/
"""

import praw #Wrapper for reddit api
import pandas as pd
import datetime as dt
import sys
import os
from threading import Timer

#takes in tf; time frame to scrape from
def dataget(tf):
    ### END OF PREPROCESS ###
    reddit = praw.Reddit(client_id='yourID', client_secret='yourSecret',user_agent='your agent name')

    """
    #Get top posts from subreddit
    #Ex: 'all' will scrape all subreddits, 'Machinelearning' will scrape ML subreddit
    """
    #PRAW only gets up to 1k
    lim = 1000
    sub = 'AmITheAsshole'
    top_subreddit = reddit.subreddit(sub).top(time_filter=tf,limit=lim)

    topics_dict = { "title":[], \
                    "score":[], \
                    "flair":[], \
                    "comms_num": [], \
                    #"comments": [], \
                    "edited": [], \
                    "created": [], \
                    "body":[], \
                    "locked":[], \
                    "id":[]} #"url":[]}
    count = 0.0
    for submission in top_subreddit:
        progress = (count/lim)*100.0
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["flair"].append(submission.link_flair_text)
        topics_dict["id"].append(submission.edited)
        topics_dict["edited"].append(submission.id)
        topics_dict["locked"].append(submission.locked)
        #topics_dict["comments"].append(submission.comments)
        #topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
        sys.stdout.write("Download progress: %d%%   \r" % (progress) )
        sys.stdout.flush()
        count = count+1.0

    topics_data = pd.DataFrame(topics_dict)
    print(" ")
    print(" Total get: ",count)

    #Fix date and time
    def get_date(created):
        return dt.datetime.fromtimestamp(created)

    _timestamp = topics_data["created"].apply(get_date)

    topics_data = topics_data.assign(timestamp = _timestamp)

    #Export to CSV
    d = dt.date.today().strftime("%d-%m-%Y")
    dirName = 'Data/'+d


    try:
        os.makedirs(dirName)
    except FileExistsError:
        print("directory already exists")

    topics_data.to_csv(dirName+'/AITA_'+tf+d+'_.csv', index=False)
    topics_data.to_csv('Data/all/AITA_'+tf+d+'_.csv', index=False)

    a_hole = 0
    nta = 0
    es = 0
    nah = 0
    for item in topics_data['flair']:
        if (item == 'Asshole'):
            a_hole = a_hole + 1
        if (item == 'Not the A-hole'):
            nta = nta + 1
        if (item == 'Everyone Sucks'):
            es = es + 1
        if (item == 'No A-holes here'):
            nah = nah + 1

    print("Assholes: ",a_hole)
    print("Not assholes: ", nta)
    print("everyone sucks: ",es)
    print("No one is an asshole: ",nah)

def __main__():
    print("starting...")
    dataget('day')
    dataget('week')
    dataget('month')
    dataget('year')
    dataget('all')
__main__()
