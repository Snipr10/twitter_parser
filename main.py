import multiprocessing
import random
import time

import threading


import os

import random

from twitter_parser.twitter_utils.parse_by_key import search_by_key

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


    # start_parsing_by_source_while(False)
    x = threading.Thread(target=new_process_account_item, args=(0, ))
    x.start()
    #
    # for i in range(1):
    #     time.sleep(10)
    #     print("thread new_process_source " + str(i))
    #     x = threading.Thread(target=new_process_source, args=(i, True,))
    #     x.start()
    #
    # for i in range(5):
    #     time.sleep(10)
    #     print("thread new_process_source " + str(i))
    #     x = threading.Thread(target=new_process_source, args=(i, False,))
    #     x.start()

    for i in range(2):
        time.sleep(10)
        print("thread new_process_key " + str(i))
        x = threading.Thread(target=new_process_key, args=(i, False,))
        x.start()

    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_key " + str(i))
    #     x = threading.Thread(target=new_process_key, args=(i, True,))
    #     x.start()

    # i = 1
    # while True:
    #     i += 1
    #     time.sleep(180)
    #     try:
    #         django.db.close_old_connections()
    #         try:
    #             Account.objects.filter(
    #                                    last_parsing__lte=update_time_timezone(
    #                                        timezone.now() - datetime.timedelta(minutes=60)),
    #                                    ).update(taken=0, banned=0)
    #         except Exception as e:
    #             print(e)
    #         try:
    #             if i % 10 == 0:
    #                 try:
    #                     Keyword.objects.filter(network_id=network_id, enabled=1, taken=1).update(taken=0)
    #                 except Exception as e:
    #                     print(e)
    #                 try:
    #                     SourcesItems.objects.filter(network_id=network_id, taken=1).update(taken=0)
    #                 except Exception as e:
    #                     print(e)
    #                 try:
    #                     SourcesItems.objects.filter(network_id=3, disabled=0, last_modified__isnull=True).update(
    #                         last_modified=datetime.datetime(2000, 1, 1))
    #                     SourcesItems.objects.filter(network_id=3, disabled=0,
    #                                                 last_modified__lte=datetime.datetime(1999, 1, 1)).update(
    #                         last_modified=datetime.datetime(2000, 1, 1))
    #                 except Exception as e:
    #                     print(e)
    #                 i = 0
    #         except Exception as e:
    #             print(e)
    #         try:
    #             select_sources = Sources.objects.filter(status=0)
    #             sources_item = SourcesItems.objects.filter(network_id=network_id, disabled=0, taken=0,
    #                                                        last_modified__isnull=False,
    #                                                        source_id__in=list(
    #                                                            select_sources.values_list('id', flat=True))
    #                                                        )
    #             sources_item.update(disabled=1)
    #         except Exception as e:
    #             print(e)
    #         try:
    #             accounts = Account.objects.filter(
    #                 last_parsing__lte=update_time_timezone(
    #                     timezone.now() - datetime.timedelta(minutes=60)),
    #             )
    #             proxies_set = set()
    #             for a in accounts:
    #                 proxies_set.add(a.proxy_id)
    #             proxies_list = list(proxies_set)
    #             print(f"proxies_list {proxies_list}")
    #             work_proxy = []
    #             work_proxy_ids = []
    #             proxy_candidates = AllProxy.objects.filter(port__in=[30001, 30011, 30010])
    #             for can in proxy_candidates:
    #                 try:
    #                     proxy_str = f"{can.login}:{can.proxy_password}@{can.ip}:{can.port}"
    #                     proxies = {'https': f'http://{proxy_str}'}
    #                     if requests.get("https://www.facebook.com/", proxies=proxies, timeout=10).ok:
    #                         work_proxy.append(can)
    #                         work_proxy_ids.append(can.id)
    #
    #                 except Exception as e:
    #                     print(f"{proxy_str} {e}")
    #             print(f"work_proxy {work_proxy}")
    #             print(f"work_proxy_ids {work_proxy_ids}")
    #
    #             exist_proxy = AllProxy.objects.filter(id__in=proxies_list)
    #             for e_p in exist_proxy:
    #                 try:
    #                     proxy_str = f"{e_p.login}:{e_p.proxy_password}@{e_p.ip}:{e_p.port}"
    #                     proxies = {'https': f'http://{proxy_str}'}
    #                     if requests.get("https://www.facebook.com/", proxies=proxies, timeout=10).ok:
    #                         work_proxy.append(e_p)
    #                         work_proxy_ids.append(e_p.id)
    #                 except Exception as e:
    #                     print(f"{proxy_str} {e}")
    #             print(f"work_proxy {work_proxy}")
    #             print(f"work_proxy_ids {work_proxy_ids}")
    #             for a in accounts:
    #                 if a.proxy_id not in work_proxy_ids:
    #                     a.proxy_id = random.choice(work_proxy_ids)
    #                     a.save(update_fields=["proxy_id"])
    #                     print(f"account {a}")
    #         except Exception as e:
    #             print(e)
    #     except Exception as e:
    #         print(e)


