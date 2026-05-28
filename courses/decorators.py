from django.shortcuts import redirect

def instructors_only(func_view):
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role == "instructor":
             return func_view(request, *args, **kwargs)
        return redirect("courses")

    return wrapper


def students_only(view_func):
    def wrapper(request , *args , **kwargs):
        if request.user.profile.role == "student":
            return view_func(request , *args , **kwargs)
        
        return redirect("instructor-courses")
    return wrapper