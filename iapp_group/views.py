from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.utils import simplejson

from .models import LdapGroup
from .forms import LdapGroupForm
from iapp_user.models import LdapUser
from iapp_user.utils import debug, get_or_none

class GroupList(ListView):
    model = LdapGroup

class GroupCreate(CreateView):
    model = LdapGroup
    form_class = LdapGroupForm

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

class GroupUpdate(UpdateView):
    model = LdapGroup
    form_class = LdapGroupForm

    def get_initial(self):
        members = []
        for member in self.object.memberUid:
            m = get_or_none(LdapUser, uid=member)
            if m:
              members.append({'cn': m.cn, 'uid': member})
        return { 'memberUid': sorted(members, key=lambda member: member['cn']) }

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
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

def _get_success_url(self):
    return reverse('group_detail', kwargs={'pk': self.request.POST['cn']})

def _form_valid(self, form):
    self.object = form.save(commit=False)
    memberUid = self.request.POST.getlist('memberUid')
    self.object.memberUid = list(set(memberUid)) # remove duplicates
    self.object.save()
    return redirect(self.get_success_url())

class GroupDetail(DetailView):
    model = LdapGroup


def ajax_group_autocomplete(request):
    if 'term' in request.GET:
        groups = LdapGroup.objects.filter(
            cn__icontains=request.GET['term']
        )
        return HttpResponse( simplejson.dumps( [ {'value': g.cn, 'label': g.cn} for g in groups ] ) )
    return HttpResponse()
