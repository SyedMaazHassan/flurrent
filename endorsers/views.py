from django.shortcuts import render, redirect
from organizations.models import Project
from django.contrib import messages
from django.db import transaction
from authentication.models import User
from django.views import View
from .models import Application, Order
from organizations.models import SocialMedia
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required


# Create your views here.
def home_view(request):
    all_projects = Project.objects.all()
    context = {
        "projects": all_projects
    }
    return render(request, "home.html", context)


@login_required
def manage_orders_view(request):
    endorser = request.user.is_endorser
    print(endorser)
    orders = endorser.getOrders()
    context = {
        'orders': orders
    }
    return render(request, "end_orders.html", context)


# @login_required
# def deliver_work_view(request):


@login_required
def single_order_view(request, order_id):
    context = {}
    endorser = request.user
    order = Order.objects.filter(id = order_id, service_provider = endorser).first()
    if not order:
        messages.error(request, "No order exists with this id")
        return redirect("core:home")

    if request.method == "POST":
        note = request.POST.get('note')
        thumbnail = request.FILES.get('thumbnail')
        source_file = request.FILES.get('source_file')
    
        try:
            order.createUpdate(
                note,
                thumbnail,
                endorser,
                source_file
            )
            messages.success(request, "Order update has been submitted successfully")

        except Exception as e:
            messages.error(request, "Something went wrong. Deliver the work again.")

    context = {
        'order': order
    }
    return render(request, "end_single_order.html", context)




def get_single_application(request):
    output = {
        "status": False,
        "data": None
    }
    application_id = request.GET.get('id')
    if application_id and application_id.isdigit():
        application_id = int(application_id)
        application = Application.objects.filter(id = application_id).first()
        if application:
            data_object = {
                "approve_url"        : request.build_absolute_uri(reverse('org:approve-application', args=[application.project.id, application.id])),
                "project_url"        : request.build_absolute_uri(reverse('org:single-project', args=[application.project.id])),
                "project_org_logo"   : application.project.organization.logo.url,
                "project_org_name"   : application.project.organization.name,
                "project_title"      : application.project.title,
                "project_description": application.project.description,
                "project_budget"     : str(application.project.budget),
                "project_created_at" : application.project.get_created_at(),
                "project_type"       : str(application.project.product.type),
                "application_price"  : application.price,
                "application_days"   : application.days,
                "application_created_at": application.get_created_at(),
                "application_status" : True if application.is_approved else False,
                "application_note"   : application.note,
                "endorser_name"      : application.created_by.getFullName(),
                "endorser_profile_pic": application.created_by.profile_pic.url,                
            }
            output['data'] = data_object
            output['status'] = True
            print(data_object['approve_url'])
    return JsonResponse(output)


@login_required
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

        application, created = Application.objects.update_or_create(
            price = price,
            note = note,
            days = days,
            project = project,
            created_by = request.user
        )
        status = ""
        if created:
            status = "submitted"
        else:
            status = "updated"

        messages.success(request, f"Your application on this project has been {status}")

    return redirect("org:single-project", project_id=project.id)



class EndorserUserProfileView(View):
    def get(self, request, section):
        # get the user's profile information
        print(section)
        user = request.user
        endorser = user.is_endorser
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
            },
            "endorser-info": {
                "outline": "",
                "button_text": "Save changes",
                "template": "end_profile/profile_info.html",
                "title": "Endorser profile info",
                "subtitle": "Update your profile info to attract more organizations.",
                "endorser": endorser
            },
            "reviews": {
                "outline": "",
                "button_text": "",
                "template": "end_profile/reviews.html",
                "title": "Endorser reviews",
                "subtitle": "Reviews you have received as an endorser",
                "reviews": user.getEndorserReviews(),
                "range_var": range(1, 6)
            },
            "applications": {
                "outline": "",
                "button_text": "",
                "template": "end_profile/applications.html",
                "title": "Your applications",
                "subtitle": "List of applications you have submmited to the projects",
                "applications": endorser.getApplications(),
            },
            "register-organization": {
                "outline": "",
                "button_text": "Save details",
                "template": "end_profile/create_organization.html",
                "title": "Register organization",
                "subtitle": "List your organization on our platform to find best endorsers",
                # "applications": endorser.getApplications(),  
            }
        
        }
            


        context = template_info[section]
        context["section"] = section
        return render(request, context["template"], context)


    def post(self, request, section):
        # update the user's profile information
        user = request.user
        endorser = user.is_endorser
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

        elif section == 'endorser-info':
            
            description = request.POST.get('description')
            tagline     = request.POST.get('tagline')
            bio         = request.POST.get('bio')
            interests   = request.POST.get('interests')
            followers   = request.POST.get('followers')

            try:
                if not tagline:
                    raise Exception("Tagline is required")

                endorser.description = description
                endorser.tagline = tagline
                endorser.bio = bio
                endorser.interests = interests
                endorser.followers = followers
                endorser.save()

                # Updating social media
                website = request.POST.get('website')
                facebook = request.POST.get('facebook')
                instagram = request.POST.get('instagram')
                youtube = request.POST.get('youtube')
                tiktok = request.POST.get('tiktok')
                
                if endorser.social_media:
                    endorser.social_media.website = website
                    endorser.social_media.facebook = facebook
                    endorser.social_media.instagram = instagram
                    endorser.social_media.youtube = youtube
                    endorser.social_media.tiktok = tiktok                
                    endorser.social_media.save()
                else:
                    if website or facebook or instagram or youtube or tiktok:
                        new_social_media = SocialMedia(
                            website = website,
                            facebook = facebook,
                            instagram = instagram,
                            youtube = youtube,
                            tiktok = tiktok
                        )
                        new_social_media.save()
                        endorser.social_media = new_social_media
                        endorser.save()

                messages.success(request, "Endorser profile has been updated")

            except Exception as e:
                messages.error(request, str(e))

        elif section == 'register-organization':            
            organization_logo = request.FILES.get('organization_logo')            
            organization_name = request.POST.get('organization_name')
            organization_type = request.POST.get('organization_type')
            description       = request.POST.get('description')

            try:
                if not (organization_name and organization_type):
                    raise Exception("Organization name or type can't by empty")

                # Updating social media
                website = request.POST.get('website')
                facebook = request.POST.get('facebook')
                instagram = request.POST.get('instagram')
                youtube = request.POST.get('youtube')
                tiktok = request.POST.get('tiktok')
                social_media = None
                if website or facebook or instagram or youtube or tiktok:
                    social_media = {
                        'website': website,
                        'facebook': facebook,
                        'instagram': instagram,
                        'youtube': youtube,
                        'tiktok': tiktok
                    }

                organization = user.createOrganization(
                    name = organization_name,
                    type = organization_type,
                    logo = organization_logo,
                    description = description,
                    social_media = social_media
                )
                
                messages.success(request, "Organization profile has been created")
                return redirect("org:profile", section="organization-info")

            except Exception as e:
                messages.error(request, str(e))


        return redirect("endorsers:profile", section=section)
