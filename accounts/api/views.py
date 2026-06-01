
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import  AllowAny







class RegisterUser(APIView):
     permission_classes=[AllowAny]
     def post(self ,request):
          username = request.data.get("username")
          password = request.data.get("password")
          

          if not username or not password:
               return Response({"error":"username and password are required"} , status.HTTP_400_BAD_REQUEST)
          
          if User.objects.filter(username=username).exists():
                return Response({"error":"username already exist"} , status.HTTP_400_BAD_REQUEST)
          


               
          


          user = User.objects.create(username=username,password=password)

          token = Token.objects.create(user=user)
          return Response({"token":token.key} , status.HTTP_201_CREATED)

