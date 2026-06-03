from django import forms
from .models import Category, Course, CourseDocument








class CourseForm(forms.ModelForm):

   
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]


    title = forms.CharField(
        max_length=200,
        required=True
    )

    description = forms.CharField(
        widget=forms.Textarea
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all()
    )

    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        required=True
    )


    class Meta:

        model = Course

        fields = [
            "title",
            "description",
            "category",
            "level"
        ]


class CourseDocumentForm(forms.ModelForm):
    class Meta:
        model = CourseDocument
        fields = ["title", "file"]
