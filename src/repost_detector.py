import requests
from urllib.parse import urlencode
from difflib import SequenceMatcher

def similarity(x: str, y: str):
    return SequenceMatcher(None, x.lower(), y.lower()).ratio()

URL_TARGET = 'https://api.pushshift.io/reddit/search/submission/?subreddit=copypasta&{}'.format

def search(selftext: str) -> list:
    q = {"selftext": selftext}

    r = requests.get(URL_TARGET(urlencode(q)))
    return r.json()["data"]

def is_repost(text: str):
    result = search(text)
    if not result:
        return False
    matchs = []
    for sub in result:
        score = similarity(sub["selftext"], text)

        if score >= 0.9:
            matchs.append({
                "title": sub["title"],
                "score": f"{score/1*100}%",
                "link": sub["full_link"],
                "author": sub["author"]
            })
    return matchs