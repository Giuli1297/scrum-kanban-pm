import pytest as pytest
from django.test import TestCase

from django.contrib.auth.models import User
from django.test import TestCase
from projectmanager import views
from django.urls.base import reverse,resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from projectmanager.models import Proyecto,rol


class TestViews(TestCase):
    super(TestViews,cls).setUpClass()
