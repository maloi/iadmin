from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import UserList, UserCreate, UserDetail, UserUpdate


urlpatterns = patterns('',
    url(r'^$', login_required(UserList.as_view()), name='user_list'),
    url(r'^detail/(?P<pk>[-\w]+)/$', login_required(UserDetail.as_view()), name='user_detail'),
    url(r'^add/$', login_required(UserCreate.as_view()), name='user_add'),
    url(r'^edit/(?P<pk>[-\w]+)/$', login_required(UserUpdate.as_view()), name='user_edit'),
)
