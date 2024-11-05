from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import os
from django.conf import settings
import django.utils


# Create your models here.


class ServiceUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    

def user_profile_image_path(instance, filename):
    # Get the username from the instance
    username = instance.username
    
    # Generate the path based on the username
    return os.path.join('user_profile_image', username, filename)


# def random_default_image():
#     # Assuming your default profile images are stored under 'default_profile_images' folder in S3 bucket
#     default_image_folder = 'assets/default_profile_images/'

#     # Get the storage instance
#     storage = S3Boto3Storage()

#     # List all files in the folder
#     files = storage.listdir(default_image_folder)[1]  # Index 1 gives list of files

#     # Filter out non-image files if necessary
#     image_files = [f for f in files if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') or f.lower().endswith('.png')]

#     # Select a random image from the list
#     random_image = random.choice(image_files)

#     # Construct the URL path to the randomly selected image

#     url = default_image_folder + random_image
#     return url


def user_profile_image_path(instance, filename):
    # Get the username from the instance
    username = instance.username
    
    # Generate the path based on the username
    return os.path.join('user_profile_image', username, filename)



class ServiceUser(AbstractBaseUser, PermissionsMixin):
    # user basic information
    email = models.EmailField(
        verbose_name="email",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to=user_profile_image_path, blank=True)
    introduction = models.TextField(blank=True)

    # Social Account Provider Type
    is_social_account = models.BooleanField(default=False)
    social_account_provider = models.CharField(max_length=100, blank=True, null=True)
    social_account_detail = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)




    #User Additional Information
    article_count = models.PositiveBigIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='user_subscribers')
    subscribing_user = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='user_subscribing', symmetrical=False)
    

    # Membership Account
    is_membership = models.BooleanField(default=False)
    was_membership = models.BooleanField(default=False)
    donation_message = models.CharField(blank=True, null=True, default=0)

    membership_renew_date = models.DateField(default=django.utils.timezone.now)
    membership_expire_date = models.DateField(default=django.utils.timezone.now)

    membership_donation_cash = models.PositiveIntegerField(default=0)

    # authentication_related_link_expire
    signup_verification_code = models.PositiveBigIntegerField(blank=True, null=True)
    email_verification_link_generated_at = models.DateTimeField(null=True, blank=True)
    password_reset_verification_code = models.PositiveBigIntegerField(blank=True, null=True)
    password_reset_link_generated_at = models.DateTimeField(null=True, blank=True)


    # Violation Restriction
    community_restriction = models.BooleanField(default=False)
    violation_detail_community = models.TextField(blank=True, null=True)
    

    # Statistics
    sign_up_date = models.DateTimeField(default=django.utils.timezone.now)
    last_active_date = models.DateTimeField(default=django.utils.timezone.now)

    objects = ServiceUserManager()


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    
    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    


class UserFCMToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=500, unique=True)

    # Notification Permission

    is_push_notification = models.BooleanField(default=True)

    is_article_notification = models.BooleanField(default=True)
    is_comment_notification = models.BooleanField(default=True)
    is_comment_reply_notification = models.BooleanField(default=True)

    is_donation_notification = models.BooleanField(default=True)
    is_donation_withdrawal_notification = models.BooleanField(default=True)

    is_announcement_notification = models.BooleanField(default=True)
    is_inquiry_notification = models.BooleanField(default=True)

