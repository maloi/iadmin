from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import LdapUser
from .forms import LdapUserForm
from .utils import timestamp2date, debug
from iapp_group.models import LdapGroup


class UserList(ListView):
    model = LdapUser


class UserCreate(CreateView):
    model = LdapUser


class UserUpdate(UpdateView):
    model = LdapUser
    form_class = LdapUserForm

    def get_initial(self):
        return { 'deIappBirthday': timestamp2date(self.object.deIappBirthday) }

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk': self.request.POST['uid']})

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['userGroups'] = LdapGroup.objects.filter(memberUid__contains=context['object'].uid)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        userGroups = self.request.POST.getlist('userGroups')
        userGroups = [g for g in userGroups if g] # filter empty strings
        self.object.save(userGroups=userGroups)
        return redirect(self.get_success_url())


class UserDetail(DetailView):
    model = LdapUser

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['user_groups'] = LdapGroup.objects.filter(memberUid__contains=context['object'].uid)
        return context

