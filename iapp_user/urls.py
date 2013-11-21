from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import UserList, UserCreate, UserDetail, UserUpdate, ajax_user_autocomplete, delete_user, undelete_user, FormerUserList
from .models import LdapUser
from iapp_admin.decorators import admin_required


urlpatterns = patterns('',
    url(r'^$',
        login_required(UserList.as_view()),
        name='user_list'
    ),
    url(r'^former_users/$',
        admin_required(login_required(FormerUserList.as_view())),
        name='former_user_list'
    ),
    url(r'^detail/(?P<pk>[-\w]+)/$',
        login_required(UserDetail.as_view()),
        name='user_detail'
    ),
    url(r'^add/$',
        admin_required(login_required(UserCreate.as_view())),
        name='user_add'
    ),
    url(r'^edit/(?P<pk>[-\w]+)/$',
        admin_required(login_required(UserUpdate.as_view())),
        name='user_edit'
    ),
    url(r'^delete/(?P<pk>[-\w]+)/$',
        admin_required(login_required(delete_user)),
        name='user_delete'
    ),
    url(r'^undelete/(?P<uidNumber>[-\w]+)/$',
        admin_required(login_required(undelete_user)),
        name='user_undelete'
    ),
    url(r'^ajax/autocomplete/$',
        ajax_user_autocomplete,
        name='ajax_user_autocomplete'
    ),
)
