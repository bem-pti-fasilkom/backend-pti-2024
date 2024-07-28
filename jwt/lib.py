from django.http import JsonResponse

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
        return handler(*args, **kwargs)
    return wrapped