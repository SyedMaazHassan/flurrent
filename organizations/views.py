from django.shortcuts import render, redirect
from endorsers.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from authentication.models import User
from django.views import View
import json
from django.http import HttpResponse
from django.db.models import Q
from itertools import chain

# Create your views here.


@login_required
def home_view(request):
    if request.method == "POST":
        lower_price = int(request.POST.get("lower_price"))
        upper_price = int(request.POST.get("upper_price"))
        name = request.POST.get("name").lower()
        rating = request.POST.get("rating")

        if name:
            name_endorsers_id = []
            for endorser in Endorser.objects.all():
                if name in endorser.created_by.getFullName().lower():
                    name_endorsers_id.append(endorser.pk)
            filtered_endorsers_with_name = Endorser.objects.filter(id__in=name_endorsers_id)
        if rating:
            rating = int(request.POST.get("rating"))
            rating_endorsers_id = []
            for endorser in Endorser.objects.all():
                if rating == endorser.created_by.getEndorserReviews().get('average'):
                    rating_endorsers_id.append(endorser.pk)
            filtered_endorsers_with_rating = Endorser.objects.filter(id__in=rating_endorsers_id)


        if name and rating:
            filtered_endorsers_with_name_and_rating = Endorser.objects.none()
            for item in list(chain(filtered_endorsers_with_name, filtered_endorsers_with_rating)):
                filtered_endorsers_with_name_and_rating |= Endorser.objects.filter(pk=item.id)
            filtered_endorsers = filtered_endorsers_with_name_and_rating.filter(
                Q(price__gte=lower_price) & Q(price__lte=upper_price),
            )
        elif name:
            filtered_endorsers = filtered_endorsers_with_name.filter(
                Q(price__gte=lower_price) & Q(price__lte=upper_price),
            )
        elif rating:
            filtered_endorsers = filtered_endorsers_with_rating.filter(
                Q(price__gte=lower_price) & Q(price__lte=upper_price),
            )
        else:
            filtered_endorsers = Endorser.objects.filter(
                Q(price__gte=lower_price) & Q(price__lte=upper_price),
            )
        context = {
            "all_endorsers": filtered_endorsers,
            "lower_price":lower_price,
            "upper_price":upper_price,
            "name":name,
            "rating": str(rating),
        }
        return render(request, "org_home.html", context)

    all_endorsers = Endorser.objects.all()
    paginator = Paginator(all_endorsers, 18)
    page = 1
    page_1 = request.GET.get("page")
    page_numbers = paginator.page_range
    if page_1 and page_1.isdigit():
        all_endorsers = paginator.get_page(page_1)
        page = int(page_1)
    else:
        all_endorsers = paginator.get_page(1)

    context = {
        "all_endorsers": all_endorsers,
        "page_numbers": page_numbers,
        "page": page,
    }
    return render(request, "org_home.html", context)


@login_required
def single_project_view(request, project_id):
    context = {}
    project = Project.objects.filter(id=project_id).first()
    if not project:
        messages.error(request, "No project exists with this id")
        return redirect("core:home")

    context["project"] = project
    context["application"] = project.isAppliedBy(request.user)
    return render(request, "single-project.html", context)


@login_required
def endorser_profile_view(request, endorser_id):
    context = {"range_var": range(1, 6)}
    endorser = Endorser.objects.filter(id=endorser_id).first()
    if not endorser:
        messages.error(request, "No endorser exists with this id")
        return redirect("core:home")
    context["endorser"] = endorser
    if request.GET.get("section") == "completed-projects":
        context["projects"] = []
    else:
        context["reviews"] = endorser.created_by.getEndorserReviews()
    return render(request, "endorser_profile_view.html", context)


@login_required
def received_applications_view(request, project_id):
    context = {}
    project = Project.objects.filter(id=project_id).first()
    if not project:
        messages.error(request, "No project exists with this id")
        return redirect("core:home")

    applications = project.getReceivedApplications()
    context["single_project"] = project
    context["applications"] = applications
    context["application_ids"] = json.dumps(
        list(applications["list"].values_list("id", flat=True))
    )
    print(context["application_ids"])

    return render(request, "received_application.html", context)


@login_required
def single_order_view(request, order_id):
    context = {}
    organization = request.user.is_organization
    order = Order.objects.filter(id=order_id, organization=organization).first()
    if not order:
        messages.error(request, "No order exists with this id")
        return redirect("core:home")
    context = {"order": order}
    return render(request, "single_order.html", context)


def mark_as_complete(request, order_id):
    context = {}
    organization = request.user.is_organization
    order = Order.objects.filter(id=order_id, organization=organization).first()
    if not order:
        messages.error(request, "No order exists with this id")
        return redirect("core:home")

    order.status = "COMPLETED"
    order.save()

    messages.success(request, "Order has been marked as completed")
    return redirect("org:single-order", order_id=order_id)

    context = {"order": order}
    return render(request, "single_order.html", context)


