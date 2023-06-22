from django.db.models import Q

from django.utils import timezone
from datetime import timedelta

from core import models
from twitter_parser.utils.find_data import update_time_timezone


def get_session():
    account = models.Account.objects.filter(Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
            timezone.localtime()) - timedelta(minutes=15)), taken=False, is_active__lte=10, proxy_id__isnull=False
                                       ).order_by('last_parsing').first()

    if account is None:
        return None, None
    try:
        account.taken = True
        account.start_parsing = update_time_timezone(timezone.now())
        account.last_parsing = update_time_timezone(timezone.now())
        account.save()
        proxy = models.AllProxy.objects.filter(id=account.proxy_id).first()
        if proxy is None:
            account.taken = False
            account.proxy_id = None
            account.save()
            return None, None
        proxy_url = f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}"

        return account, proxy_url
    except Exception as e:
        print(e)
        account.banned = True
        account.save()
        return None, None
