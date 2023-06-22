import datetime
import json
import logging
import time
from datetime import timedelta
import random

import django.db
import requests
from django.db.models import Q
from django.utils import timezone
from concurrent.futures.thread import ThreadPoolExecutor

from core import models

from twitter_parser.settings import network_id, BEST_PROXY_KEY
from twitter_parser.twitter_utils.parse_by_key import search_by_key
from twitter_parser.twitter_utils.session import get_session
from twitter_parser.utils.find_data import update_time_timezone
from twitter_parser.utils.proxy import generate_proxy_session, check_facebook_url

logger = logging.getLogger(__file__)


def start_parsing_by_keyword(special_group=False):
    print("start_parsing_by_keyword")
    django.db.close_old_connections()

    select_sources = models.Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)
    print(f"select_sources {select_sources}")
    if not select_sources.exists():
        print(f"not select_sources special_group {special_group}")
        return
    key_source = models.KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))
    print(f"key_source {key_source}")

    key_word = models.Keyword.objects.filter(network_id=network_id, enabled=1,
                                             taken=0,

                                             id__in=list(key_source.values_list(
                                                 'keyword_id', flat=True))
                                             ).order_by('last_modified').first()
    print(f"key_word {key_word}")

    if key_word is not None:
        # print(f"{key_word} special_group {special_group}")
        select_source = select_sources.get(id=key_source.filter(keyword_id=key_word.id).first().source_id)
        last_update = key_word.last_modified
        time_ = select_source.sources
        print("time")
        print(time_)

        if last_update is None or (last_update + datetime.timedelta(minutes=time_) <
                                   update_time_timezone(timezone.localtime())):
            print("key_word")
            key_word.taken = 1
            key_word.save()
            try:
                print("get_session")
                account, proxy = get_session()
                if account:
                    print("search_by_key")

                    res_tw, res_us = search_by_key(account.login, account.password,account.email, account.email_password, proxy, key_word)
                else:
                    raise Exception("can not get_data")
            finally:
                django.db.close_old_connections()
                key_word.taken = 0
                key_word.save(update_fields=["taken"])
