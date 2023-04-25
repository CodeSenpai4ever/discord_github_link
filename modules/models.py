from django.db import models


# Create your models here.
class DiscordUser(models.Model):
    user_id = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    access_token = models.CharField(max_length=100, null=False)
    refresh_token = models.CharField(max_length=100, null=False)
    expires_in = models.BigIntegerField(null=False)
