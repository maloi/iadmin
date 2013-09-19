from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import LdapMaillist
from .forms import LdapMaillistForm
from iapp_user.models import LdapUser
from iapp_user.utils import debug, get_or_none

class MaillistList(ListView):
    model = LdapMaillist

class MaillistCreate(CreateView):
    model = LdapMaillist
    form_class = LdapMaillistForm

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

class MaillistUpdate(UpdateView):
    model = LdapMaillist
    form_class = LdapMaillistForm

    def get_initial(self):
        owners = []
        for owner in self.object.owner:
            owners.append(LdapUser.objects.get(uid=owner.split('=')[1].split(',')[0]))
        members = []
        for member in self.object.member:
            members.append(LdapUser.objects.get(uid=member.split('=')[1].split(',')[0]))
        return { 'member': sorted(members, key=lambda member: member.cn),
                 'owner': sorted(owners, key=lambda owner: owner.cn)
               }

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

def _get_success_url(self):
    return reverse('maillist_detail', kwargs={'pk': self.request.POST['cn']})

def _form_valid(self, form):
    self.object = form.save(commit=False)
    member = self.request.POST.getlist('member')
    owner = self.request.POST.getlist('owner')
    rfc822MailMember = self.request.POST.getlist('rfc822MailMember')
    self.object.member = list(set(member)) # remove duplicates
    self.object.owner = list(set(owner)) # remove duplicates
    self.object.rfc822MailMember = list(set(rfc822MailMember)) # remove duplicates
    self.object.save()
    return redirect(self.get_success_url())

class MaillistDetail(DetailView):
    model = LdapMaillist

    def get_initial(self):
        owners = []
        for owner in self.object.owner:
            owners.append(LdapUser.objects.get(uid=owner.split('=')[1].split(',')[0]))
        members = []
        for member in self.object.member:
            members.append(LdapUser.objects.get(uid=member.split('=')[1].split(',')[0]))
        return { 'member': sorted(members, key=lambda member: member.cn),
                 'owner': sorted(owners, key=lambda owner: owner.cn)
               }
            