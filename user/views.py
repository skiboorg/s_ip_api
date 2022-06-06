import json
import time

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import create_random_string
from .serializers import *
from .models import *
from rest_framework import generics

from django.core.mail import send_mail, EmailMessage
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
import requests
from .services import *

from rest_framework.pagination import PageNumberPagination

import logging

logger = logging.getLogger(__name__)



class GetUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        result = False
        user = request.user
        if data['code'] == user.email_confirmation_code:
            user.set_password(data['password'])
            user.last_password_change = now()
            user.save()
            result = True
            logger.info(f'UID {user.id} {user.email} change password')
        else:
            logger.warning(f'UID {user.id} {user.email} enter wrong code while change password')
        return Response(result, status=200)


