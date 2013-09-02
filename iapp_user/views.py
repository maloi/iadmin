import os
import base64
import time

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import simplejson
from django.http import HttpResponse
from django.conf import settings

from PIL import Image, ImageOps

from .models import LdapUser
from .forms import LdapUserForm
from .utils import timestamp2date, debug, getPhotoPath
from iapp_group.models import LdapGroup
from iapp_room.models import LdapRoom


class UserList(ListView):
    model = LdapUser


class UserCreate(CreateView):
    model = LdapUser


class UserUpdate(UpdateView):
    model = LdapUser
    form_class = LdapUserForm

    def get_initial(self):
        initial = {}
        if self.object.deIappBirthday:
            initial['deIappBirthday'] = timestamp2date(self.object.deIappBirthday)
        roomNumber = self.object.roomNumber
        telephoneNumber = self.object.telephoneNumber
        room = LdapRoom.objects.filter(cn__contains=roomNumber).filter(cn__contains=telephoneNumber)
        if len(room) > 0:
            initial['room'] = room[0].pk
        return initial

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk': self.request.POST['uid']})

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['userGroups'] = LdapGroup.objects.filter(memberUid__contains=context['object'].uid)
        fullname = self.object.gecos.replace(' ', '_')
        context['photoUrl'] = fullname + '/' + fullname + '-200x200.jpg'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        userGroups = self.request.POST.getlist('userGroups')
        userGroups = sorted([g for g in userGroups if g]) # filter empty strings
        room = form.cleaned_data.get('room')
        if room:
            import re
            s = re.search('([\w\s]+\w).*Tel:\s*(\d+)', room.pk)
            self.object.roomNumber = s.group(1)
            self.object.telephoneNumber = s.group(2)
        photo = self.request.FILES.get('photo', None)
        if photo:
            path = getPhotoPath(self.object, self.object.photo.path)
            absPath = settings.MEDIA_ROOT + path
            if os.path.exists(absPath):
                os.rename(absPath, absPath + time.strftime("-%Y%m%d-%H%M%S"))
            self.object.photo.save(path, photo, save=False)
            photo.open()
            self.object.jpegPhoto = photo.read()
            photo.close()
            fileName, fileExtension = os.path.splitext(absPath)
            image = Image.open(absPath)
            imagefit = ImageOps.fit(image, (640, 512), Image.ANTIALIAS)
            imagefit.save(fileName + '-640x512.jpg', 'JPEG', quality=75)
            imagefit = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
            imagefit.save(fileName + '-200x200.jpg', 'JPEG', quality=75)
        if len(form.cleaned_data.get('userPassword1')) > 0:
            self.object.save(userGroups=userGroups, password=form.cleaned_data.get('userPassword1'))
        else:
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
