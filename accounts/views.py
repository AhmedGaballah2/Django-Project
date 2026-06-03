from django.shortcuts import render ,redirect
from django.urls import reverse , reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib.auth.views import LoginView



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

           if profile.role == "student":
               return redirect("courses")
           else:
                return redirect("instructor-courses")


           

     return render (request , "accounts/profile.html" , {"form":form} )


def register (request):
     form  = UserCreationForm(request.POST or None)
     if form.is_valid():
          user  = form.save()
          login(request , user)
          return redirect(reverse("profile"))
     return render(request , "accounts/register.html" , {"form" :form})





class CustomLoginView(LoginView):
     template_name="accounts/login.html"


     def get_success_url(self):
           if self.request.user.profile.role == "instructor":
                return reverse_lazy("instructor-courses")
           else:
                return reverse_lazy("courses")
     