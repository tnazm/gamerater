from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    cover = models.URLField(null=True, blank=True)
    first_release_date = models.DateField(blank=True, null=True)
    genres = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    aggregated_rating = models.IntegerField(default=0, blank=True, null=True)
    developer = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ['id']


class User(AbstractUser):
    games = models.ManyToManyField(Game, through="GameRelationship")


class GameRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_backlog = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    journal_entry = models.CharField(max_length=10000, blank=True)
    time_played = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_rel"),
        ]
        ordering = ['id']
