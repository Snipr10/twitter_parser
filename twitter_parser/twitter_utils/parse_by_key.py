import asyncio
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


def search_by_key(username, password, email, email_password, proxy_url, key_word):
    res_tw = None
    res_us = None
    errors = []
    try:
        # email, username, password = "kemullinax70@hotmail.com", "queleraren39157", "2SmyGTeoRm"
        # proxy_url = "http://tools-admin_metamap_com:456f634698@193.142.249.56:30001"
        # email_password = 'Kerrie19701970'
        # email = 'kemullinax70@hotmail.com'

        search = MySearch(email, username, password, debug=True, proxy_url=proxy_url,
                          protonmail={'email': email, 'password': email_password})
        # search = Search(email, username, password, save=True, debug=1)
        errors = search.errors
        latest_results = search.run(
            limit=150,
            retries=2,
            queries=[
                {
                    'category': 'Latest',
                    'query': key_word
                }

            ],
        )
        res_tw = []
        res_us = []
        for r in latest_results[0]:
            try:
                post = r['content']['itemContent']['tweet_results']['result']['legacy']
                us = [r['content']['itemContent']['tweet_results']['result']['core']['user_results']['result'][
                          'legacy']]
                us[0]["id"] = post['user_id_str']
                res_tw.extend([r['content']['itemContent']['tweet_results']['result']['legacy']])
                res_us.extend(us)
            except Exception:
                pass
    except Exception as e:
        print(e)
        errors.append(e)
    return res_tw, res_us, errors

if __name__ == '__main__':
    search_by_key(None, None, None, None, None, "беглов")