@login_required
def manage_orders_view(request):
    organization = request.user.is_organization
    print(organization)
    orders = organization.getOrders()
    print(orders)
    context = {"orders": orders}
    return render(request, "manage_orders.html", context)


class ApplicationApproval(View):
    def check_access(self, user, project_id, application_id):
        project = Project.objects.filter(id=project_id).first()
        application = Application.objects.filter(id=application_id).first()
        if (
            not project
            or not application
            or application.project != project
            or project.created_by != user
        ):
            return False

        return {"project": project, "application": application}

    def get(self, request, project_id, application_id):
        context = {}
        context = self.check_access(request.user, project_id, application_id)
        if not context:
            messages.error(request, "Invalid request")
            return redirect("core:home")
        return render(request, "approve-application.html", context)

    def post(self, request, project_id, application_id):
        context = {}
        context = self.check_access(request.user, project_id, application_id)
        if not context:
            messages.error(request, "Invalid request")
            return redirect("core:home")

        # approving request
        application = context["application"]
        order = application.approve(approved_by=request.user)
        # placing order
        print(order)

        # Transferring money start

        # Transferring money end

        # redirecting user to the order page
        messages.success(request, "Order has been confirmed successfully!")
        return redirect("org:orders")


class OrgUserProfileView(View):
    def get(self, request, section):
        # get the user's profile information.
        print(section)
        user = request.user
        # get the referral's query set and invite link for the current user.
        referrals = user.getRefers()
        invite_link = user.getInviteLink()
        # calculating total number of points for the current users.
        total_points = 0
        for refer in referrals:
            total_points += refer.points
        # dynamic template info.
        template_info = {
            "personal": {
                "outline": "",
                "button_text": "Save changes",
                "template": "org_profile/personal_info.html",
                "title": "Personal Info",
                "subtitle": "Your personal info is 50% completed",
            },
            "security": {
                "outline": "-outline",
                "button_text": "Update password",
                "template": "org_profile/security.html",
                "title": "Password & Security",
                "subtitle": "Manage your password settings and secure your account.",
            },
            "referrals": {
                "outline": "-outline",
                "template": "org_profile/referrals.html",
                "title": "Your Referrals",
                "subtitle": "See all the people who have accepted your refer link, total earned points and more.",
                "referrals_list": referrals,
                "referrals_count": referrals.count(),
                "total_points": total_points,
                "invite_link": invite_link,
            },
            "dashboard": {
                "outline": "-outline",
                "template": "org_profile/dashboard.html",
                "title": "Dashboard",
                "subtitle": "See the number of endorsers, staff, earnings and their analytics here.",
            },
            "organization-info": {
                "outline": "",
                "button_text": "Save changes",
                "template": "org_profile/info.html",
                "title": "Organization profile",
                "subtitle": "Manage your organization profile, update basic info, location or social ids",
                "organization": user.is_organization,
            },
            "my-projects": {
                "outline": "",
                "button_text": "",
                "template": "org_profile/my_projects.html",
                "title": "My projects",
                "subtitle": "Manage your projects, edit or create a new one",
                "projects": user.is_organization.getProjects(),
            },
            "create-project": {
                "outline": "",
                "button_text": "Save project",
                "template": "org_profile/create_project.html",
                "title": "Create project",
                "subtitle": "Post a project for thousands of endorsers out there",
            },
            "organization-reviews": {
                "outline": "",
                "button_text": "",
                "template": "org_profile/reviews.html",
                "title": "Organization reviews",
                "subtitle": "Reviews your organization has received after exchange of service or product",
                "reviews": user.getOrgReviews(),
                "range_var": range(1, 6),
            },
            "staff": {
                "outline": "",
                "button_text": "",
                "template": "org_profile/staff.html",
                "title": "Staff members",
                "subtitle": "Manage your staff members, they can have access to some options",
                "staff_members": user.is_organization.getStaffMembers(),
            },
            "become-endorser": {
                "outline": "",
                "button_text": "Save endorser details",
                "template": "org_profile/create_endorser.html",
                "title": "Become endorser",
                "subtitle": "Get a chance to apply on jobs and start selling",
                "endorser": user.is_endorser,
            },
        }

        context = template_info[section]
        context["section"] = section
        return render(request, context["template"], context)

    def post(self, request, section):
        # update the user's profile information
        user = request.user
        organization = user.is_organization
        # return redirect("org:profile", section="security")
        if section == "personal":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            # email = request.POST.get('email')
            phone = request.POST.get("phone")
            bio = request.POST.get("bio")
            profile_pic = request.FILES.get("profile_pic")

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
                messages.success(
                    request, "Personal info has been updated successfully!"
                )

            except Exception as e:
                messages.error(request, str(e))

        elif section == "security":
            # update the user's password

            current_password = request.POST.get("current_password")
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")

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

        elif section == "organization-info":
            # update the user's organizations

            organization_name = request.POST.get("organization_name")
            organization_type = request.POST.get("organization_type")
            description = request.POST.get("description")
            logo = request.FILES.get("logo")
            print(request.FILES)
            try:
                if not (organization_name and organization_type):
                    raise Exception("Organization name or type can't by empty")

                organization.name = organization_name
                organization.type = organization_type
                organization.description = description
                if logo:
                    organization.logo = logo
                organization.save()

                # Updating social media
                website = request.POST.get("website")
                facebook = request.POST.get("facebook")
                instagram = request.POST.get("instagram")
                youtube = request.POST.get("youtube")
                tiktok = request.POST.get("tiktok")

                if organization.social_media:
                    organization.social_media.website = website
                    organization.social_media.facebook = facebook
                    organization.social_media.instagram = instagram
                    organization.social_media.youtube = youtube
                    organization.social_media.tiktok = tiktok
                    organization.social_media.save()
                else:
                    if website or facebook or instagram or youtube or tiktok:
                        new_social_media = SocialMedia(
                            website=website,
                            facebook=facebook,
                            instagram=instagram,
                            youtube=youtube,
                            tiktok=tiktok,
                        )
                        new_social_media.save()
                        organization.social_media = new_social_media
                        organization.save()

                messages.success(request, "Organization profile has been updated")

            except Exception as e:
                messages.error(request, str(e))

        elif section == "create-project":
            project_title = request.POST.get("project_title")
            project_description = request.POST.get("project_description")

            min_price = request.POST.get("min_price")
            max_price = request.POST.get("max_price")

            product_title = request.POST.get("product_title")
            product_type = request.POST.get("product_type")
            product_description = request.POST.get("product_description")
            product_thumbnail = request.FILES.get("product_thumbnail")

            requirements = request.POST.get("requirements")
            benefits = request.POST.get("benefits")

            try:
                with transaction.atomic():
                    if min_price >= max_price:
                        raise Exception("Minimum price must be less than maximum price")

                    product_or_service = organization.createProductOrService(
                        product_title,
                        product_type,
                        product_description,
                        user,
                        product_thumbnail,
                    )
                    print("Product or service created")

                    # Creating project
                    project = organization.createProject(
                        project_title,
                        project_description,
                        [min_price, max_price],
                        product_or_service,
                        requirements,
                        benefits,
                        user,
                    )

                    messages.success(request, "Project has been posted successfully!")
                    return redirect("org:single-project", project_id=project.id)

            except Exception as e:
                messages.error(request, str(e))

        elif section == "staff":
            staff_first_name = request.POST.get("staff_first_name")
            staff_last_name = request.POST.get("staff_last_name")
            staff_designation = request.POST.get("staff_designation")
            staff_email = request.POST.get("staff_email")
            staff_password = request.POST.get("staff_password")
            staff_profile_pic = request.FILES.get("staff_profile_pic")

            try:
                with transaction.atomic():
                    # Creating staff
                    new_staff_user = User.objects.create(
                        first_name=staff_first_name,
                        last_name=staff_last_name,
                        email=staff_email,
                    )
                    if staff_profile_pic:
                        new_staff_user.profile_pic = staff_profile_pic
                    new_staff_user.set_password(staff_password)
                    organization.createStaffMember(
                        new_staff_user, staff_designation, user
                    )

                    messages.success(
                        request, "Staff member has been added successfully"
                    )

            except Exception as e:
                messages.error(request, str(e))

        elif section == "become-endorser":
            description = request.POST.get("description")
            interests = request.POST.get("interests")
            tagline = request.POST.get("tagline")
            bio = request.POST.get("bio")
            followers = request.POST.get("followers")

            # Social media
            website = request.POST.get("website")
            facebook = request.POST.get("facebook")
            instagram = request.POST.get("instagram")
            youtube = request.POST.get("youtube")
            tiktok = request.POST.get("tiktok")

            try:
                with transaction.atomic():
                    social_media = None
                    if website or facebook or instagram or youtube or tiktok:
                        social_media = {
                            "website": website,
                            "facebook": facebook,
                            "youtube": youtube,
                            "tiktok": tiktok,
                            "instagram": instagram,
                        }

                    if not tagline or not followers:
                        raise Exception("Tagline and followers are required")

                    new_endorser = user.createEndorser(
                        tagline=tagline,
                        followers=followers,
                        description=description,
                        interests=interests,
                        social_media=social_media,
                    )
                    messages.success(request, "Endorser profile has been created")
                    return redirect("core:profile")

            except Exception as e:
                messages.error(request, str(e))

        return redirect("org:profile", section=section)
