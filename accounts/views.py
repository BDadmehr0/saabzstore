import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import UserProfileForm
from .models import OTP, User


def multi_step_auth(request):
    return render(request, "accounts/auth.html")


@csrf_exempt
def api_send_otp(request):
    data = json.loads(request.body)
    phone = data.get("phone_number")

    if not phone:
        return JsonResponse({"success": False, "error": "شماره موبایل الزامی است"})

    user = User.objects.filter(phone_number=phone).first()
    if user and user.has_usable_password():
        request.session["temp_phone"] = phone
        return JsonResponse({"success": True, "skip_otp": True})

    code = OTP.generate_otp()
    OTP.objects.create(phone_number=phone, code=code)
    print(f"OTP for {phone}: {code}")

    request.session["phone_for_auth"] = phone
    return JsonResponse({"success": True, "skip_otp": False})


@csrf_exempt
def api_verify_otp(request):
    data = json.loads(request.body)
    phone = request.session.get("phone_for_auth")
    otp_code = data.get("code")

    if not phone:
        return JsonResponse({"success": False, "error": "شماره در سیستم یافت نشد"})

    otp_obj = OTP.objects.filter(phone_number=phone, code=otp_code).last()
    if not otp_obj or not otp_obj.is_valid():
        return JsonResponse({"success": False, "error": "کد اشتباه یا منقضی شده است"})

    user = User.objects.filter(phone_number=phone).first()
    if user:
        login(request, user)
        return JsonResponse({"success": True, "new_user": False})

    request.session["temp_phone"] = phone
    return JsonResponse({"success": True, "new_user": True})


@csrf_exempt
def api_set_name(request):
    data = json.loads(request.body)
    name = data.get("name")

    if not name:
        return JsonResponse({"success": False, "error": "نام الزامی است"})

    request.session["temp_name"] = name
    return JsonResponse({"success": True})


@csrf_exempt
def api_set_password(request):
    data = json.loads(request.body)
    phone = request.session.get("temp_phone")
    name = request.session.get("temp_name")
    password = data.get("password")

    if not phone:
        return JsonResponse({"success": False, "error": "سشن معتبر نیست"})

    if not password:
        return JsonResponse({"success": False, "error": "رمز عبور الزامی است"})

    user = User.objects.filter(phone_number=phone).first()

    if user:
        user.set_password(password)
        if name:
            user.name = name
        user.save()

    else:
        user = User.objects.create_user(
            phone_number=phone, password=password, name=name
        )

    for key in ["temp_phone", "temp_name", "phone_for_auth"]:
        if key in request.session:
            del request.session[key]

    login(request, user)
    return JsonResponse({"success": True})


@login_required
def dashboard(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = UserProfileForm(instance=user)
    return render(request, "accounts/dashboard.html", {"user": user, "form": form})


def user_logout(request):
    logout(request)
    return redirect("multi_step_auth")
