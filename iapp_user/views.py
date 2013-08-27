import base64

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import simplejson
from django.http import HttpResponse

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
        if not self.object.deIappBirthday:
            return {}
        return { 'deIappBirthday': timestamp2date(self.object.deIappBirthday), }

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk': self.request.POST['uid']})

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['userGroups'] = LdapGroup.objects.filter(memberUid__contains=context['object'].uid)
        fullname = self.object.gecos.replace(' ', '_')
        context['photoUrl'] = fullname + '/' + fullname + '-original.jpg'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        userGroups = self.request.POST.getlist('userGroups')
        userGroups = [g for g in userGroups if g] # filter empty strings
        photo = self.request.FILES['photo']
        self.object.photo.save(self.object.photo.path, photo, save=False)
        photo.open()
        self.object.jpegPhoto = photo.read()
        photo.close()
        self.object.save(userGroups=userGroups)
        return redirect(self.get_success_url())


class UserDetail(DetailView):
    model = LdapUser

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['user_groups'] = LdapGroup.objects.filter(memberUid__contains=context['object'].uid)
        return context


def ajax_user_autocomplete(request):
    if 'term' in request.GET:
        users = LdapUser.objects.filter(
            cn__icontains=request.GET['term']
        )
        return HttpResponse( simplejson.dumps( [ {'label': user.cn, 'value': user.uid} for user in users ] ) )
    return HttpResponse()
