import asyncio
from asyncio import gather
from pathlib import Path

from httpx import AsyncClient
from orjson import orjson

from twitter.search import Search
from twitter.util import get_headers
from httpx import Client

from twitter_parser.twitter_utils.login import login


class MySearch(Search):
    def __init__(self, email: str = None, username: str = None, password: str = None, session: Client = None, proxy_url=None, **kwargs):
        self.proxy_url = proxy_url
        self.logger = self._init_logger(**kwargs)
        self.session, self.errors = self._validate_session(email, username, password, session, proxy_url,  **kwargs)
        self.api = 'https://api.twitter.com/2/search/adaptive.json?'
        self.save = kwargs.get('save', True)
        self.debug = kwargs.get('debug', 0)

    async def process(self, queries: tuple, config: dict, out: Path, **kwargs) -> list:
        proxies = {"http://": self.proxy_url, "https://": self.proxy_url}

        async with AsyncClient(headers=get_headers(self.session), proxies=proxies) as s:
            return await asyncio.gather(*(self.paginate(s, q, config, out, **kwargs) for q in queries))

    @classmethod
    def _validate_session(cls, *args, **kwargs):
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

        raise Exception('Session not authenticated. '
                        'Please use an authenticated session or remove the `session` argument and try again.')


async def _search_key(key):
    print("key 1")
    from main import db_api

    res = list( await gather(db_api.search(key, limit=500)))
    print("key2")
    return res


def search_by_key(key_word):
    res = None
    errors = []
    try:
        res = asyncio.run(_search_key(key_word))

    except Exception as e:
        print(e)
        errors.append(e)
    return res

if __name__ == '__main__':
    res = search_by_key("беглов")

