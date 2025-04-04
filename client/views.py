from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django import views
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import *
from django.db.utils import IntegrityError

# Create your views here.

class IndexView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        return render(request, "client/index.html", {"user":user})
    

class ProfileView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        profile = CustomerModel.objects.filter(user=user)
        return render(request, "client/profile.html", {"profile":profile})