from django.db import models
from django.contrib.auth.models import User

# Admin profile model with complete fields
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    admin_role = models.CharField(max_length=50, blank=True, null=True)
    security_question = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Admin Profile"

