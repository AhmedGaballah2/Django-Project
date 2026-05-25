
from django import forms
from .models import Profile



class ProfileForm(forms.ModelForm):
    ROLE_CHOICES = [
        ("instructor" , "Instructor"),
        ("student" , "Student")

      ]
    bio = forms.CharField(max_length=100 ,widget=forms.Textarea)
    role = forms.ChoiceField(choices=ROLE_CHOICES)


    class Meta:
        model = Profile
        fields = [
            "bio",
            "role"
        ]