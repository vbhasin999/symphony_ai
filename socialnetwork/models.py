from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()

class Comment(models.Model):
    text = models.CharField(max_length=200)
    creator = models.ForeignKey(User,  default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    post = models.ForeignKey(Post,  default=None, on_delete=models.PROTECT)

class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length = 50)
    following = models.ManyToManyField(User, related_name='followers')


