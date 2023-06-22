import datetime
import hashlib


def find_value(html, key, num_sep_chars=1, separator='"'):
    start_pos = html.find(key)
    if start_pos == -1:
        return None
    start_pos += len(key) + num_sep_chars
    end_pos = html.find(separator, start_pos)
    return html[start_pos:end_pos]


def get_sphinx_id(id, group_id):
    m = hashlib.md5()
    m.update(('https://m.facebook.com/story.php?story_fbid={}&id={}'.format(id, group_id)).encode())
    return int(str(int(m.hexdigest(), 16))[:16])


def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())


def update_time_timezone(my_time):
    return my_time + datetime.timedelta(hours=3)


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest(), 16))[:16])