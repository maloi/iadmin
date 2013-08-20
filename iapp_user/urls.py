from django.conf.urls import patterns, url
from .views import UserList, UserCreate, UserDetail, UserUpdate

urlpatterns = patterns('',
    url(r'^$', UserList.as_view(), name='user_list'),
    url(r'^detail/(?P<pk>[-\w]+)/$', UserDetail.as_view(), name='user_detail'),
    url(r'^add/$', UserCreate.as_view(), name='user_add'),
    url(r'^edit/(?P<pk>[-\w]+)/$', UserUpdate.as_view(), name='user_edit'),
)
