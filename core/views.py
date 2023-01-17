from django.shortcuts import render, redirect
from faker import Faker
from authentication.models import User
from organizations.models import *
from django.db import transaction
import random
from endorsers.models import Endorser
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def createFakeOrganizationsUser(quantity = 10):
    fake = Faker()

    for i in range(quantity):
        
        # User data
        profile = fake.profile()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = profile["mail"]
        password = email
        
        # # Organization data        
        name = fake.name()
        description = fake.text()
        type = fake.word()
        social_media = {
            'website'   : profile['website'][0],
            'facebook'  : None,
            'youtube'   : None,
            'tiktok'    : None,
            'instagram' : None
        }
        location = profile['current_location']

        # creating new user:
        new_user = User(
            first_name = first_name,
            last_name = last_name,
            email = email
        )
        new_user.set_password(password)
        new_user.save()
        print("User created")

        new_user.createOrganization(
            name=name,
            logo=None,
            description=description,
            type=type,
            location=location,
            social_media=social_media
        )

      
        # )




def createFakeProjects():
    fake = Faker()
    all_organizations = Organization.objects.all()
    for organization in all_organizations:
        quantity_of_jobs = random.randint(7, 15)
        created_by = organization.created_by 
        for i in range(quantity_of_jobs):
            # Creating product
            product_or_service = organization.createProductOrService(
                fake.name(),
                random.choice(['service', 'product']),
                fake.text(),
                created_by
            )
            print("Product or service created")

            # Creating project
            project = organization.createProject(
                fake.sentence(),
                fake.text(),
                [random.randint(100, 500), random.randint(1500, 2500)],
                product_or_service,
                "\n".join(fake.paragraphs(nb=3)),
                "\n".join(fake.paragraphs(nb=3)),
                created_by
            )
            print("Project created")

    # for i in range(quantity):
    #     print(i)



def createFakeStaffMember():
    designations = [    "Software Developer",    "Technical Writer",    "Technical Support Engineer",    "System Administrator",    "Network Engineer",    "Data Scientist",    "DevOps Engineer",    "Quality Assurance Tester",    "Project Manager",    "Information Security Analyst"]
    fake = Faker()
    all_organizations = Organization.objects.all()
    for organization in all_organizations:
        qty = random.randint(4, 10)
        created_by = organization.created_by 
        for i in range(qty):
            profile = fake.profile()
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = profile["mail"]
            password = email
            
            # creating new user:
            new_user = User(
                first_name = first_name,
                last_name = last_name,
                email = email
            )
            new_user.set_password(password)
            new_user.save()
            print("User created")

            # Creating member
            staff_member = organization.createStaffMember(
                new_user,
                random.choice(designations),
                created_by
            )
            print("Staff member created")




def createFakeEndorsers(quantity = 100):
    fake = Faker()
    for i in range(quantity):
        # User data
        profile = fake.profile()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = profile["mail"]
        password = email

        # Endorser data
        social_media = {
            'website'   : profile['website'][0],
            'facebook'  : None,
            'youtube'   : None,
            'tiktok'    : None,
            'instagram' : None
        }
        location = profile['current_location']
        

        # creating new user:
        new_user = User(
            first_name = first_name,
            last_name = last_name,
            email = email
        )
        new_user.set_password(password)
        new_user.save()
        print("User created")
        
        # create new endorser
        new_endorser = new_user.createEndorser(
            fake.catch_phrase(),
            fake.text(),
            fake.random_int(min=500, max=100000),
            "\n".join(fake.paragraphs(nb=3)),
            location,
            social_media
        )
        print(new_endorser)
        print("=============")

        




