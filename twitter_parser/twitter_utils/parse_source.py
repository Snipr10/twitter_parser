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
        self.session, self.errors = self._validate_session(email, username, password, session, proxy_url,  **kwargs)
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


async def _search_source(source):
    import asyncio
    from twscrape import API, gather
    api = API()
    try:
        user_id = int(source)
    except Exception:
        user_id = (await api.user_by_login("noah")).id
    res = await gather(api.user_tweets(user_id, limit=20))
    return res


def search_by_source(source):
    res = None
    errors = []
    try:
        res = asyncio.run(_search_source(source))

    except Exception as e:
        print(e)
        errors.append(e)
    return res



if __name__ == '__main__':
    search_by_source("Serhio62472993")
