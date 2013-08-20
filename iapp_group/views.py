from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import LdapGroup

class GroupList(ListView):
    model = LdapGroup

class GroupCreate(CreateView):
    model = LdapGroup

class GroupUpdate(UpdateView):
    model = LdapGroup

class GroupDetail(DetailView):
    model = LdapGroup
