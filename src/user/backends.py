from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in 
    using their email address.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate user by email.
        The 'email' parameter must contain an email address.
        """
        if email is None:
            email = kwargs.get(User.EMAIL_FIELD)

        if email is None or password is None:
            return None

        try:
            # Try to find user by email
            user = User.objects.get(
                Q(email__iexact=email)
            )
        except User.DoesNotExist:
            # Run the default password hasher to reduce timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # In case of duplicate (shouldn't happen with unique constraints)
            user = User.objects.filter(
                Q(email__iexact=email)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
