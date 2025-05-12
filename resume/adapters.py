from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth import get_user_model

class NoEmailGithubAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin: SocialLogin):
        user = sociallogin.user
        if not user.email:
            # GitHub sometimes doesn't return email. Let's fake one.
            user.email = f"{user.username}@github.placeholder.com"
