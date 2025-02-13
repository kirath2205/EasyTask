from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

class Auth(AbstractUser):
    mobile_number = PhoneNumberField(null=False, blank=False, unique=True)
    email = models.EmailField(unique=True)

#
# @receiver(post_save, sender=Auth)
# def create_profile_entry(sender, instance, created, **kwargs):
#     if created:
#         profile = Profile.objects.create(user=instance)
#         UserToImageAttachment.objects.create(user_profile = profile)
