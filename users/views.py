from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from GuideForum.models import UserProfile


# Create your views here.
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))


def register(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()

            user_profile = UserProfile(user=new_user)
            user_profile.save()

            authenticated_user = authenticate(username=new_user.username,
                                              password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('homepage'))
    context = {'form': form}
    return render(request, 'register.html', context)

