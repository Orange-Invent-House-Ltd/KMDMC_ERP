from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in 
    using either their username or email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by username or email.
        The 'username' parameter can contain either a username or email.
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None

        try:
            # Try to find user by username or email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher to reduce timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # In case of duplicate (shouldn't happen with unique constraints)
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