@transaction.atomic
def landing_view(request):
    # createFakeOrganizationsUser()
    # createFakeProjects()
    # createFakeStaffMember()
    # print(all_users.count())
    # createFakeEndorsers()

    words = ['Digital marketing expert', 'Social media consultant', 'Marketing specialist', 'Advertising professional', 'Marketing manager', 'Graphic designer', 'Web developer', 'Advertising agency owner', 'Publicist', 'Brand ambassador', 'Social media analyst', 'Marketing coordinator', 'Marketing director', 'Social media specialist', 'Marketing consultant', 'Marketing research specialist', 'Social media consultant', 'Marketing communication specialist', 'Marketing analyst', 'Marketing research analyst', 'Marketing assistant', 'Marketing intern', 'Marketing strategist', 'Marketing coordinator', 'Marketing officer', 'Marketing assistant', 'Marketing specialist', 'Marketing research associate', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator', 'Marketing manager', 'Marketing research specialist', 'Marketing specialist', 'Marketing officer', 'Marketing assistant', 'Marketing intern', 'Marketing coordinator']

    # all_users = Endorser.objects.all()
    # for endorser in all_users:
    #     bio = random.choice(words)
    #     endorser.bio = bio
    #     endorser.save()
    #     print(bio)

    return render(request, 'landing.html')


@login_required
def profile_view(request):
    if request.user.mode == "organization":
        return redirect("org:profile", section = "personal")
    else:
        return redirect("endorsers:profile", section = "personal")

@login_required
def home_view(request):
    if request.user.mode == "organization":
        return redirect("org:home")
    else:
        return redirect("endorsers:home")

@login_required
def switch_mode(request, mode):
    if mode not in ['organization', 'endorser']:
        return redirect("org:profile", section="personal")

    user = request.user
    if mode == "organization" and not user.is_organization:
        messages.error(request, "Organization is not created yet")
        return redirect("endorsers:profile", section="personal")

    if mode == "endorser" and not user.is_endorser:
        messages.error(request, "Endorser profile is not created yet")
        return redirect("org:profile", section="personal")

    user.mode = mode
    user.save()
    return redirect("core:home")


class UserProfileView(View):
    def get(self, request, section):
        # get the user's profile information
        print(section)
        user = request.user
        template_info = {
            "personal": {
                "outline": "",
                "button_text": "Save changes",
                "template": "profile/personal_info.html",
                "title": "Personal Info",
                "subtitle": "Your personal info is 50% completed"
            },
            "security": {
                "outline": "-outline",
                "button_text": "Update password",
                "template": "profile/security.html",
                "title": "Password & Security",
                "subtitle": "Manage your password settings and secure your account."
            },
            "organization-info": {
                "outline": "",
                "button_text": "Save changes",
                "template": "profile/organization/info.html",
                "title": "Organization profile",
                "subtitle": "Manage your organization profile, update basic info, location or social ids",
                "organization": user.is_organization
            },
            "my-projects": {
                "outline": "",
                "button_text": "",
                "template": "profile/organization/my_projects.html",
                "title": "My projects",
                "subtitle": "Manage your projects, edit or create a new one",
                "projects": user.is_organization.getProjects()
            },
            "create-project": {
                "outline": "",
                "button_text": "Save project",
                "template": "profile/organization/create_project.html",
                "title": "Create project",
                "subtitle": "Post a project for thousands of endorsers out there",
            },
            "organization-reviews": {
                "outline": "",
                "button_text": "",
                "template": "profile/organization/reviews.html",
                "title": "Organization reviews",
                "subtitle": "Reviews your organization has received after exchange of service or product",
                "reviews": user.getOrgReviews(),
                "range_var": range(1, 6)
            },
            "staff": {
                "outline": "",
                "button_text": "",
                "template": "profile/organization/staff.html",
                "title": "Staff members",
                "subtitle": "Manage your staff members, they can have access to some options",
                "staff_members": user.is_organization.getStaffMembers(),
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

        elif section == 'organization-info':
            # update the user's organizations

            organization_name = request.POST.get('organization_name')
            organization_type = request.POST.get('organization_type')
            description = request.POST.get('description')
            logo = request.FILES.get('logo')
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
                website = request.POST.get('website')
                facebook = request.POST.get('facebook')
                instagram = request.POST.get('instagram')
                youtube = request.POST.get('youtube')
                tiktok = request.POST.get('tiktok')
                
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
                            website = website,
                            facebook = facebook,
                            instagram = instagram,
                            youtube = youtube,
                            tiktok = tiktok
                        )
                        new_social_media.save()
                        organization.social_media = new_social_media
                        organization.save()

                messages.success(request, "Organization profile has been updated")

            except Exception as e:
                messages.error(request, str(e))

        elif section == "create-project":

            project_title       = request.POST.get("project_title")
            project_description = request.POST.get("project_description")

            min_price           = request.POST.get("min_price")
            max_price           = request.POST.get("max_price")

            product_title       = request.POST.get("product_title")
            product_type        = request.POST.get("product_type")
            product_description = request.POST.get("product_description")
            product_thumbnail   = request.FILES.get("product_thumbnail")

            requirements        = request.POST.get("requirements")
            benefits            = request.POST.get("benefits")

            try:
                with transaction.atomic():
                    if min_price >= max_price:
                        raise Exception("Minimum price must be less than maximum price")

                    product_or_service = organization.createProductOrService(
                        product_title,
                        product_type,
                        product_description,
                        user,
                        product_thumbnail
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
                        user
                    )

                    messages.success(request, "Project has been posted successfully!")
                    return redirect("org:single-project", project_id=project.id)

            except Exception as e:
                messages.error(request, str(e))

        elif section == "staff":
            staff_first_name       = request.POST.get("staff_first_name")
            staff_last_name        = request.POST.get("staff_last_name")
            staff_designation      = request.POST.get("staff_designation")
            staff_email            = request.POST.get("staff_email")
            staff_password         = request.POST.get("staff_password")
            staff_profile_pic      = request.FILES.get("staff_profile_pic")

            try:
                with transaction.atomic():

                    # Creating staff
                    new_staff_user = User.objects.create(
                        first_name = staff_first_name,
                        last_name = staff_last_name,
                        email = staff_email,
                    )
                    new_staff_user.profile_pic = staff_profile_pic
                    new_staff_user.set_password(staff_password)
                    organization.createStaffMember(new_staff_user, staff_designation, user)

                    messages.success(request, "Staff member has been added successfully")

            except Exception as e:
                messages.error(request, str(e))

        return redirect("org:profile", section=section)
