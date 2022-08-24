# import jwt
# from django.conf import settings
# from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator
import uuid

# Create your models here.


class MyManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if password is None:
            raise TypeError('Superusers must have a password.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        db_index=True, max_length=255, unique=True, verbose_name='email address')
    first_name = models.CharField(
        max_length=150, null=False, blank=False, verbose_name='first name')
    last_name = models.CharField(
        max_length=150, null=False, blank=False, verbose_name='last name')
    password = models.CharField(
        max_length=128, null=False, blank=False, verbose_name='password')
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    regToken = models.UUIDField(default=uuid.uuid4, editable=False,
                                unique=True, verbose_name='token')
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyManager()

    def __str__(self):
        return self.first_name

    def get_full_name(self) -> str:
        return super().get_full_name()

    # @property
    # def token(self):
    #     return self._generate_jwt_token()

    # def _generate_jwt_token(self):
    #     """
    #     Generates a JSON Web Token that stores user's ID and has an expiry
    #     date set to 60 days.
    #     """
    #     time = datetime.now() + timedelta(minutes=1000)
    #     payload = {
    #         'id': self.pk,
    #         'expiryTime': int(time.strftime('%s'))
    #     }

    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    #     return token.decode('utf-8')
        
class Category(models.Model):
    cat_name = models.CharField(max_length=150, unique=True, null=False, blank=False)
    desription = models.TextField(null=False, blank=False)
    created_by = models.ForeignKey(User, related_name='staff_add', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.cat_name

class Store(models.Model):
    store_name = models.CharField(max_length=150, unique=True, null=False, blank=False)
    store_logo = models.ImageField(upload_to='StoreLogo/', unique=True)
    added_by = models.ForeignKey(User, related_name='staff_store_add', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.store_name


class SubCategory(models.Model):
    sub_cat_name = models.CharField(max_length=150, unique=True, null=False, blank=False)
    desription = models.TextField(null=False, blank=False)
    created_by = models.ForeignKey(User, related_name='staff_add_sub_cat', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.sub_cat_name


class Product(models.Model):
    prod_name = models.CharField(max_length=150, unique=True, null=False, blank=False)
    images = models.ImageField(upload_to='Product/', unique=True)
    desription = models.TextField(null=False, blank=False)
    count = models.IntegerField(null=False, blank=False, default=0)
    created_by = models.ForeignKey(User, related_name='staff_add_pro', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='pro_cat', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='sub_cat', on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.prod_name

    def get_product_count(self, product):
        return self.filter(prod_name = product).count()

# Number of times a product is saved
class Saves(models.Model):
    user = models.ForeignKey(User, related_name='user_wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_wishlist', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]


class NewSearch(models.Model):
    keyword = models.CharField(max_length=20, null=True)
    ip_address = models.CharField(max_length=20, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

