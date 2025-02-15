import hashlib
import json

from core.models import User, Post

from dateutil.parser import parse
import pika

from twitter_parser.settings import rmq_settings, FIRST_DATE


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
    sphinx_ids= []
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
                    logo=us.get('profile_banner_url'),


            )
        except Exception as e:
            print(e)
    for tw in res_tw:
        print(parse(tw.get("created_at")), tw.get("id_str"))
        try:
            created_date = parse(tw.get("created_at"))
            print("FIRST_DATE")
            if created_date < FIRST_DATE:
                continue

            print("created_date < FIRST_DATE")
            sphinx_id = get_sphinx_id(tw.get("id_str"))
            sphinx_ids.append(sphinx_id)
            Post.objects.create(
                id=tw.get("id_str"),
                from_id=tw.get('user_id_str'),
                owner_sphinx_id=get_sphinx_id(tw.get("user_id_str")),
                content=tw.get("full_text"),
                repost_of=bool(tw.get('retweeted')),
                created_date=created_date,
                viewed=tw.get('ext_views', {}).get("count") or 0,
                comments=tw.get('retweet_count') or 0,
                reposts=tw.get('reply_count') or 0,
                likes=tw.get('favorite_count') or 0,
                sphinx_id=sphinx_id,
                content_hash=get_md5_text(tw.get("full_text"))

            )
        except Exception as e:
            print(e)

    try:
        print(sphinx_ids)
        parameters = pika.URLParameters(rmq_settings)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for sphinx_id in sphinx_ids:
            print(f"{sphinx_id} added")

            rmq_json_data = {
                "id": str(sphinx_id),
                "network_id": 2
            }
            channel.basic_publish(exchange='',
                                  routing_key='post_index',
                                  body=json.dumps(rmq_json_data))
        channel.close()
    except Exception as e:
        print(f"RMQ basic_publish {e}")

def save_new_flow(res):
    users = []
    sphinx_ids= []

    for r in res:
        try:
            try:
                print("FIRST_DATE")
                if r.date < FIRST_DATE:
                    continue
            except Exception:
                pass
            print("created_date < FIRST_DATE")
            sphinx_id = get_sphinx_id(r.conversationIdStr)
            sphinx_ids.append(sphinx_id)
            Post.objects.create(
                id=r.id,
                from_id=r.user.id,
                owner_sphinx_id=get_sphinx_id(r.user.id),
                content=r.rawContent,
                repost_of=bool(r.retweetedTweet),
                created_date=r.date,
                viewed=r.viewCount or 0,
                comments=r.replyCount  or 0,
                reposts=r.retweetCount or 0,
                likes=r.likeCount or 0,
                sphinx_id=sphinx_id,
                content_hash=get_md5_text(r.rawContent)

            )
        except Exception as e:
            print(e)
        try:
            User.objects.create(
                id=r.user.id,
                sphinx_id=get_sphinx_id(r.user.id),
                name=r.user.displayname,
                screen_name=r.user.username,
                url=r.user.url or "",
                followers=r.user.followersCount or 0,
                district=0,
                friends=r.user.friendsCount or 0,
                created_date=r.user.created,
                logo=r.user.profileImageUrl,

            )
        except Exception as e:
            print(e)

    try:
        print(sphinx_ids)
        parameters = pika.URLParameters(rmq_settings)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for sphinx_id in sphinx_ids:
            print(f"{sphinx_id} added")

            rmq_json_data = {
                "id": str(sphinx_id),
                "network_id": 2
            }
            channel.basic_publish(exchange='',
                                  routing_key='post_index',
                                  body=json.dumps(rmq_json_data))
        channel.close()
    except Exception as e:
        print(f"RMQ basic_publish {e}")