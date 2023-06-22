import pytz
from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import now


class Account(models.Model):
    login = models.CharField(default='', max_length=200)
    password = models.CharField(default='', max_length=200)
    email = models.CharField(default='', max_length=200)
    email_password = models.CharField(default='', max_length=200)
    taken = models.BooleanField(default=False)
    is_active = models.IntegerField(default=0)
    start_parsing = models.DateTimeField(default=now)
    last_parsing = models.DateTimeField(default=now)
    proxy_id = models.CharField(max_length=256)

    class Meta:
        db_table = 'prsr_parser_tw_accounts'


class AllProxy(models.Model):
    ip = models.CharField(max_length=256)
    port = models.IntegerField()
    login = models.CharField(max_length=256)
    proxy_password = models.CharField(max_length=256)
    last_used = models.DateTimeField(null=True, blank=True)
    last_used_y = models.DateTimeField(null=True, blank=True)
    failed = models.IntegerField()
    errors = models.IntegerField()
    foregin = models.IntegerField()
    banned_fb = models.IntegerField()
    banned_y = models.IntegerField()
    banned_tw = models.IntegerField()
    valid_untill = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=256, null=True, blank=True)
    v6 = models.IntegerField()
    last_modified = models.DateTimeField(null=True, blank=True)
    checking = models.BooleanField()

    class Meta:
        db_table = 'prsr_parser_proxy'

#
#
# class Post(models.Model):
#     id = models.IntegerField(primary_key=True)
#     user_id = models.IntegerField(null=True, blank=True)
#     group_id = models.IntegerField()
#     found_date = models.DateField(auto_now_add=True)
#     repost_from = models.IntegerField(null=True, blank=True)
#     created_date = models.DateTimeField(null=True, blank=True)
#     likes_count = models.IntegerField(default=0, null=True, blank=True)
#     comments_count = models.IntegerField(default=0, null=True, blank=True)
#     repost_count = models.IntegerField(default=-1, null=True, blank=True)
#     # repost_count = models.IntegerField(default=0, null=True, blank=True)
#
#     trust = models.IntegerField(null=True, blank=True)
#     sphinx_id = models.IntegerField(null=True, blank=True)
#     updated = models.DateField(null=True, blank=True)
#     last_modified = models.DateTimeField(default=now)
#     content_hash = models.CharField(max_length=32, null=True, blank=True)
#     taken = models.IntegerField(default=0)
#     url = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_posts'
#
#
# class PostContent(models.Model):
#     post_id = models.IntegerField(primary_key=True)
#     content = models.TextField(null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_posts_content'
#
#
# class User(models.Model):
#     id = models.IntegerField(primary_key=True)
#     sphinx_id = models.IntegerField(default=0)
#     screen_name = models.CharField(max_length=255)
#     logo = models.CharField(max_length=255)
#     url = models.CharField(max_length=255, null=True, blank=True)
#     name = models.CharField(max_length=255)
#     sex = models.IntegerField(default=0)
#     bdate = models.DateField(null=True, blank=True)
#     followers = models.IntegerField(default=0, null=True, blank=True)
#     last_modify = models.DateTimeField()
#     username = models.CharField(max_length=255)
#     last_modified = models.DateTimeField(default=now)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_users'
#
#
# class UserExt(models.Model):
#     id = models.IntegerField(primary_key=True)
#     city = models.CharField(max_length=255)
#     home_town = models.CharField(max_length=255)
#     education = models.TextField()
#     job = models.TextField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_users_ext'
#
#
# class Comment(models.Model):
#     id = models.IntegerField(primary_key=True)
#     user_id = models.IntegerField()
#     post_id = models.IntegerField()
#     root_comment_id = models.IntegerField()
#     created_date = models.DateTimeField()
#     likes = models.IntegerField(default=0)
#     trust = models.IntegerField(null=True, blank=True)
#     # last_modified = models.DateTimeField(default=now)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_comments'
#
#
# class CommentContext(models.Model):
#     id = models.IntegerField(primary_key=True)
#     content = models.TextField()
#     # last_modified = models.DateTimeField(default=now)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_comment_content'
#
#
# # TODO add id
# class CommentLike(models.Model):
#     comment_id = models.IntegerField()
#     post_id = models.IntegerField()
#     user_id = models.IntegerField()
#     created_date = models.DateTimeField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_comment_likes'
#
#
# # TODO add id
# class Likes(models.Model):
#     post_id = models.IntegerField()
#     user_id = models.IntegerField()
#     created_date = models.DateTimeField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_likes'
#
#
# class Photo(models.Model):
#     id = models.IntegerField(primary_key=True)
#     href = models.CharField(max_length=512)
#     # last_modified = models.DateTimeField(default=now)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_photos'
#
# # ???
# class PostPhoto(models.Model):
#     post_id = models.IntegerField()
#     photo_id = models.IntegerField(primary_key=True)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_posts_photos'
#
#
# class PostTrust(models.Model):
#     post_id = models.IntegerField(primary_key=True)
#     trustword_id = models.IntegerField()
#     trust = models.IntegerField()
#     modify_date = models.DateTimeField()
#     modify_by = models.IntegerField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_post_trust'
#
#
# # TODO add id
# class Repost(models.Model):
#     post_id = models.IntegerField()
#     user_id = models.IntegerField()
#     created_date = models.DateTimeField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_reposts'
#
#
# # TODO add id
# class Friends(models.Model):
#     friend_id = models.IntegerField()
#     user_id = models.IntegerField()
#     created_date = models.DateTimeField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_users_friends'
#
#
class Sources(models.Model):
    uid = models.IntegerField(default=0)
    published = models.IntegerField(default=1)
    status = models.BooleanField(default=0)
    type = models.CharField(default="profiles", max_length=4096)
    # retro = models.DateField(null=True, blank=True)
    retro_max = models.DateField(null=True, blank=True)
    networks = models.IntegerField(default=0)
    # last_modify = models.DateTimeField(null=True, blank=True)
    # links_modify = models.DateTimeField(null=True, blank=True)
    # n2_modify = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=1)
    linking = models.BooleanField(default=0)
    sources = models.IntegerField(default=15)
    profiles = models.IntegerField(default=15)
    stats_params = models.CharField(null=True, blank=True, max_length=4096)

    class Meta:
        db_table = 'prsr_parser_sources'

