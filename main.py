#!/usr/bin/env python3

import time
import praw
from reddit_oauth import cid, csec, pw
import logging
from datetime import date

def main():
    user = sr = "unexpected_relevance"
    #pw = getpass.getpass()    
    reddit = praw.Reddit(client_id=cid,
                         client_secret=csec,
                         username=user,
                         password=pw,
                         user_agent="Script to crosspost saved posts")

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=date.today().strftime("%Y%m%d") + ".log",
                    filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO) 
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console) 
    
    logging.info("Successfully authenticated user : " + reddit.user.me().name)
    
    saved = list(reddit.user.me().saved(limit=None))
    saved.reverse()
    num_saved = len(saved)
    logging.info("Number of items saved : " + str(num_saved))

    i = 1
    successes = 0
    fails = 0
    for item in saved:
        try:
            if i > num_saved: break
            if isinstance(item, praw.models.Comment):
                try:
                    body = item.permalink + "\n\n" + item.body + "\n\n User : " + item.author.name
                except AttributeError:
                    logging.error("Could not find user (removed or deleted)")
                    body = item.permalink + "\n\n" + item.body + "\n\n User : [deleted]"

                title = item.submission.title
                reddit.subreddit(sr).submit(title="Comment : " + title, selftext=body)
            if isinstance(item, praw.models.Submission):
                title = item.title
                item.crosspost(sr, title=title, send_replies=False)
            
            item.unsave()
            logging.info(str(i) + "/" + str(num_saved) + " : Successfully crossposted : " + title)
            successes = successes + 1
        except praw.exceptions.RedditAPIException:
            logging.error(str(i) + "/" + str(num_saved) + " : Failed to crosspost : " + title)
            fails = fails + 1
            pass

        i = i + 1
        time.sleep(2)

    logging.info("\nOperation complete")
    logging.info("Successes : " + str(successes))
    logging.info("Fails : " + str(fails))


if __name__ == "__main__":
    main()
