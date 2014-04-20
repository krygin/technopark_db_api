from django.conf.urls import patterns, include, url

from django.contrib import admin
from technopark_db_api_app.views import post
from technopark_db_api_app.views import thread
from technopark_db_api_app.views import user
from technopark_db_api_app.views import forum
from technopark_db_api_app.views import system
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'technopark_db_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^db/api/clear/$', system.clear),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^db/api/user/create/$', user.create),
    url(r'^db/api/user/follow/$', user.follow),
    url(r'^db/api/user/unfollow/$', user.unfollow),
    url(r'^db/api/user/details/$', user.details),
    url(r'^db/api/user/listFollowers/$', user.listFollowers),
    url(r'^db/api/user/listFollowing/$', user.listFollowing),
    url(r'^db/api/user/updateProfile/$', user.updateProfile),
    url(r'^db/api/user/listPosts/$', user.listPosts),



    url(r'^db/api/forum/create/$', forum.create),
    url(r'^db/api/forum/details/$', forum.details),
    url(r'^db/api/forum/listPosts/$', forum.listPosts),
    url(r'^db/api/forum/listThreads/$', forum.listThreads),
    url(r'^db/api/forum/listUsers/$', forum.listUsers),


    url(r'^db/api/thread/create/$', thread.create),
    url(r'^db/api/thread/close/$', thread.close),
    url(r'^db/api/thread/open/$', thread.open),
    url(r'^db/api/thread/remove/$', thread.remove),
    url(r'^db/api/thread/restore/$', thread.restore),
    url(r'^db/api/thread/vote/$', thread.vote),
    url(r'^db/api/thread/subscribe/$', thread.subscribe),
    url(r'^db/api/thread/unsubscribe/$', thread.unsubscribe),
    url(r'^db/api/thread/update/$', thread.update),
    url(r'^db/api/thread/details/$', thread.details),
    url(r'^db/api/thread/listPosts/$', thread.listPosts),
    url(r'^db/api/thread/list/$', thread.list),

    url(r'^db/api/post/create/$', post.create),
    url(r'^db/api/post/details/$', post.details),
    url(r'^db/api/post/remove/$', post.remove),
    url(r'^db/api/post/restore/$', post.restore),
    url(r'^db/api/post/update/$', post.update),
    url(r'^db/api/post/vote/$', post.vote),
    url(r'^db/api/post/list/$', post.list),
)
