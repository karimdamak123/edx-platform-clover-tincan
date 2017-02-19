"""
Base urls for the django_comment_client.
"""
from django.conf.urls import url, patterns

urlpatterns = patterns(
    'django_comment_client.base.views',

    url(r'upload$', 'upload', name='upload'),
    url(r'threads/(?P<thread_id>[\w\-]+)/update$', 'update_thread', name='update_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/reply$', 'create_comment', name='create_comment'),
    url(r'threads/(?P<thread_id>[\w\-]+)/delete', 'delete_thread', name='delete_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/upvote$', 'vote_for_thread', {'value': 'up'}, name='upvote_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/downvote$', 'vote_for_thread', {'value': 'down'}, name='downvote_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/flagAbuse$', 'flag_abuse_for_thread', name='flag_abuse_for_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/unFlagAbuse$', 'un_flag_abuse_for_thread', name='un_flag_abuse_for_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/unvote$', 'undo_vote_for_thread', name='undo_vote_for_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/pin$', 'pin_thread', name='pin_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/unpin$', 'un_pin_thread', name='un_pin_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/follow$', 'follow_thread', name='follow_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/unfollow$', 'unfollow_thread', name='unfollow_thread'),
    url(r'threads/(?P<thread_id>[\w\-]+)/close$', 'openclose_thread', name='openclose_thread'),
    url(r'comments/(?P<comment_id>[\w\-]+)/update$', 'update_comment', name='update_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/endorse$', 'endorse_comment', name='endorse_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/reply$', 'create_sub_comment', name='create_sub_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/delete$', 'delete_comment', name='delete_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/upvote$', 'vote_for_comment', {'value': 'up'}, name='upvote_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/downvote$', 'vote_for_comment', {'value': 'down'}, name='downvote_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/unvote$', 'undo_vote_for_comment', name='undo_vote_for_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/flagAbuse$', 'flag_abuse_for_comment', name='flag_abuse_for_comment'),
    url(r'comments/(?P<comment_id>[\w\-]+)/unFlagAbuse$', 'un_flag_abuse_for_comment', name='un_flag_abuse_for_comment'),
    url(r'^(?P<commentable_id>[\w\-.]+)/threads/create$', 'create_thread', name='create_thread'),
    url(r'^(?P<commentable_id>[\w\-.]+)/follow$', 'follow_commentable', name='follow_commentable'),
    url(r'^(?P<commentable_id>[\w\-.]+)/unfollow$', 'unfollow_commentable', name='unfollow_commentable'),
    url(r'users$', 'users', name='users'),
)
