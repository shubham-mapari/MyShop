from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User

# Optional: separate profile model (can be used if needed)
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    shop_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

# Custom AdminUser model
class AdminUser(AbstractUser):
    mobile = models.CharField(max_length=15)
    shop_name = models.CharField(max_length=100)
    address = models.TextField()
    role = models.CharField(max_length=50)
    security_question = models.CharField(max_length=255)

    # Override groups and permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='adminuser_set',   # avoids clash with default User
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='adminuser_set',   # avoids clash with default User
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username
