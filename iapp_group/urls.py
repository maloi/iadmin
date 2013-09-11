from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import GroupList, GroupCreate, GroupDetail, GroupUpdate, ajax_group_autocomplete


urlpatterns = patterns('',
    url(r'^$', login_required(GroupList.as_view()), name='group_list'),
    url(r'^detail/(?P<pk>[-_\w\W]+)/$', login_required(GroupDetail.as_view()), name='group_detail'),
    url(r'^add/$', login_required(GroupCreate.as_view()), name='group_add'),
    url(r'^edit/(?P<pk>[-_\w\W]+)/$', login_required(GroupUpdate.as_view()), name='group_edit'),
    url(r'^ajax/autocomplete/$', ajax_group_autocomplete, name='ajax_group_autocomplete'),
)
