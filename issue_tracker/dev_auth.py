from functools import wraps
from jwt.models import SSOAccount

def dev_sso_authenticated(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        if len(args) == 0:
            raise RuntimeError("No args passed to view")

        if len(args) < 2: # Function-based view (request)
            request = args[0]
        else: # Method of a class-based view (self, request)
            request = args[1]

        npm = request.headers.get("Dummy-Auth")

        try:
            user = SSOAccount.objects.get(npm=npm)
        except SSOAccount.DoesNotExist:
            request.sso_user = None
        else:
            request.sso_user = user

        return handler(*args, **kwargs)

    return wrapped