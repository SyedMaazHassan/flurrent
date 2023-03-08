from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from organizations.models import Organization, Staff
from django.db import transaction
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Avg
import random, string
import uuid

# from endorsers.models import Endorser


# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Refer(models.Model):
    user_joined = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="user_joined"
    )
    invited_by = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="invited_by"
    )
    points = models.IntegerField(default=2)
    register_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    phone           = PhoneNumberField(null=True, blank=True)
    bio             = models.TextField(null=True, blank=True)
    email           = models.EmailField(unique=True)
    profile_pic     = models.ImageField(upload_to="profile_pics", default="profile_pics/default.png")
    is_staff_member = models.OneToOneField("organizations.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_member_object")
    is_organization = models.OneToOneField("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_object")
    is_endorser     = models.OneToOneField("endorsers.Endorser", on_delete=models.SET_NULL, null=True, blank=True, related_name="endorser_object")
    mode            = models.CharField(max_length=15, choices=[("endorser", "Endorser"), ("organization", "Organization")], default="organization")
    refer_id        = models.CharField(null=True, blank=True, max_length=8)

    def getAccount(self):
        from wallet.models import Account
        account = Account.objects.filter(user = self).first()
        return account

    def generate_unique_number(self):
        alphanumeric_chars = string.ascii_uppercase + string.digits 
        return ''.join(random.choice(alphanumeric_chars) for _ in range(10))

    def getFullName(self):
        return f"{self.first_name} {self.last_name}"

    def getReviews(self, type):
        all_reviews = Review.objects.filter(created_for=self, type=type)
        count = all_reviews.count()
        average = 0
        if count > 0:
            total_aggr = all_reviews.aggregate(Avg("star"))
            average = round(total_aggr["star__avg"], 1)

        return {"list": all_reviews, "count": count, "average": average}

    def getOrgReviews(self):
        return self.getReviews("organization")

    def getEndorserReviews(self):
        return self.getReviews("endorser")

    def createSocialMedia(self, social_media=None):
        from organizations.models import SocialMedia

        if social_media:
            new_social_media = SocialMedia.objects.create(
                facebook=social_media["facebook"],
                youtube=social_media["youtube"],
                tiktok=social_media["tiktok"],
                instagram=social_media["instagram"],
                website=social_media["website"],
            )
            social_media = new_social_media
        return social_media

    def createLocation(self, latitude, longitude):
        from organizations.models import Location

        new_location = Location.objects.create(latitude=latitude, longitude=longitude)
        return new_location

    def createEndorser(
        self,
        tagline,
        followers,
        description=None,
        interests=None,
        location=None,
        social_media=None,
    ):
        from endorsers.models import Endorser

        with transaction.atomic():
            # create new Location object
            if location:
                location = self.createLocation(location[0], location[1])

            # create new Social media
            if social_media:
                social_media = self.createSocialMedia(social_media)

            # create new Endorser
            new_endorser = Endorser.objects.create(
                tagline=tagline,
                description=description,
                followers=followers,
                interests=interests,
                location=location,
                social_media=social_media,
                created_by=self,
            )

            # updating the user object
            self.is_endorser = new_endorser
            self.mode = "endorser"
            self.save()
            print("Endorser created")
            return new_endorser

    def createOrganization(
        self, name, type, logo=None, description=None, location=None, social_media=None
    ):
        from organizations.models import Location, Organization, SocialMedia

        with transaction.atomic():
            # create new Location object
            if location:
                location = self.createLocation(location[0], location[1])
            # create new Social media
            if social_media:
                social_media = self.createSocialMedia(social_media)
            # Creating organization
            new_organization = Organization(
                name=name,
                description=description,
                type=type,
                location=location,
                social_media=social_media,
                created_by=self,
            )
            if logo:
                new_organization.logo = logo

            new_organization.save()
            self.is_organization = new_organization
            self.mode = "organization"
            self.save()

            return new_organization

            print("Organization created")

    def getRefers(self):
        return Refer.objects.filter(invited_by=self)

    def getInviteLink(self):
        base_url = "http://127.0.0.1:8000"
        return f"{base_url}/authentication/signup?refer_id={self.refer_id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.refer_id = self.generate_unique_number()
        super().save(*args, **kwargs)





# Create your models here.
class Review(models.Model):
    feedback = models.TextField()
    star = models.IntegerField()
    type = models.CharField(
        max_length=20,
        choices=[("organization", "Organization"), ("endorser", "Endorser")],
    )
    created_for = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="receiver"
    )
    created_by = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="sender"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.created_for == self.created_by:
            raise Exception("You can't submit the review to yourself")
        super(Review, self).save(*args, **kwargs)
