import datetime
import hashlib
import multiprocessing
import time

import threading


import os

import random

BOT = None

Task = []


def new_process_key(i, special_group=False):
    for i in range(2):

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_keyword_while, args=(special_group, ))
        x.start()
        time.sleep(random.randint(10, 25))


def start_parsing_by_keyword_while(special_group=False):
    while True:
        try:
            start_parsing_by_keyword(special_group)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def new_process_source(i, special_group=False):
    for i in range(2):
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
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def start_parsing_account_source_while():
    print("start_parsing_account_source_while")
    while True:
        try:
            start_parsing_account_source(special_group=False)
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


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

    from core import models


    print(1)
    def get_sphinx_id(url):
        m = hashlib.md5()
        m.update(str(url).encode())
        return int(str(int(m.hexdigest(), 16))[:16])
    print(2)
    for owner in models.Post.objects.filter(owner_sphinx_id = 1420591320632896):
        print(owner.id)
        try:
            owner.owner_sphinx_id = get_sphinx_id(owner.from_id)
            owner.save(update_fields=["owner_sphinx_id"])
        except Exception as e:
            print(e)
        django.db.close_old_connections()

    #
    # for i in range(1):
    #     time.sleep(10)
    #     print("thread new_process_source " + str(i))
    #     x = threading.Thread(target=new_process_source, args=(i, True,))
    #     x.start()
    #
    for i in range(2):
        time.sleep(10)
        print("thread new_process_source " + str(i))
        x = threading.Thread(target=new_process_source, args=(i, False,))
        x.start()

    for i in range(2):
        print("thread new_process_key " + str(i))
        x = threading.Thread(target=new_process_key, args=(i, ))
        x.start()
        time.sleep(10)

    while True:
        try:
            models.Keyword.objects.filter(last_modified__isnull=True).update(last_modified=datetime.date(2000, 1, 1))
            models.Keyword.objects.filter(last_modified__lte=datetime.date(2000, 1, 1)).update(last_modified=datetime.date(2000, 1, 1))

            print("update Keyword")
            # models.Keyword.objects.raw(
            #     f"UPDATE `prsr_parser_keywords` SET `last_modified` = `2000-01-01 00:00:00` WHERE `network_id` = `{network_id}` and `last_modified` IS NULL")
        #
        except Exception as e:
            print(e)
        time.sleep(15)

