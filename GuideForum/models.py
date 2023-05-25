from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_description = models.TextField(default="bio not added")
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/blank.png')

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=30, blank=True, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default="1")  # Update the owner field
    text = models.TextField()
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    preview = models.ImageField(upload_to='previews/', default='previews/blank.png')
    likes = models.ManyToManyField(User, related_name='liked_topics', blank=True)

    def __str__(self):
        return self.title


class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return self.text[:50] + "..."
