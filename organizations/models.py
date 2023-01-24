from django.db import models
from django.utils import timezone
from django.db import transaction
# Create your models here.
import timeago


# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver


class CreatedCommon(models.Model):
    created_at  = models.DateTimeField(default=timezone.now)
    created_by  = models.ForeignKey("authentication.User", on_delete=models.CASCADE)

    def get_created_at(self):
        current_time = timezone.now()
        created_at = self.created_at
        difference = current_time - created_at
        return timeago.format(difference) 

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class Location(models.Model):
    latitude    = models.FloatField()
    longitude   = models.FloatField()

    def __str__(self) -> str:
        return f'({self.latitude}, {self.longitude})'


class Budget(models.Model):
    min_price   = models.FloatField(null=True, blank=True)
    max_price   = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.min_price or self.max_price:
            super(Budget, self).save(*args, **kwargs)
        else:
            raise Exception("Add at least 1 price")

    def __str__(self) -> str:
        return f"${int(self.min_price)} -  ${int(self.max_price)}"

class SocialMedia(models.Model):
    website     = models.URLField(null=True, blank=True)
    facebook    = models.URLField(null=True, blank=True)
    instagram   = models.URLField(null=True, blank=True)
    youtube     = models.URLField(null=True, blank=True)
    tiktok      = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.website or self.facebook or self.instagram or self.tiktok or self.youtube:
            super(SocialMedia, self).save(*args, **kwargs)
        else:
            raise Exception("Add at least 1 url in social media object")

    def __str__(self):
        string = ""
        if self.website:
            string += "website, "
        if self.facebook:
            string += "facebook, "
        if self.instagram:
            string += "instagram, "
        if self.youtube:
            string += "youtube, "
        if self.tiktok:
            string += "tiktok, "

        return string


class Organization(CreatedCommon):
    name        = models.CharField(max_length=255)
    logo        = models.ImageField(upload_to="logos", default="logos/default.jpg", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type        = models.CharField(max_length=255)
    location    = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True, blank=True)
    social_media = models.OneToOneField(SocialMedia, on_delete=models.SET_NULL, null=True, blank=True)


    def getOrders(self):
        from endorsers.models import Order
        all_orders = Order.objects.filter(organization = self)
        return {
            "list": all_orders,
            "count": all_orders.count()
        }

    def createProject(self, title, description, budget, product, requirements, benefits, created_by):
        with transaction.atomic():
            new_budget = Budget.objects.create(
                min_price = budget[0],
                max_price = budget[1]
            )
            new_project = Project.objects.create(
                title       = title,
                description = description,
                budget      = new_budget,
                product     = product,
                requirements= requirements,
                benefits    = benefits,
                organization= self,
                created_by  = created_by
            )
            return new_project

    def getStaffMembers(self):
        all_staff_members = Staff.objects.filter(organization = self)
        return all_staff_members

    def getProjects(self, exclude=None):
        all_projects = Project.objects.filter(organization = self)
        if exclude:
            all_projects = all_projects.exclude(id = exclude)
        return all_projects

    def createProductOrService(self, name, type, description, created_by, thumbnail=None):
        new_product_or_service = ProductService.objects.create(
            name            = name,
            type            = type,
            description     = description,
            organization    = self,
            thumbnail       = thumbnail,
            created_by      = created_by
        )
        return new_product_or_service
    
    def createStaffMember(self, user, designation, created_by):
        new_staff = Staff.objects.create(
            designation = designation,
            organization = self,
            user        = user,
            created_by  = created_by
        )
        user.is_staff_member = new_staff
        user.save()
        return new_staff

    def __str__(self) -> str:
        return f'{self.name} ({self.type})'


class Staff(CreatedCommon):
    designation = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user  = models.OneToOneField("authentication.User", on_delete=models.CASCADE, null=True, blank=True, related_name="staff_member_obj")

    def __str__(self) -> str:
        return f'{self.user} ({self.designation})'


class ProductService(CreatedCommon):
    name        = models.CharField(max_length=255)
    type        = models.CharField(max_length=255, choices=[('product', 'product'), ('service', 'service')], default='product')
    description = models.TextField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    thumbnail   = models.ImageField(upload_to="product-thumbnail", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


class Project(CreatedCommon):
    title       = models.CharField(max_length=255)
    description = models.TextField()
    budget      = models.OneToOneField(Budget, on_delete=models.SET_NULL, null=True, blank=True)
    product     = models.ForeignKey(ProductService, on_delete=models.CASCADE)
    requirements = models.TextField()
    benefits    = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    is_active   = models.BooleanField(default=True)

    def isAppliedBy(self, user):
        from endorsers.models import Application
        application = Application.objects.filter(project = self, created_by = user).first()
        return application

    def getShortText(self, string, length):
        if len(string) > length:
            string = string[:length] + "..."
        return string

    def getShortTitle(self):
        return self.getShortText(self.title, 38)

    def getShortDescription(self):
        return self.getShortText(self.description, 150)

    def getMoreFromThisOrg(self):
        more_projects = self.organization.getProjects(exclude = self.id)[:5]
        return more_projects

    def getRequirements(self):
        requirements = self.requirements.split("\n")
        return requirements

    def getReceivedApplications(self):
        from endorsers.models import Application
        applications = Application.objects.filter(project = self)
        return {
            "list": applications,
            "count": applications.count()
        }

    def getBenefits(self):
        benefits = self.benefits.split("\n")
        return benefits

    def __str__(self) -> str:
        return f"{self.title} ({self.budget}) {'ACTIVE' if self.is_active else ''}"

    
