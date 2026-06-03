
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import  AllowAny
from ..models import Profile







class RegisterUser(APIView):
     permission_classes=[AllowAny]
     def post(self ,request):
          username = request.data.get("username")
          password = request.data.get("password")
          role = request.data.get("role")

          if not username or not password or not role:
               return Response({"error":"username,password and role are required"} , status.HTTP_400_BAD_REQUEST)
          

          if role not in ["student" , "instructor"]:
               return Response({"error":"Invalid role"} , status.HTTP_400_BAD_REQUEST)



          if User.objects.filter(username=username).exists():
                return Response({"error":"username already exist"} , status.HTTP_400_BAD_REQUEST)
          
          


               
          


          user = User.objects.create(username=username,password=password)
          profile = Profile.objects.create(owner=user,role=role)

          token = Token.objects.create(user=user)
          return Response({"token":token.key} , status.HTTP_201_CREATED)

