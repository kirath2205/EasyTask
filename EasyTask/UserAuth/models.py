from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Auth(AbstractUser):
    username = models.CharField(max_length=100)
    mobile_number = PhoneNumberField()
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
#
# @receiver(post_save, sender=Auth)
# def create_profile_entry(sender, instance, created, **kwargs):
#     if created:
#         profile = Profile.objects.create(user=instance)
#         UserToImageAttachment.objects.create(user_profile = profile)
