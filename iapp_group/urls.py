from django.conf.urls import patterns, url
from .views import GroupList, GroupCreate, GroupDetail, GroupUpdate

urlpatterns = patterns('',
    url(r'^$', GroupList.as_view(), name='group_list'),
    url(r'^detail/(?P<pk>[-_\w\W]+)/$', GroupDetail.as_view(), name='group_detail'),
    url(r'^add/$', GroupCreate.as_view(), name='group_add'),
    url(r'^edit/(?P<pk>[-_\w\W]+)/$', GroupUpdate.as_view(), name='group_edit'),
)
