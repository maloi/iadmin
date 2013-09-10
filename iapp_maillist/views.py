from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import LdapMaillist
from iapp_user.models import LdapUser
from iapp_user.utils import debug

class MaillistList(ListView):
    model = LdapMaillist

class MaillistCreate(CreateView):
    model = LdapMaillist

class MaillistUpdate(UpdateView):
    model = LdapMaillist

    def get_initial(self):
        members = []
        for member in self.object.member:
            members.append(LdapUser.objects.get(uid=member.split('=')[1].split(',')[0]))
        return { 'member': sorted(members, key=lambda member: member.cn) }

    def form_invalid(self, form):
        debug(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        member = self.request.POST.getlist('member')
        debug(member)
        self.object.member =  [m for m in member if m] # filter empty strings
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('maillist_detail', kwargs={'pk': self.request.POST['cn']})


class MaillistDetail(DetailView):
    model = LdapMaillist
