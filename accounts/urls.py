from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from .api.views import RegisterUser



urlpatterns= [
    path("login" , views.CustomLoginView.as_view(template_name="accounts/login.html") ,name="login"),
    path("register" , views.register, name="register") , 
    path("logout" , auth_views.LogoutView.as_view(), name =  "logout" ),
    path("auth/login", obtain_auth_token , name="login_user" ),
    path("auth/register", RegisterUser.as_view()  , name="register_user" ),
    path("profile" , views.profile , name="profile")
]