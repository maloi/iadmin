import os
import base64
import time
import re

from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import simplejson
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext


from PIL import Image, ImageOps

from .models import LdapUser, FormerLdapUser
from .forms import LdapUserForm
from .utils import timestamp2date, debug, getPhotoPath
from iapp_room.models import LdapRoom


class UserList(ListView):
    model = LdapUser


class FormerUserList(ListView):
    model = FormerLdapUser


class UserCreate(CreateView):
    model = LdapUser
    form_class = LdapUserForm

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_initial(self):
        # set initial uidNumber to lowest unused one
        initial = {}
        users = LdapUser.objects.all()
        max_uidNumber = 0
        for user in users:
            if user.uidNumber in xrange(max_uidNumber, 20000):
                max_uidNumber = user.uidNumber + 1
        initial['uidNumber'] = max_uidNumber
        return initial

    def get_success_url(self):
        return _get_success_url(self)

class UserUpdate(UpdateView):
    model = LdapUser
    form_class = LdapUserForm

    def get_initial(self):
        # set birthday to humanreadable form (and the one jqeury datepicker uses)
        initial = {}
        if self.object.deIappBirthday:
            initial['deIappBirthday'] = timestamp2date(self.object.deIappBirthday)
        # build room from room/telephoneNumber
        roomNumber = self.object.roomNumber
        telephoneNumber = self.object.telephoneNumber
        if roomNumber and telephoneNumber:
            room = LdapRoom.objects.filter(cn__contains=roomNumber).filter(cn__contains=telephoneNumber)
            if len(room) > 0:
                initial['room'] = room[0].pk
        return initial


    def get_context_data(self, **kwargs):
        """
        add photoUrl (small image) so it can be used to show a photo
        """
        context = super(self.__class__, self).get_context_data(**kwargs)
        fullname = self.object.gecos.replace(' ', '_')
        context['photoUrl'] = fullname + '/' + fullname + '-200x200.jpg'
        return context

    def form_valid(self, form):
        return _form_valid(self, form)

    def get_success_url(self):
        return _get_success_url(self)

def _get_success_url(self):
    return reverse('user_detail', kwargs={'pk': self.request.POST['uid']})

def _form_valid(self, form):
    """
    is called when form is valid
    """
    self.object = form.save(commit=False)
    # extract usergroups from form
    userGroups = self.request.POST.getlist('userGroups')
    userGroups = sorted([g for g in userGroups if g]) # filter empty strings
    # get telephone/roomNumber from form
    room = form.cleaned_data.get('room')
    if room:
        s = re.search('([\w\s]+\w).*Tel:\s*(\d+)', room.pk)
        self.object.roomNumber = s.group(1)
        self.object.telephoneNumber = s.group(2)
    # get uploaded image
    # photos will be saved under MEDIA_ROOT/user_fullname/
    # MEDIA_ROOT is set in settings.py
    photo = self.request.FILES.get('photo', None)
    if photo:
        # save on filesystem and rename existing one, so it is backed up
        path = getPhotoPath(self.object, self.object.photo.path)
        absPath = settings.MEDIA_ROOT + path
        if os.path.exists(absPath):
            os.rename(absPath, absPath + time.strftime("-%Y%m%d-%H%M%S"))
        self.object.photo.save(path, photo, save=False)
        # put photo into ldap (jpegPhoto attribute
        photo.open()
        self.object.jpegPhoto = photo.read()
        photo.close()
        # build and save wanted thumbnails of photo on filesystem
        fileName, fileExtension = os.path.splitext(absPath)
        image = Image.open(absPath)
        imagefit = ImageOps.fit(image, (640, 512), Image.ANTIALIAS)
        imagefit.save(fileName + '-640x512.jpg', 'JPEG', quality=75)
        imagefit = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
        imagefit.save(fileName + '-200x200.jpg', 'JPEG', quality=75)
    # if password was changed save user with new usergroups and new password
    if len(form.cleaned_data.get('userPassword1')) > 0:
        self.object.save(userGroups=userGroups, password=form.cleaned_data.get('userPassword1'))
    # else call save() with new usergroups only
    else:
        self.object.save(userGroups=userGroups)
    return redirect(self.get_success_url())

class UserDetail(DetailView):
    model = LdapUser


def delete_user(request, pk):
    # if user is to be deleted, check for confirmation first
    if request.method == 'GET':
        return render_to_response('iapp_user/ldapuser_delete.html',
                        { 'user': LdapUser.objects.get(pk=pk) }, context_instance=RequestContext(request))
    # if confirmed delete user (move to former members)
    # and remove user from all his groups
    elif request.method == 'POST':
        user = LdapUser.objects.get(pk=pk)
        for group in user.groups():
            group.memberUid.remove(user.uid )
            group.save()
        user.delete()
        return redirect(reverse('user_list'))

def undelete_user(request, uidNumber):
    # same as delete user but opposite direction
    if request.method == 'GET':
        return render_to_response('iapp_user/ldapuser_undelete.html',
                        { 'user': FormerLdapUser.objects.get(uidNumber=uidNumber) }, context_instance=RequestContext(request))
    elif request.method == 'POST':
        user = FormerLdapUser.objects.get(uidNumber=uidNumber)
        user.undelete()
        return redirect(reverse('former_user_list'))

def ajax_user_autocomplete(request):
    # ajax (json) response for autocomplete of users
    if 'term' in request.GET:
        users = LdapUser.objects.filter(
            cn__icontains=request.GET['term']
        )
        return HttpResponse( simplejson.dumps( [ {'value': user.cn, 'label': user.cn, 'dn': user.dn, 'uid': user.uid} for user in users ] ) )
    return HttpResponse()
