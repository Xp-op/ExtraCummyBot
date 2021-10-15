import praw
import praw.exceptions
import time
from swear_filter import censor, can_censor
import os
from repost_detector import is_repost
from praw.models.util import stream_generator


ID_BOT = os.getenv("ID_BOT")
SEC_BOT = os.getenv("SECRET_BOT")
PASSWORD = os.getenv("PASSWORD")

# speedy boat in my house lmao

class CummyBot:

    def __init__(self, version: tuple, developer: str, id: str, secret: str, username: str, password:str) -> None:
        self.bot = praw.Reddit(
            user_agent=f'{".".join(map(str,version))} [Author:{developer}]',
            client_id=id,
            client_secret=secret,
            username=username,
            password=password
        )
        self.func_post = None
        self.func_comment = None
        self.requests_amount = 0
        self.username = username

    def __repr__(self) -> str:
        return self.bot.user.me().__repr__()

    def when_new_post(self):
        def deco(func):
            self.func_post = func
        return deco

    def when_new_comment(self):
        def deco(func):
            self.func_comment = func
        return deco
    
    def _stream(self, sub):
        def __com_post(**kwargs):
            return [*sub.new(**kwargs), *sub.comments(**kwargs)]
        return __com_post

    def stream(self, sub):
        return stream_generator(self._stream(sub), skip_existing=True)

    def start(self, subreddit_name: str):
        subreddit = self.bot.subreddit(subreddit_name)
        for reddit_obj in self.stream(subreddit):
            if isinstance(reddit_obj, praw.reddit.Submission):
                self.func_post(self, reddit_obj)
            else:
                self.func_comment(self, reddit_obj)

bot = CummyBot( (0,1),
                "Xp(u/I_have_good_memes)",
                ID_BOT,
                SEC_BOT,
                "ExtraCummyBot1000",
                PASSWORD )

def split_max(s: str, max_len: int):
    if len(s) < max_len:
        return [s]
    l = []
    curr = s
    while True:
        c = curr[:max_len]
        if not c:
            break
        l.append(c)
        curr = curr[max_len:]
    return l

def reply(sub, text, fmt=(), fmts=None):
    bot.requests_amount += 1
    if bot.requests_amount == 15:
        print("Sleep for 5 minutes")
        time.sleep(300)
        bot.requests_amount = 0
    sub.reply(text.format(*fmt, **(fmts or {})))

def main():
    os.system("clear")
    print(f"Bot Name: {bot.username}")

    @bot.when_new_post()
    def event(bot, sub: praw.reddit.Submission):
        print(f"Found post: {sub.title}\nLink: {sub.permalink}")
        text = (sub.title if not sub.selftext else sub.selftext)

        posts = is_repost(text)
        if posts:
            s = "This copypasta seem like a repost\n"
            for post in posts:
                title = post["title"][:20]
                link = post["link"]
                author = post["author"]
                score = post["score"]
                s += f"\n[{title}]({link}) by u/{author} (Score: {score})\n"

            s += "\nIf you think this is a false detect, report it to u/I_have_good_memes"
            reply(sub, s)
            return

        for msg in split_max(text, 9999):
            reply(sub, censor(msg) if can_censor(msg) else msg)
        print("Replied")
    
    @bot.when_new_comment()
    def event_com(bot, com: praw.reddit.Comment):
        sub = com.submission
        print(f"Found comment on {sub.title}\nLink: {com.permalink}")

        body = com.body.lower()

        if body.startswith(f"u/{bot.username} repost"):
            print("comment is invoking the repost check")
            text = (sub.title if not sub.selftext else sub.selftext)

            posts = is_repost(text)
            if posts:
                s = "This copypasta seem like a repost\n"
                for post in posts:
                    title = post["title"][:20]
                    link = post["link"]
                    author = post["author"]
                    score = post["score"]
                    s += f"\n[{title}]({link}) by u/{author} (Score: {score})\n"

                s += "\nIf you think this is a false detect, report it to u/I_have_good_memes"
                reply(com, s)
                return
            else:
                reply(com, "This copypasta is original! Congrats OP")
            

    while True:
        try:
            bot.start("copypasta+extracummybot")
        except KeyboardInterrupt:
            return
        except praw.exceptions.APIException as e:
            print("Error, Retrying in 10 minutes")
            print(e)
            time.sleep(600)
            continue

if __name__ == '__main__':
    main()