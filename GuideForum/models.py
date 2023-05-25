from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30, blank=True, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, default="1")
    text = models.TextField()
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    preview = models.ImageField(upload_to='previews/', default='previews/blank.png')
    likes = models.ManyToManyField(User, related_name='liked_topics', blank=True)

    def __str__(self):
        return self.title


class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return self.text[:50] + "..."
