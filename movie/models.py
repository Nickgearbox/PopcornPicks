from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)  # New field

    def save(self, *args, **kwargs):
        """Automatically store the user's full name"""
        if not self.full_name:
            self.full_name = self.user.get_full_name() or self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} in {self.group.name}"


class Poll(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    movie_name = models.CharField(max_length=200)
    movie_image = models.URLField(blank=True, null=True)  # Store movie poster URL
    movie_trailer = models.URLField(blank=True, null=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.movie_name} ({self.votes} votes)"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} voted for {self.poll.movie_name}"
    

