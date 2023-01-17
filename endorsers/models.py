from django.db import models
from organizations.models import CreatedCommon, Project, Location, SocialMedia
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
        

class Approval(CreatedCommon):
    pass


class Application(CreatedCommon):
    note        = models.TextField()
    price       = models.FloatField()
    days        = models.IntegerField()
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_approved = models.OneToOneField(Approval, on_delete=models.SET_NULL, null=True, blank=True)