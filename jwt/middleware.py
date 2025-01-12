from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
import requests

class SSOJwtMiddlware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            setattr(request, "sso_user", None)
            return None
        try:
            jwt_token = auth_header.split(" ")[1]
            #auth_response = requests.get("http://sso:5555/sso/check", headers={"Authorization": f"Bearer {jwt_token}"})
            auth_response = requests.get("https://bem.cs.ui.ac.id/sso/check", headers={"Authorization": f"Bearer {jwt_token}"})
            if auth_response.status_code == 200:
                setattr(request, "sso_user", auth_response.json())
            else:
                setattr(request, "sso_user", None)
        except IndexError:
            setattr(request, "sso_user", None)
            return None

        return None

    def process_response(self, request: HttpRequest, response: HttpResponse):
        # This method is called after the view
        # You can modify the response here
        return response