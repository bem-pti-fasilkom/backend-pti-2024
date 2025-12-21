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

        raw = request.sso_user

        if raw is None:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        if isinstance(raw, SSOAccount):
            request.sso_user = raw
            return handler(*args, **kwargs)
        
        npm = raw.get("npm")

        if npm is None:
            return JsonResponse({"error": "Invalid SSO data"}, status=401)
        
        try:
            sso_user = SSOAccount.objects.get(npm=npm)
        except SSOAccount.DoesNotExist:
            org = raw.get("organization", {})
            sso_user = SSOAccount.objects.create(
                npm=raw.get("npm"),
                full_name=raw.get("nama"),
                username=raw.get("username"),
                faculty=org.get("faculty"),
                short_faculty=org.get("short_faculty"),
                major=org.get("major"),
                program=org.get("program"),
            )
        
        request.sso_user = sso_user
        return handler(*args, **kwargs)
    return wrapped