#
#
# def start_parsing_by_source(special_group=False):
#     print(1)
#     django.db.close_old_connections()
#
#     select_sources = models.Sources.objects.filter(
#         Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
#         status=1)
#     if not select_sources.exists():
#         print("not select_sources")
#
#         return
#     print(2)
#     source_special_in = list(models.SourcesSpecial.objects.all().values_list('source_item_id', flat=True))
#     source_special_in = [x for x in source_special_in if x is not None]
#     source_account_special_in = list(models.SourcesAccountsItems.objects.all().values_list('source_id', flat=True))
#     source_account_special_in = [x for x in source_account_special_in if x is not None]
#     print(3)
#     face_session, account = get_session(special_group)
#     if not face_session:
#         raise Exception("can not get_source")
#
#     if special_group:
#         sources_item = models.SourcesItems.objects.filter(network_id=network_id, disabled=0, taken=0,
#                                                           reindexing=1,
#                                                           id__in=source_special_in,
#                                                           last_modified__isnull=False,
#                                                           source_id__in=list(
#                                                               select_sources.values_list('id', flat=True))
#                                                           ).exclude(id__in=source_account_special_in).order_by(
#             'last_modified').first()
#         if sources_item is None:
#             sources_item = models.SourcesItems.objects.filter(network_id=network_id, disabled=0, taken=0,
#                                                               last_modified__isnull=False,
#                                                               id__in=source_special_in,
#                                                               source_id__in=list(
#                                                                   select_sources.values_list('id', flat=True))
#                                                               ).exclude(id__in=source_account_special_in).order_by(
#                 'last_modified').first()
#     else:
#         sources_item = models.SourcesItems.objects.filter(~Q(id__in=source_special_in),
#                                                           network_id=network_id, disabled=0, taken=0,
#                                                           reindexing=1,
#                                                           last_modified__isnull=False,
#                                                           source_id__in=list(
#                                                               select_sources.values_list('id', flat=True))
#                                                           ).exclude(id__in=source_account_special_in).order_by(
#             'last_modified').first()
#         if sources_item is None:
#             sources_item = models.SourcesItems.objects.filter(~Q(id__in=source_special_in),
#                                                               network_id=network_id, disabled=0, taken=0,
#                                                               last_modified__isnull=False,
#                                                               source_id__in=list(
#                                                                   select_sources.values_list('id', flat=True))
#                                                               ).exclude(id__in=source_account_special_in).order_by(
#                 'last_modified').first()
#     print(4)
#
#     if sources_item is not None:
#         print(sources_item)
#         select_source = select_sources.get(id=sources_item.source_id)
#         retro = select_source.retro
#
#         retro_date = datetime.datetime(retro.year, retro.month, retro.day)
#         last_modified = sources_item.last_modified
#         # try:
#         #     last_modified_up = datetime.datetime(last_modified.year, last_modified.month, last_modified.day,
#         #                                          last_modified.hour, last_modified.minute, last_modified.second)
#         #     if retro_date < last_modified_up:
#         #         retro_date = last_modified_up
#         # except Exception:
#         #     pass
#         sources_item.taken = 1
#         sources_item.save(update_fields=["taken"])
#         time_ = select_source.sources
#         print(5)
#
#         if last_modified is None or (last_modified + datetime.timedelta(minutes=time_) <
#                                      update_time_timezone(timezone.localtime())):
#             try:
#                 print(6)
#
#                 search_source(face_session, account, sources_item, retro_date)
#             finally:
#                 django.db.close_old_connections()
#                 sources_item.taken = 0
#                 sources_item.save(update_fields=["taken"])
#
#
# def start_first_update_posts():
#     pool_source = ThreadPoolExecutor(15)
#     print("start")
#     posts = models.Post.objects.filter(last_modified__lte=datetime.date(2000, 1, 1),
#                                        taken=0).order_by('found_date')[:100]
#     print("posts")
#     print(posts)
#     for post in posts:
#         post.taken = 1
#         post.save()
#         print(post.id)
#         try:
#             if post is not None:
#                 # todo get proxy
#                 # parallel_parse_post(post)
#                 pool_source.submit(parallel_parse_post, post)
#         except Exception as e:
#             logger.error(e)
#             print(e)
#             # try:
#             #     stop_proxy(proxy)
#             # except Exception as e:
#             #     logger.warning(e)
#             print('post bad')
#             post.taken = 0
#             post.save()
#
#
# def add_work_credential():
#     account_work_ids = models.WorkCred.objects.filter().values_list('account_id', flat=True)
#     account_work = models.Account.objects.filter(available=True, banned=False).exclude(id__in=account_work_ids)
#     for account in account_work:
#         check_accounts(account, attempt=0)
#
#
# def add_proxy():
#     print("update_proxy")
#     # key = models.Keys.objects.all().first().proxykey
#
#     new_proxy = requests.get(
#         "https://api.best-proxies.ru/proxylist.json?key=%s&twitter=1&type=http&speed=1" % BEST_PROXY_KEY,
#         timeout=60)
#
#     proxies = []
#     print("new_proxy.text")
#     print(new_proxy.text)
#     for proxy in json.loads(new_proxy.text):
#         ip = proxy['ip']
#         port = proxy['port']
#         print(ip)
#         print(port)
#         if not models.AllProxy.objects.filter(ip=ip, port=port).exists():
#             proxies.append(
#                 models.AllProxy(ip=ip, port=port, login="test", proxy_password="test", last_used=timezone.now(),
#                                 failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0, banned_tw=0,
#                                 valid_untill=timezone.now() + timedelta(days=3), v6=0, last_modified=timezone.now(),
#                                 checking=0
#
#                                 ))
#     models.AllProxy.objects.bulk_create(proxies, batch_size=200, ignore_conflicts=True)
#
#
# def update_proxy():
#     print("update_proxy")
#     # key = models.Keys.objects.all().first().proxykey
#     key = 'd73007770373106ac0256675c604bc22'
#
#     new_proxy = requests.get(
#         "https://api.best-proxies.ru/proxylist.json?key=%s&twitter=1&type=http,https&speed=1,2" % key,
#         timeout=60)
#
#     proxies = []
#     limit = 0
#     for proxy in json.loads(new_proxy.text):
#         host = proxy['ip']
#         port = proxy['port']
#         print(host)
#         print(port)
#         limit += 1
#         session = generate_proxy_session('test', 'test', host, port)
#         if not models.AllProxy.objects.filter(ip=host, port=port).exists():
#             if check_facebook_url(session):
#                 if port == '8080':
#                     if check_proxy_available_for_facebook(session):
#                         print('ad 8080 ' + str(host))
#                         proxies.append(models.AllProxy(ip=host, port=port, login="test", proxy_password="test",
#                                                        last_used=timezone.now(),
#                                                        failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0,
#                                                        banned_tw=0,
#                                                        valid_untill=timezone.now() + timedelta(days=3), v6=0,
#                                                        last_modified=timezone.now(),
#                                                        checking=0
#                                                        ))
#                         # models.Proxy.objects.create(host=host, port=port, login="test", password="test")
#                 else:
#                     proxies.append(models.AllProxy(ip=host, port=port, login="test", proxy_password="test",
#                                                    last_used=timezone.now(),
#                                                    failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0,
#                                                    banned_tw=0,
#                                                    valid_untill=timezone.now() + timedelta(days=3), v6=0,
#                                                    last_modified=timezone.now(),
#                                                    checking=0
#
#                                                    ))
#         if limit >= 20:
#             models.AllProxy.objects.bulk_create(proxies, batch_size=200, ignore_conflicts=True)
#             limit = 0
#             proxies = []
#
#
# def check_proxy_available_for_facebook(session):
#     try:
#         accounts = models.Account.objects.filter(banned=False).order_by('id')[:500]
#         account = random.choice(accounts)
#         # login = "+79910404158"
#         # password = "yBZHsBZHou761"
#         print(account.id)
#         response = session.post('https://m.facebook.com/login.php', data={
#             'email': account.login,
#             'pass': account.password,
#             # 'email': login,
#             # 'pass': password
#         }, allow_redirects=False, timeout=10)
#         start_page = session.get('https://www.facebook.com/', timeout=10)
#         print(start_page)
#         if 'login/?privacy_mutation_token' in start_page.url:
#             account.banned = True
#             account.save()
#             return check_proxy_available_for_facebook(session)
#         if 'checkpoint' in start_page:
#             account.available = False
#             account.save()
#         if 'checkpoint' not in start_page.url and '/login/device-based/regulr/' not in start_page.url:
#             print(str(account.id) + " ok")
#             return True
#     except Exception as e:
#         print(e)
#         pass
#     print(str(account.id) + " bad")
#     return False
#
#
# def check_not_available_accounts():
#     for account in models.Account.objects.filter().order_by("-id")[:500]:
#         if not models.WorkCred.objects.filter(account_id=account.id).exists():
#             check_accounts(account, attempt=0)
#
#
# def start_parsing_account_source():
#     while True:
#         try:
#             face_session, account = get_session(is_join=True)
#             if not account:
#                 print("not account")
#
#                 return
#
#             select_sources = models.Sources.objects.filter(
#                 Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
#                 status=1)
#             if not select_sources.exists():
#                 print("not select_sources")
#                 return
#             print(1)
#             source_account_special_in = list(
#                 models.SourcesAccountsItems.objects.filter(account_id=account.id).values_list('source_id', flat=True))
#             source_account_special_in = [x for x in source_account_special_in if x is not None]
#
#             sources_item = models.SourcesItems.objects.filter(network_id=network_id, disabled=0, taken=0,
#                                                               id__in=source_account_special_in,
#                                                               last_modified__isnull=False,
#                                                               source_id__in=list(
#                                                                   select_sources.values_list('id', flat=True))
#                                                               ).order_by('last_modified').first()
#             print(2)
#
#             if sources_item is None:
#                 account.last_parsing = update_time_timezone(timezone.localtime())
#                 account.taken = 0
#                 account.save()
#             print(3)
#
#             if sources_item is not None:
#                 select_source = select_sources.get(id=sources_item.source_id)
#                 retro = select_source.retro
#
#                 retro_date = datetime.datetime(retro.year, retro.month, retro.day)
#                 last_modified = sources_item.last_modified
#                 # try:
#                 #     last_modified_up = datetime.datetime(last_modified.year, last_modified.month, last_modified.day,
#                 #                                          last_modified.hour, last_modified.minute, last_modified.second)
#                 #     if retro_date < last_modified_up:
#                 #         retro_date = last_modified_up
#                 # except Exception:
#                 #     pass
#                 sources_item.taken = 1
#                 sources_item.save(update_fields=["taken"])
#                 time_ = select_source.sources
#                 print(4)
#
#                 if last_modified is None or (last_modified + datetime.timedelta(minutes=time_) <
#                                              update_time_timezone(timezone.localtime())):
#                     try:
#                         print("search_source")
#                         search_source(face_session, account, sources_item, retro_date)
#                     finally:
#                         django.db.close_old_connections()
#                         sources_item.taken = 0
#                         sources_item.save(update_fields=["taken"])
#                 else:
#                     account.last_parsing = update_time_timezone(timezone.localtime())
#                     account.taken = 0
#                     account.save()
#         except Exception as e:
#             print(e)
#             time.sleep(5 * 60)
