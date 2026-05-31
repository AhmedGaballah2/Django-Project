from rest_framework.permissions import BasePermission , SAFE_METHODS





class IsInstructorOrReadOnly(BasePermission):

    def has_permission(self , request , view):
        if request.method != "GET":
            return request.user.is_authenticated and request.user.profile.role == "instructor"
        return True

    def has_object_permission(self,request , view , obj):

        if request.method in SAFE_METHODS:
            return True
        

        return  obj.instructor == request.user 
    



class IsStudent(BasePermission):
    def has_permission(self , request , view):
        return request.user.profile.role  == "student"
    


class IsInstructor(BasePermission):
    def has_permission(self , request , view):
        return request.user.profile.role  == "instructor"
