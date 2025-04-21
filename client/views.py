from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django import views
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import *
from accounts.models import MobileModel
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
        try:
            mobile = MobileModel.objects.get(user=user)
        except MobileModel.DoesNotExist:
            mobile = ""
            return render(request, "client/profile.html", {"profile":profile, "mobile":mobile})
        return render(request, "client/profile.html", {"profile":profile, "mobile":mobile})
    

# class ExhibitionView(LoginRequiredMixin, views.View):
#     login_url = "accounts:signin"

#     def get(self, request):
#         user = get_object_or_404(User, pk=request.user.id)


class InvoiceView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        invoices = InvoiceModel.objects.filter(customer__user=user)
        context = {
            "invoices":invoices,
        }
        return render(request, "client/invoice.html", context)
    

class InvoiceDetailsView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        valet = get_object_or_404(ValetModel, user=user)
        context = {
            "invoice":invoice,
            "valet":valet,
        }
        return render(request, "client/invoice-details.html", context)