#
# class SourcesSpecial(models.Model):
#     source_id = models.IntegerField()
#     keyword_id = models.IntegerField()
#     source_item_id = models.IntegerField()
#
#     class Meta:
#         db_table = 'prsr_parser_source_special'
#
#
class SourcesItems(models.Model):
    source_id = models.IntegerField()
    network_id = models.IntegerField(default=0)
    type = models.IntegerField(default=1)
    data = models.CharField(default='', max_length=4096)
    last_modified = models.DateTimeField(null=True, blank=True)
    reindexed = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=0)
    reindexing = models.BooleanField(default=0)
    disabled = models.BooleanField(default=0)
    forced = models.BooleanField(default=0)

    class Meta:
        db_table = 'prsr_parser_source_items'

#
# class SourcesAccountsItems(models.Model):
#     source_id = models.IntegerField()
#     account_id = models.IntegerField()
#
#     class Meta:
#         db_table = 'prsr_parser_fb_account_source'
#
#
class Keyword(models.Model):
    id = models.IntegerField(primary_key=True)
    network_id = models.IntegerField(default=0)
    keyword = models.CharField(default='', max_length=4096)
    enabled = models.IntegerField(default=0)
    # created_date = models.DateTimeField(null=True, blank=True)
    # modified_date = models.DateTimeField(null=True, blank=True)
    # depth = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=0)
    reindexing = models.BooleanField(default=0)
    forced = models.BooleanField(default=0)

    class Meta:
        db_table = 'prsr_parser_keywords'
#

class KeywordSource(models.Model):
    keyword_id = models.IntegerField(primary_key=True)
    source_id = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_source_keywords'


# class Account(models.Model):
#     login = models.CharField(default='', max_length=200)
#     password = models.CharField(default='', max_length=200)
#     available = models.BooleanField(default=True)
#     availability_check = models.DateTimeField(null=True, blank=True)
#     banned = models.BooleanField(default=False)
#     taken = models.BooleanField(default=False)
#     cookie = models.CharField(default='', max_length=200)
#     proxy_id = models.CharField(max_length=256)
#     start_parsing = models.DateTimeField(null=True, blank=True)
#     last_parsing = models.DateTimeField(null=True, blank=True)
#     error = models.CharField(default='', max_length=1000)
#     special_group = models.IntegerField(default=0)
#     is_join_group = models.IntegerField(default=0)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_account'
#
#

#
#
# class WorkCred(models.Model):
#     account_id = models.IntegerField()
#     proxy_id = models.IntegerField()
#     in_progress = models.BooleanField(default=False)
#     start_parsing = models.DateTimeField(null=True, blank=True)
#     last_parsing = models.DateTimeField(null=True, blank=True)
#     locked = models.BooleanField(default=False)
#
#     class Meta:
#         db_table = 'prsr_parser_fb_worker_cerd'
#
#
#
#
#
#
# class Test(models.Model):
#     class Meta:
#         unique_together = (('key1', 'key2'),)
#
#     key1 = models.IntegerField()
#     key2 = models.IntegerField()
#
#
# # class Test1(models.Model):
# #     class Meta:
# #         unique_together = (('key1', 'key2'),)
# #         db_table = 'core_test1'
# #
# #     key1 = models.IntegerField()
# #     key2 = models.IntegerField()
