import hashlib

from core.models import User, Post

from dateutil.parser import parse

def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())

def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(str(url).encode())
    return int(str(int(m.hexdigest(), 16))[:16])

def save_d(res_tw, res_us):
    users = []
    for us in res_us:
        try:
                User.objects.create(
                    id=us.get("id"),
                    sphinx_id=get_sphinx_id(us.get("id")),
                    name=us.get("name"),
                    screen_name=us.get("screen_name"),
                    url=us.get("url") or "",
                    followers=us.get("followers_count"),
                    district=0,
                    friends=us.get("friends_count") or 0,
                    created_date= parse(us.get("created_at")),
                    logo=us.get('profile_image_url'),


            )
        except Exception as e:
            print(e)
    for tw in res_tw:
        try:
            Post.objects.create(
                id=tw.get("id"),
                from_id=tw.get("user_id"),
                owner_sphinx_id=get_sphinx_id(tw.get("user_id")),
                content=tw.get("full_text"),
                repost_of=bool(tw.get('retweeted')),
                created_date=parse(tw.get("created_at")),
                viewed=tw.get('ext_views', {}).get("count") or 0,
                comments=tw.get('retweet_count') or 0,
                reposts=tw.get('reply_count') or 0,
                likes=tw.get('favorite_count') or 0,
                sphinx_id=get_sphinx_id(tw.get("id")),
                content_hash=get_md5_text(tw.get("full_text"))

            )
        except Exception as e:
            print(e)
