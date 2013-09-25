from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import MaillistList, MaillistCreate, MaillistDetail, MaillistUpdate, MaillistDelete
from .models import LdapMaillist
from iapp_admin.decorators import admin_required, owner_or_admin_required


urlpatterns = patterns('',
    url(r'^$',
        login_required(MaillistList.as_view()),
        name='maillist_list'
    ),
    url(r'^detail/(?P<pk>[-_\w\W]+)/$',
        login_required(MaillistDetail.as_view()),
        name='maillist_detail'
    ),
    url(r'^add/$',
        admin_required(login_required(MaillistCreate.as_view())),
        name='maillist_add'
    ),
    url(r'^edit/(?P<pk>[-_\w\W]+)/$',
        owner_or_admin_required(LdapMaillist, login_required(MaillistUpdate.as_view())),
        name='maillist_edit'
    ),
    url(r'^delete/(?P<pk>[-_\w\W]+)/$',
        login_required(MaillistDelete.as_view()),
        name='maillist_delete'
    ),
)
