from django.http import JsonResponse
from .models import SSOAccount
from dataclasses import dataclass

@dataclass
class SSOUser:
    npm: str
    full_name: str
    username: str
    faculty: str
    short_faculty: str
    major: str
    program: str

def sso_authenticated(handler, *args, **kwargs):
    """
    USAGE

    ```
    @sso_authenticated
    def my_view(self, request):
        user = request.sso_user
        return JsonResponse({"message": "Hello, world!"})
    ```

    NOTE: This decorator is used to check if the user is authenticated. If the user is not authenticated, it will return a 401 status code.
    The second argument of the handler function should be the request object.

    You can access the user object by using.
    """
    def wrapped(*args, **kwargs):
        # check if the wrapped function is a class-based view
        if len(args) < 2:
            request = args[0]
        else:
            request = args[1]
        npm = request.sso_user.get("npm") if request.sso_user is not None else None
        sso_user = None
        try:
            sso_user = SSOAccount.objects.get(npm=npm)
        except SSOAccount.DoesNotExist:
            pass
        if sso_user is None and npm is not None:
            sso_user = SSOAccount.objects.create(
                npm=request.sso_user["user"],
                full_name=request.sso_user["nama"],
                username=request.sso_user["user"],
                faculty=request.sso_user["jurusan"]["faculty"],
                short_faculty=request.sso_user["jurusan"]["shortFaculty"],
                major=request.sso_user["jurusan"]["major"],
                program=request.sso_user["jurusan"]["program"]
            )
            sso_user.save()
        request.sso_user = sso_user
        return handler(*args, **kwargs)
    return wrapped