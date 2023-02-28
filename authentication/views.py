# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Refer
from organizations.models import Organization
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("core:home")
        else:
            context = {
                "email": email,
                "password": password,
                "error": "Invalid email or password",
            }
            return render(request, "signin.html", context)
    else:
        return render(request, "signin.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("authentication:login")


def validatePersonalInfo(request):
    status = False
    message = ""
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    if first_name and last_name and email:
        if not User.objects.filter(email=email).exists():
            status = True
        else:
            message = "Email address already exist"

    return {
        "status": status,
        "message": message,
        "data": {"first_name": first_name, "last_name": last_name, "email": email},
    }


def validateProfileType(request):
    status = False
    message = ""
    profile_type = request.POST.get("profile_type")
    organization_name = request.POST.get("organization_name")
    organization_type = request.POST.get("organization_type")
    endorser_tagline = request.POST.get("endorser_tagline")
    endorser_followers = request.POST.get("endorser_followers")

    if profile_type == "organization":
        if organization_name and organization_type:
            if not Organization.objects.filter(name=organization_name).exists():
                status = True
            else:
                message = "Organization already exist"
        else:
            message = "Organization detail is missing"

    if profile_type == "endorser":
        if endorser_tagline and endorser_followers:
            status = True
        else:
            message = "Endorser detail is missing"

    return {
        "status": status,
        "message": message,
        "data": {
            "profile_type": profile_type,
            "organization_name": organization_name,
            "organization_type": organization_type,
            "endorser_tagline": endorser_tagline,
            "endorser_followers": endorser_followers,
        },
    }


def validatePassword(request):
    status = False
    message = ""
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")
    if password1 and password2 and password1 == password2:
        status = True
    else:
        message = "Password is not matched"

    return {
        "status": status,
        "message": message,
        "data": {"password1": password1, "password2": password2},
    }


def signup_view(request):
    context = {"error": False}
    if request.method == "POST":
        # for personal information
        personal_info = validatePersonalInfo(request)
        profile_type = validateProfileType(request)
        set_password = validatePassword(request)
        print(personal_info)
        print(profile_type)
        print(set_password)

        if (
            personal_info["status"]
            and profile_type["status"]
            and set_password["status"]
        ):
            # Create profile
            try:
                with transaction.atomic():
                    # creating new user:
                    new_user = User(
                        first_name=personal_info["data"]["first_name"],
                        last_name=personal_info["data"]["last_name"],
                        email=personal_info["data"]["email"],
                    )
                    new_user.set_password(set_password["data"]["password1"])
                    new_user.save()

                    # Creating profile type
                    if profile_type["data"]["profile_type"] == "organization":
                        new_user.createOrganization(
                            name=profile_type["data"]["organization_name"],
                            type=profile_type["data"]["organization_type"],
                        )
                        # Organization created

                    # Creating profile type
                    if profile_type["data"]["profile_type"] == "endorser":
                        new_user.createEndorser(
                            tagline=profile_type["data"]["endorser_tagline"],
                            followers=profile_type["data"]["endorser_followers"],
                        )
                        # endorser created
                    refer_id = request.POST.get("refer_id")
                    invited_by = User.objects.filter(refer_id=refer_id)
                    if invited_by.count():
                        new_refer = Refer(
                            user_joined=new_user, invited_by=invited_by[0]
                        )
                        new_refer.save()

                    messages.success(request, "Profile has been created successfully!")
                    return redirect("authentication:login")

            except Exception as e:
                messages.error(request, str(e))

        else:
            error_msg = ""
            if personal_info["message"]:
                error_msg += "»" + personal_info["message"] + "\n"

            if profile_type["message"]:
                error_msg += "»" + profile_type["message"] + "\n"

            if set_password["message"]:
                error_msg += "»" + set_password["message"] + "\n"

            messages.error(request, error_msg)

        context = {
            "error": True,
            "personal_info": personal_info,
            "profile_type": profile_type,
            "set_password": set_password,
        }
    return render(request, "signup.html", context)
