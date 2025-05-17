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
    

class ProfileAddView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"
    
    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        mobile = get_object_or_404(MobileModel, user=user)
        items = {
            "code":user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "mobile":mobile.mobile,
        }
        form = ProfileAddForm(initial=items)
        context = {
            "form":form,
        }
        return render(request, "client/profile-add.html", context)
    
    def post(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        mobile = get_object_or_404(MobileModel, user=user)
        items = {
            "code":user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "mobile":mobile.mobile,
        }
        form = ProfileAddForm(request.POST, initial=items)
        context = {
            "form":form,
        }
        if form.is_valid():
            kind = form.cleaned_data.get("kind")
            brand = form.cleaned_data.get("brand")
            ceoname = form.cleaned_data.get("ceoname")
            company = form.cleaned_data.get("company")
            ncode = form.cleaned_data.get("ncode")
            phone = form.cleaned_data.get("phone")
            fax = form.cleaned_data.get("fax")
            email = form.cleaned_data.get("email")
            postalcode = form.cleaned_data.get("postalcode")
            address = form.cleaned_data.get("address")
            if kind == CustomerModel.KIND_REAL:
                customer = CustomerModel(
                    is_active=False,
                    kind=kind,
                    user=user,
                    brand=brand,
                    phone=phone,
                    fax=fax,
                    email=email,
                    postalcode=postalcode,
                    address=address,
                    user_created=user,
                    user_modified=user,
                )
            else:
                if not ncode:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای شناسه ملی باشد.")
                    return render(request, 'client/profile-add.html', {'form':form})
                elif not ceoname:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام مدیرعامل باشد.")
                    return render(request, 'client/profile-add.html', {'form':form})
                elif not company:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام شرکت یا سازمان باشد.")
                    return render(request, 'client/profile-add.html', {'form':form})
                else:
                    customer = CustomerModel(
                        is_active=False,
                        kind=kind,
                        user=user,
                        brand=brand,
                        ceoname=ceoname,
                        company=company,
                        ncode=ncode,
                        phone=phone,
                        fax=fax,
                        email=email,
                        postalcode=postalcode,
                        address=address,
                        user_created=user,
                        user_modified=user,
                    )
            try:
                customer.save()
            except IntegrityError:
                messages.error(request, f"قبلا نام تجاری {brand} با کدملی {user.username} ثبت شده است!")
                return redirect("client:profile-add")
            messages.success(request, f"حساب کاربری شما با نام تجاری {brand} با موفقیت ثبت شد.")
            return redirect("client:profile-add")
        return render(request, "client/profile-add.html", context)
    

class DocumentAddView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        documents = DocumentsModel.objects.filter(user=user)
        form = DocumentAddForm()
        context = {
            "documents":documents,
            "form":form,
        }
        return render(request, "client/document-add.html", context)
    
    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        documents = DocumentsModel.objects.filter(user=user)
        form = DocumentAddForm(request.POST, request.FILES)
        context = {
            "documents":documents,
            "form":form,
        }
        if form.is_valid():
            file = form.cleaned_data.get("file")
            document = DocumentsModel(
                file=file,
                state=DocumentsModel.STATE_WAIT,
                user=user,
                user_created=user,
                user_modified=user,
            )
            try:
                document.save()
            except:
                messages.error(request, "خطای سیستمی رخ داده است، دوباره سعی کنید!")
                return render(request, "client/document-add.html", context)
            messages.success(request, "مدرک شما با موفقیت بارگذاری شد.")
            return render(request, "client/document-add.html", context)
        return render(request, "client/document-add.html", context)


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
                "callbackURL":"https://portal.urmiafair.com/client/payment/done/",
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
        return render(request, "client/payment-create.html", {"form":form})
    

class PaymentDoneView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == "POST":
            invoiceid = request.POST.get("invoiceid")
            amount = request.POST.get("amount")
            tracenumber = request.POST.get("tracenumber")
            cardnumber = request.POST.get("cardnumber")
            issuerbank = request.POST.get("issuerbank")
            respcode = request.POST.get("respcode")
            respmsg = request.POST.get("respmsg")
            payload = request.POST.get("payload")
            rrn = request.POST.get("rrn")
            datepaid = request.POST.get("datePaid")
            digitalreceipt = request.POST.get("digitalreceipt")
            if respcode == 0:
                response = requests.post(
                    url="https://sepehr.shaparak.ir:8081/V1/PeymentApi/Advice",
                    data={
                        "digitalreceipt":digitalreceipt,
                        "Tid":Terminal_id,
                    }
                )
                response.json()
                if response["Status"] == "ok" and response["ReturnId"] == str(amount):
                    invoice = get_object_or_404(InvoiceModel, pk=int(invoiceid))
                    wallet = get_object_or_404(WalletModel, user=user)
                    pay = PaymentModel(
                        state=PaymentModel.STATE_IPG,
                        wallet=wallet,
                        invoice=invoice,
                        amount=int(amount),
                        cardnumber=cardnumber,
                        issuerbank=issuerbank,
                        rrn=rrn,
                        tracenumber=tracenumber,
                        digitalreceipt=digitalreceipt,
                        respcode=int(respcode),
                        respmsg=respmsg,
                        payload=payload,
                        datepaid=datepaid,
                        user_created=user,
                        user_modified=user,
                    )
                    try:
                        pay.save()
                    except IntegrityError:
                        return render(request, "client/error.html", {"error":"رسید دیجیتال تکراری است، این تراکنش قبلا انجام شده است!"})
                    total = int(wallet.cash) + int(amount)
                    wallet.cash = str(total)
                    wallet.save()
                    return render(request, "client/payment-done.html")
                return render(request, "client/error.html", {"error":response["Message"]})
            return render(request, "client/error.html", {"error":"تراکنش ناموفق!!"})
    

class RequestExhibitionView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)