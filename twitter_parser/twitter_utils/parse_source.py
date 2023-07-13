import asyncio
from pathlib import Path

import orjson
from tqdm.asyncio import tqdm_asyncio
from twitter.constants import RED, RESET
from twitter.scraper import Scraper

from httpx import Client, Limits, AsyncClient
from twitter.util import get_headers

from twitter_parser.twitter_utils.login import login


class MyScraper(Scraper):
    def __init__(self, email: str = None, username: str = None, password: str = None, session: Client = None, proxy_url=None, **kwargs):
        self.save = kwargs.get('save', True)
        self.debug = kwargs.get('debug', 0)
        self.pbar = kwargs.get('pbar', True)
        self.out = Path(kwargs.get('out', 'data'))
        self.guest = False
        self.logger = self._init_logger(**kwargs)
        self.session, self.errors = self._validate_session(email, username, password, session, proxy_url, **kwargs)
        self.proxy_url = proxy_url

    async def _process(self, operation: tuple, queries: list[dict], **kwargs):
        limits = Limits(max_connections=100, max_keepalive_connections=10)
        headers = self.session.headers if self.guest else get_headers(self.session)
        cookies = self.session.cookies
        async with AsyncClient(limits=limits, headers=headers, cookies=cookies, timeout=20,
                               proxies=self.proxy_url ) as c:
            tasks = (self._paginate(c, operation, **q, **kwargs) for q in queries)
            if self.pbar:
                return await tqdm_asyncio.gather(*tasks, desc=operation[-1])
            return await asyncio.gather(*tasks)

    def _validate_session(self, *args, **kwargs):
        email, username, password, session, proxy_url = args
        errors = []
        # validate credentials
        if all((email, username, password)):
            return login(email, username, password, proxy_url,  **kwargs)

        # invalid credentials, try validating session
        if session and all(session.cookies.get(c) for c in {'ct0', 'auth_token'}):
            return session, errors

        # invalid credentials and session
        cookies = kwargs.get('cookies')

        # try validating cookies dict
        if isinstance(cookies, dict) and all(cookies.get(c) for c in {'ct0', 'auth_token'}):
            _session = Client(cookies=cookies, follow_redirects=True)
            _session.headers.update(get_headers(_session))
            return _session, errors

        # try validating cookies from file
        if isinstance(cookies, str):
            _session = Client(cookies=orjson.loads(Path(cookies).read_bytes()), follow_redirects=True)
            _session.headers.update(get_headers(_session))
            return _session, errors

        # no session, credentials, or cookies provided. use guest session.
        if self.debug:
            self.logger.warning(f'{RED}This is a guest session, some endpoints cannot be accessed.{RESET}\n')
        self.guest = True
        return session, errors


def search_by_source(username, password, email, email_password, proxy_url, source):
    res_tw = None
    res_us = None
    errors = []
    try:
        # username, password = "visitant_YTs_", "tWi8uz70"
        # proxy_url = "http://tools-admin_metamap_com:456f634698@193.142.249.56:30001"
        # email_password = 'tWi8uz70'
        # email = 'suutjijao@hotmail.com'

        scraper = MyScraper(email, username, password, proxy_url=proxy_url, protonmail={'email': email, 'password': email_password})
        errors = scraper.errors
        try:
            user_ids = [int(source)]
        except Exception:
            user_ids = [scraper.users(['kaliningradru'])[0]['data']['user']['result']['rest_id']]

        latest_results = scraper.tweets(user_ids, limit=100)

        res_tw = []
        res_us = []
        for r in latest_results:
            try:
                for tw in r['data']['user']['result']['timeline_v2']['timeline']['instructions'][-1]['entries']:
                    try:
                        post_i = tw['content']
                        if post_i.get("itemContent") is None:
                            posts = post_i.get("items")
                        else:
                            posts = [post_i.get("itemContent")]
                        for post in posts:
                            try:
                                post = post['tweet_results']['result']['legacy']
                                us = [tw['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']]
                                us[0]["id"] = post['user_id_str']
                                res_tw.extend([post])
                                res_us.extend(us)
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return res_tw, res_us, errors


if __name__ == '__main__':
    search_by_source(None, None, None, None, None, "Serhio62472993")
