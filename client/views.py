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
import requests
from crm.settings import Terminal_id

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
        wallet = get_object_or_404(WalletModel, user=user)
        try:
            mobile = MobileModel.objects.get(user=user)
        except MobileModel.DoesNotExist:
            mobile = "-"
        context = {
            "invoice":invoice,
            "wallet":wallet,
            "mobile":mobile,
        }
        return render(request, "client/invoice-details.html", context)
    

class PaymentListView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        payments = PaymentModel.objects.filter(wallet__user=user)
        return render(request, "client/payment-list.html", {"payments":payments})
    

class PaymentCreateView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        ref = request.META.get('HTTP_REFERER')
        response = requests.post(
            url='https://sepehr.shaparak.ir:8081/V1/PeymentApi/GetToken',
            data={
                "TerminalID":Terminal_id,
                "Amount":f"{invoice.amount}",
                "InvoiceID":f"{invoice.pk}",
                "callbackURL":"https://portal.urmiafair.com/client/payment/advice",
                "payload":""
            }
        )
        if response.ok:
            token = response.json()
            if token['Status'] == 0:
                access_token = token['Accesstoken']
                form = PaymentCreateForm(initial={"TerminalID":Terminal_id, "token":access_token})
                return render(request, "client/payment-create.html", {"form":form})
            return HttpResponseRedirect(ref)
        return HttpResponseRedirect(ref)
    

class PaymentDoneView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def post(self, request):
        if request.method == "POST":
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
             = request.POST.get("")
    

class RequestExhibitionView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)