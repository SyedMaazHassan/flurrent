from django.db import models
from organizations.models import CreatedCommon, Project, Location, SocialMedia
from django.db import transaction
from django.utils import timezone
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver



class Endorser(CreatedCommon):
    tagline     = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    bio         = models.CharField(max_length=200, null=True, blank=True)
    followers   = models.IntegerField(default=0)
    interests   = models.TextField(null = True, blank = True)
    location    = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True, blank=True)
    social_media = models.OneToOneField(SocialMedia, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)

    def getOrders(self):
        orders = Order.objects.filter(service_provider = self.created_by)
        return {
            "list": orders,
            "count": orders.count()
        }

    def getApplications(self):
        all_applications = Application.objects.filter(created_by = self.created_by)
        count = all_applications.count()
        return {
            "list": all_applications,
            "count": count
        }

    def getCompletedJobs(self):
        return {"count": "5000+"}

    def getFollowers(self):
        if self.followers < 1000:
            return str(self.followers)
        elif self.followers < 1000000:
            return '{:.1f}K'.format(self.followers / 1000)
        else:
            return '{:.1f}M'.format(self.followers / 1000000)

    def __str__(self) -> str:
        return self.created_by.getFullName()


class OrderUpdate(CreatedCommon):
    note = models.TextField()
    thumbnail = models.ImageField(upload_to="orders/portfolio_thumbnails")
    source_file = models.ImageField(upload_to="orders/source_files", null=True, blank=True)
    order = models.ForeignKey("endorsers.Order", on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


class Order(CreatedCommon):
    project = models.ForeignKey("organizations.Project", on_delete=models.SET_NULL, null=True, blank=True)
    application = models.ForeignKey("endorsers.Application", on_delete=models.SET_NULL, null=True, blank=True)
    requirements = models.TextField()
    price = models.FloatField()
    days = models.IntegerField()
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.ForeignKey("authentication.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="ServiceProvider")
    status = models.CharField(max_length=50, default="ACTIVE")
    updated_at = models.DateField(default=timezone.now)

    def getUpdates(self):
        all_updates = OrderUpdate.objects.filter(order = self).order_by("created_by")
        return all_updates

    def createUpdate(self, note, thumbnail, service_provider, source_file=None):
        new_order_update = OrderUpdate(
            note = note,
            thumbnail = thumbnail,
            order = self,
            created_by = service_provider
        )
        if source_file:
            new_order_update.source_file = source_file
        new_order_update.save()
        return new_order_update

    def createFromApplication(self, application, created_by):
        self.project = application.project
        self.application = application
        self.requirements = self.project.requirements
        self.price = application.price
        self.days = application.days
        self.service_provider = self.application.created_by
        self.organization = self.application.project.organization
        self.created_by = created_by

    def getDeliveryDate(self):
        from datetime import timedelta
        delivery_date = self.created_at + timedelta(days=8)
        return delivery_date

class Approval(CreatedCommon):
    order = models.ForeignKey("endorsers.Order", on_delete=models.CASCADE, null=True, blank=True)


class Application(CreatedCommon):
    note        = models.TextField()
    price       = models.FloatField()
    days        = models.IntegerField()
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_approved = models.OneToOneField(Approval, on_delete=models.SET_NULL, null=True, blank=True)

    def approve(self, approved_by):
        # creating order
        try:
            with transaction.atomic():
                new_order = Order()
                new_order.createFromApplication(self, approved_by)
                new_order.save()

                # creating approval object
                new_approval = Approval(
                    order = new_order,
                    created_by = approved_by
                )
                new_approval.save()

                # updating application object as APPROVED
                self.is_approved = new_approval
                self.save()

                # exit
                print("Successfully approved")
                return new_order
        except Exception as e:
            print(str(e))
            return False

    def save(self, *args, **kwargs):
        if self.project.created_by == self.created_by:
            raise Exception("You can't submit the request to your own project")
        super(Application, self).save(*args, **kwargs)