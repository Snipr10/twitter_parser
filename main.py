import asyncio
import base64
import datetime
import hashlib
import json
import multiprocessing
import time

import threading

import os

import random

from asgiref.sync import sync_to_async
from django.db.models import Q, F
from twscrape import API, gather

db_api = API()
BOT = None

Task = []


async def delete_inactive():
    await db_api.pool.delete_inactive()


async def add_accounts(login, password, email, email_password, cookies, proxy_url):
    if cookies:
        await db_api.pool.add_account(login,
                                      password,
                                      email,
                                      email_password,
                                      cookies=str(cookies),
                                      proxy=proxy_url,

                                      )
    else:
        await db_api.pool.add_account(login,
                                      password,
                                      email,
                                      email_password,
                                      proxy=proxy_url,
                                      )


async def get_active_accounts():
    return [user.get("username") for user in await db_api.pool.accounts_info()]


async def async_activate_accounts():
    await db_api.pool.login_all()


def activate_accounts():
    asyncio.run(delete_inactive())

    print(111)
    usernames = asyncio.run(get_active_accounts())
    print(112)

    for account in Account.objects.filter(~Q(login__in=usernames)).filter(is_active__lt=20).exclude(
            proxy_id__isnull=True):

        print(account)
        try:
            try:

                cookc = base64.b64decode(account.auth_data)
                cookc = str(cookc)
                cookc = cookc.replace('\\"', '').replace('\\', '')
                cookc = cookc[:cookc.rfind("]") + 1]

                cookies = ''
                for i in range(len(cookc)):
                    try:
                        cookies = json.loads(cookc[i:])
                        break
                    except Exception:
                        pass
            except Exception:
                cookies = None
            proxy = models.AllProxy.objects.filter(id=account.proxy_id).first()
            print(4)

            proxy_url = f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}"
            usernames = asyncio.run(add_accounts(account.login,
                                                 account.password,
                                                 account.email,
                                                 account.email_password, cookies, proxy_url))

        except Exception as e:
            print(e)
            pass
    asyncio.run(async_activate_accounts())

    Account.objects.filter(~Q(login__in=usernames)).filter(is_active__lt=20).update(is_active=F('is_active') + 1)


def new_process_key(i, special_group=False):
    start_parsing_by_keyword_while(special_group)


def start_parsing_by_keyword_while(special_group=False):
    while True:
        try:
            start_parsing_by_keyword(special_group)
            time.sleep(15 * 60)

        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def new_process_source(i, special_group=False):
    for i in range(1):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_source_while, args=(special_group,))
        x.start()


def new_process_account_item(i):
    x = multiprocessing.Process(target=start_parsing_account_source_while, args=())
    x.start()


def start_parsing_by_source_while(special_group=False):
    print(special_group)
    while True:
        try:
            start_parsing_by_source(special_group)
            time.sleep(10 * 60)
        except Exception as e:
            print(e)
            time.sleep(10 * 60)


def start_parsing_account_source_while():
    print("start_parsing_account_source_while")
    while True:
        try:
            start_parsing_account_source(special_group=False)
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


async def _search_key(key):
    print("key 1")
    res = list(await gather(db_api.search(key, limit=500)))
    print("key2")
    return res


async def _search_source(source):
    print(2)

    try:
        user_id = int(source)
    except Exception:
        user_id = (await db_api.user_by_login(source)).id
    print(3)

    res = await gather(db_api.user_tweets(user_id, limit=100))
    print(4)
    print(res)
    return res


if __name__ == '__main__':

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitter_parser.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print(21)
    import django

    django.setup()

    futures = []

    from twitter_parser.tasks import start_parsing_by_keyword, start_parsing_by_source
    from twitter_parser.settings import network_id

    from core.models import Account

    from core import models
    from django.db import connection

    #
    # print(1)
    # def get_sphinx_id(url):
    #     m = hashlib.md5()
    #     m.update(str(url).encode())
    #     return int(str(int(m.hexdigest(), 16))[:16])
    # print(2)
    # for owner in models.Post.objects.filter(owner_sphinx_id = 1420591320632896):
    #     print(owner.id)
    #     try:
    #         owner.owner_sphinx_id = get_sphinx_id(owner.from_id)
    #         owner.save(update_fields=["owner_sphinx_id"])
    #     except Exception as e:
    #         print(e)
    #     django.db.close_old_connections()

    #
    print(5)
    activate_accounts()
    #
    for i in range(2):
        time.sleep(10)
        print("thread new_process_source " + str(i))
        x = threading.Thread(target=new_process_source, args=(i, True,))
        x.start()

    for i in range(2):
        print("thread new_process_source " + str(i))
        x = threading.Thread(target=new_process_source, args=(i, False,))
        x.start()
        time.sleep(10)

    for i in range(2):
        print("thread new_process_key " + str(i))
        x = threading.Thread(target=new_process_key, args=(i,))
        x.start()
        time.sleep(10)

    i = 1
    while True:

        i += 1
        try:
            with connection.cursor() as cursor:
                query = """
                      UPDATE `prsr_parser_keywords` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 2 AND `last_modified` = '0000-00-00 00:00:00' AND `disabled` = 0;
                      """
                cursor.execute(query)
        except Exception as e:
            print(e)
        try:
            with connection.cursor() as cursor:
                query = """
                      UPDATE `prsr_parser_source_items` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 2 AND `disabled` = 0 AND `last_modified` = '0000-00-00 00:00:00';
                      """
                cursor.execute(query)
        except Exception as e:
            print(e)
        try:
            models.Keyword.objects.filter(last_modified__isnull=True).update(last_modified=datetime.date(2000, 1, 1))
            models.Keyword.objects.filter(last_modified__lte=datetime.date(2000, 1, 1)).update(
                last_modified=datetime.date(2000, 1, 1))

            print("update Keyword")
            # models.Keyword.objects.raw(
            #     f"UPDATE `prsr_parser_keywords` SET `last_modified` = `2000-01-01 00:00:00` WHERE `network_id` = `{network_id}` and `last_modified` IS NULL")
        #
        except Exception as e:
            print(e)
        try:
            if i % 10 == 0:
                try:
                    models.Keyword.objects.filter(network_id=network_id, taken=1).update(taken=0)
                except Exception as e:
                    print(e)
                try:
                    models.SourcesItems.objects.filter(network_id=network_id, taken=1).update(taken=0)
                except Exception as e:
                    print(e)
                i = 0
            if i % 1000 == 0:
                activate_accounts()
        except Exception as e:
            print(e)
        time.sleep(180)
