import multiprocessing
import random
import time

import threading


import os

import random

BOT = None

Task = []


def new_process_key(i, special_group=False):
    for i in range(2):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_keyword_while, args=(special_group, ))
        x.start()


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
            start_parsing_account_source()
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
    print(1)
    import django

    django.setup()

    futures = []
    #
    # x = threading.Thread(target=update_, args=(0,))
    # x.start()
    from core.models import Account, Keyword, Sources, SourcesItems, AllProxy

