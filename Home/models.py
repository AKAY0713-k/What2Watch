from django.db import models
from django.contrib.auth.models import User
from django.db import models


# makemigrations-create changes and store  in a file
# migrate-apply the pending changes craeted by makemigrations

# Create your models here.
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    desc = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    upload_avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    contribution_points = models.IntegerField(default=0)
    role = models.CharField(max_length=20, default="Member")
    join_date = models.DateField(null=True, blank=True) 
    last_online = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    

class Drama(models.Model):
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True)
    country = models.CharField(max_length=50, default='Korea')  
    release_year = models.CharField(max_length=4, default='2000')
    episodes = models.IntegerField(default=1)
    rating = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    trailer_url = models.URLField(blank=True)
    type = models.CharField(max_length=50, default='Drama') 
    status = models.CharField(max_length=20, default='Completed')  
    genre = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
    

from django.db import models

class Actor(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, null=True, blank=True)
    born = models.DateField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dramas = models.TextField(null=True, blank=True)
    movies = models.TextField(null=True, blank=True)
    image = models.URLField(max_length=500) 

    def __str__(self):
        return self.name

# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

WATCH_STATUS_CHOICES = [
    ("currently_watching", "Currently Watching"),
    ("completed", "Completed"),
    ("on_hold", "On Hold"),
    ("dropped", "Dropped"),
    ("plan_to_watch", "Plan to Watch"),
]

CONTENT_TYPE_CHOICES = [
    ("drama", "Drama"),
    ("movie", "Movie"),
    ("variety", "Variety Show"),
]


mood_genre_map = {
    "happy": ["Comedy", "Romance", "Slice of Life"],
    "sad": ["Melodrama", "Tragedy", "Romance"],
    "excited": ["Action", "Thriller", "Adventure"],
    "scared": ["Horror", "Mystery"],
    "emotional": ["Drama", "Psychological"],
    "bored": ["Fantasy", "Sci-Fi", "Mystery"]
}


# models.py

class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=WATCH_STATUS_CHOICES)
    episodes_watched = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    added_on = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.status})"
