from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from .lib import sso_authenticated, SSOUser

# Create your views here.
@sso_authenticated
def check_self(req: HttpRequest):
    user: SSOUser = req.sso_user
    return JsonResponse({
        "username": user.username,
        "npm": user.npm,
        "full_name": user.full_name,
        "faculty": user.faculty,
        "short_faculty": user.short_faculty,
        "major": user.major,
    })