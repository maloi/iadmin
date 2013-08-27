from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import LdapGroup
from iapp_user.models import LdapUser
from iapp_user.utils import debug, get_or_none

class GroupList(ListView):
    model = LdapGroup

class GroupCreate(CreateView):
    model = LdapGroup

class GroupUpdate(UpdateView):
    model = LdapGroup

    def get_initial(self):
        sortedMembers = sorted(self.object.memberUid)
        sortedMembersDict = []
        for member in sortedMembers:
            m = get_or_none(LdapUser, uid=member)
            if m:
              sortedMembersDict.append({'cn': m.cn, 'uid': member})
        return { 'memberUid': sortedMembersDict }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        members = self.object.memberUid
        invalidMembers = []
        for member in members:
            m = get_or_none(LdapUser, uid=member)
            if not m:
              invalidMembers.append(member)
        context['invalidMembers'] = sorted(invalidMembers)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        memberUid = self.request.POST.getlist('memberUid')
        self.object.memberUid =  [m for m in memberUid if m] # filter empty strings
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('group_detail', kwargs={'pk': self.request.POST['cn']})

class GroupDetail(DetailView):
    model = LdapGroup


