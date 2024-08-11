from django.http import JsonResponse
from .models import SSOAccount

def sso_authenticated(handler):
    """
    USAGE

    ```
    @sso_authenticated
    def my_view(self, request):
        user = request.sso_user
        return JsonResponse({"message": "Hello, world!"})
    ```

    NOTE: This decorator is used to check if the user is authenticated. If the user is not authenticated, it will return a 401 status code.
    The second argument of the handler function should be the request object. Must be used in a class-based view.

    You can access the user object by using.
    """
    def wrapped(*args, **kwargs):
        request = args[1]
        if request.sso_user is None:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        npm = request.sso_user.get("npm")
        sso_user = None
        try:
            sso_user = SSOAccount.objects.get(npm=npm)
        except SSOAccount.DoesNotExist:
            pass
        if sso_user is None:
            sso_user = SSOAccount.objects.create(
                npm=npm,
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