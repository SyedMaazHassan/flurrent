from django.shortcuts import render, redirect
from organizations.models import Project
from django.contrib import messages
from django.db import transaction
from authentication.models import User
from django.views import View


# Create your views here.
def home_view(request):
    all_projects = Project.objects.all()
    context = {
        "projects": all_projects
    }
    return render(request, "home.html", context)



def apply_on_project(request, project_id):
    project = Project.objects.filter(id = project_id).first()
    if not project:
        messages.error(request, "No project exists with this id")
        return redirect("core:home")

    if request.method == 'POST':
        price   = request.POST.get('price')
        note    = request.POST.get('note')
        days    = request.POST.get('days')

        print(price, note, days)

        messages.success(request, "Application has been submitted")

    return redirect("org:single-project", project_id=project.id)



class EndorserUserProfileView(View):
    def get(self, request, section):
        # get the user's profile information
        print(section)
        user = request.user
        template_info = {
            "personal": {
                "outline": "",
                "button_text": "Save changes",
                "template": "end_profile/personal_info.html",
                "title": "Personal Info",
                "subtitle": "Your personal info is 50% completed"
            },
            "security": {
                "outline": "-outline",
                "button_text": "Update password",
                "template": "end_profile/security.html",
                "title": "Password & Security",
                "subtitle": "Manage your password settings and secure your account."
            }

        }
            


        context = template_info[section]
        context["section"] = section
        return render(request, context["template"], context)


    def post(self, request, section):
        # update the user's profile information
        user = request.user
        organization = user.is_organization
        # return redirect("org:profile", section="security")
        if section == 'personal':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            # email = request.POST.get('email')
            phone = request.POST.get('phone')
            bio = request.POST.get('bio')
            profile_pic = request.FILES.get('profile_pic')

            try:
                if not (first_name and last_name):
                    raise Exception("'Name' field can't by empty")

                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if profile_pic:
                    user.profile_pic = profile_pic

                user.bio = bio
                user.phone = phone
                user.save()
                messages.success(request, "Personal info has been updated successfully!")
            
            except Exception as e:
                messages.error(request, str(e))

        elif section == 'security':
            # update the user's password

            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not user.check_password(current_password):
                messages.error(request, "Current password is wrong!")
            else:
                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    messages.success(request, "Password has been updated!")
                    return redirect("authentication:login")
                else:
                    messages.error(request, "New password must be same")

        return redirect("endorsers:profile", section=section)
