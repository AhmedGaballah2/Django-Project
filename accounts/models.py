from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    ROLE_CHOICES = [
        ("instructor" , "Instructor"),
        ("student" , "Student")

      ]
    bio = models.CharField(max_length=100 ,blank=True)
    role = models.CharField(max_length=10 , choices=ROLE_CHOICES)
    owner = models.OneToOneField(User, on_delete=models.CASCADE , related_name="profile")
 
    
    
    def __str__(self):
        return f"{self.owner}"



    

