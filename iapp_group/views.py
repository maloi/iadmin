from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.utils import simplejson

from .models import LdapGroup
from .forms import LdapGroupForm
from iapp_user.models import LdapUser
from iapp_user.utils import debug, get_or_none

class GroupList(ListView):
    model = LdapGroup
    
    def get_context_data(self, **kwargs):
        context = super(GroupList, self).get_context_data(**kwargs)
        context['groups'] = sorted(context['ldapgroup_list'], key=lambda ldapgroup: ldapgroup.cn)
        return context

class GroupCreate(CreateView):
    model = LdapGroup
    form_class = LdapGroupForm
    
    def get_initial(self):
        a_gid = LdapGroup.objects.all()
        min_gid = 20000
        max_gid = 30000
        act = 0
        for gid in a_gid:
            if gid.gidNumber > act and gid.gidNumber >= min_gid and gid.gidNumber <= max_gid:
                act = gid.gidNumber
        return { 'gidNumber' : act + 1 }

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

class GroupDelete(DeleteView):
    model = LdapGroup
    success_url = reverse_lazy('group_list')

class GroupUpdate(UpdateView):
    model = LdapGroup
    form_class = LdapGroupForm
    template_name_suffix = '_update_form'

    def get_initial(self):
        owners = []
        for owner in self.object.owner:
            owners.append(LdapUser.objects.get(uid=owner.split('=')[1].split(',')[0]))
        members = []
        for member in self.object.memberUid:
            m = get_or_none(LdapUser, uid=member)
            if m:
              members.append({'cn': m.cn, 'uid': member})
        return { 'memberUid': sorted(members, key=lambda member: member['cn']),
                    'owner': sorted(owners, key=lambda owner: owner.cn)
                    }

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
    owner = self.request.POST.getlist('owner')
    self.object.memberUid = list(set(memberUid)) # remove duplicates
    self.object.owner = list(set(owner)) # remove duplicates
    self.object.save()
    return redirect(self.get_success_url())

class GroupDetail(DetailView):
    model = LdapGroup
    
    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['owners'] = []
        for owner in self.object.owner:
            context['owners'].append(LdapUser.objects.get(uid=owner.split('=')[1].split(',')[0]))
        context['members'] = []
        for member in self.object.memberUid:
            context['members'].append(LdapUser.objects.get(uid=member))
        return context

def ajax_group_autocomplete(request):
    if 'term' in request.GET:
        groups = LdapGroup.objects.filter(
            cn__icontains=request.GET['term']
        )
        return HttpResponse( simplejson.dumps( [ {'value': g.cn, 'label': g.cn} for g in groups ] ) )
    return HttpResponse()
