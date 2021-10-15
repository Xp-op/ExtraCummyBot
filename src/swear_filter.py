from profanity_filter import ProfanityFilter
import json

pf = ProfanityFilter()

pf.censor_char = '-'

censor = pf.censor

illegals = ["nigga",
            "niggas",
            "nigger",
            "niggers",
            "negro",
            "cunt",
            "retard",
            "fagot"]
badwords = json.load(open("words.json"))
limit = 14

def clean_str(s: str):
    r = []
    for word in s.split():
        r.append(''.join(c for c in word if c.isalpha()))
    return ' '.join(r)

def can_censor(text: str):
    text_s = list(map(str.lower, clean_str(text).split()))
    if any((any(w.startswith(x) for w in text_s) for x in illegals)):
        return True
    c = 0
    for w in badwords:
        for word in text_s:
            if word.startswith(w):
                c += 1
    return c >= limit