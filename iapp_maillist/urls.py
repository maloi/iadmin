from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import MaillistList, MaillistCreate, MaillistDetail, MaillistUpdate


urlpatterns = patterns('',
    url(r'^$', login_required(MaillistList.as_view()), name='maillist_list'),
    url(r'^detail/(?P<pk>[-_\w\W]+)/$', login_required(MaillistDetail.as_view()), name='maillist_detail'),
    url(r'^add/$', login_required(MaillistCreate.as_view()), name='maillist_add'),
    url(r'^edit/(?P<pk>[-_\w\W]+)/$', login_required(MaillistUpdate.as_view()), name='maillist_edit'),
)
