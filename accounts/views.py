from django.shortcuts import render ,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm


# Create your views here.

@login_required

def home(request):
    return render(request,"accounts/test.html")

@login_required
def profile(request):
     form = ProfileForm(request.POST or None)
     if form.is_valid():
           profile = form.save(commit=False)
           profile.owner = request.user
           profile.save()

           return redirect("/")

     return render (request , "accounts/profile.html" , {"form":form} )


def register (request):
     form  = UserCreationForm(request.POST or None)
     if form.is_valid():
          user  = form.save()
          login(request , user)
          return redirect(reverse("profile"))
     return render(request , "accounts/register.html" , {"form" :form})