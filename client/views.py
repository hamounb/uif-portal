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
from crm.settings import Terminal_id, merchant_id
import zibal.zibal as zibal

# Create your views here.

    
def persian_digits_to_english(s:str):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translate_table = str.maketrans(persian_digits, english_digits)
    return s.translate(translate_table)


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
            ncode = persian_digits_to_english(form.cleaned_data.get("ncode"))
            phone = persian_digits_to_english(form.cleaned_data.get("phone"))
            fax = persian_digits_to_english(form.cleaned_data.get("fax"))
            email = form.cleaned_data.get("email")
            postalcode = persian_digits_to_english(form.cleaned_data.get("postalcode"))
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
            return redirect("client:profile")
        return render(request, "client/profile-add.html", context)
    

class ProfileEditView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request, pid):
        user = get_object_or_404(User, pk=request.user.id)
        profile = get_object_or_404(CustomerModel, pk=pid)
        mobile = get_object_or_404(MobileModel, user=user)
        items = {
            "kind":profile.kind,
            "code":user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "mobile":mobile.mobile,
            "brand":profile.brand,
            "company":profile.company,
            "ceoname":profile.ceoname,
            "ncode":profile.ncode,
            "phone":profile.phone,
            "fax":profile.fax,
            "email":profile.email,
            "postalcode":profile.postalcode,
            "address":profile.address,
        }
        form = ProfileAddForm(initial=items)
        context = {
            "form":form,
        }
        return render(request, "client/profile-add.html", context)
    
    def post(self, request, pid):
        user = get_object_or_404(User, pk=request.user.pk)
        profile = get_object_or_404(CustomerModel, pk=pid)
        mobile = get_object_or_404(MobileModel, user=user)
        items = {
            "kind":profile.kind,
            "code":user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "mobile":mobile.mobile,
            "brand":profile.brand,
            "company":profile.company,
            "ceoname":profile.ceoname,
            "ncode":profile.ncode,
            "phone":profile.phone,
            "fax":profile.fax,
            "email":profile.email,
            "postalcode":profile.postalcode,
            "address":profile.address,
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
            ncode = persian_digits_to_english(form.cleaned_data.get("ncode"))
            phone = persian_digits_to_english(form.cleaned_data.get("phone"))
            fax = persian_digits_to_english(form.cleaned_data.get("fax"))
            email = form.cleaned_data.get("email")
            postalcode = persian_digits_to_english(form.cleaned_data.get("postalcode"))
            address = form.cleaned_data.get("address")
            if kind == CustomerModel.KIND_REAL:
                profile.is_active = False
                profile.kind = CustomerModel.KIND_REAL
                profile.user = user
                profile.brand = brand
                profile.phone = phone
                profile.fax = fax
                profile.email = email
                profile.postalcode = postalcode
                profile.address = address
                profile.user_modified = user
                profile.save()
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
                    profile.is_active = False
                    profile.kind = CustomerModel.KIND_LEGAL
                    profile.user = user
                    profile.brand = brand
                    profile.ceoname = ceoname
                    profile.company = company
                    profile.ncode = ncode
                    profile.phone = phone
                    profile.fax = fax
                    profile.email = email
                    profile.postalcode = postalcode
                    profile.address = address
                    profile.user_modified = user
                    profile.save()
            messages.success(request, f"حساب کاربری شما با نام تجاری {brand} با موفقیت ویرایش شد.")
            return redirect("client:profile")
        return render(request, "client/profile-add.html", context)


class DocumentAddView(LoginRequiredMixin, views.View):
    login_url = "signin"

    def post(self, request, cid):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=cid)
        form = DocumentAddForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get("file")
            doc = DocumentsModel(
                customer=customer,
                file=file,
                user_created=user,
                user_modified=user,
            )
            doc.save()
            messages.success(request, "مدرک جدید با موفقیت بارگذاری شد.")
            return redirect("client:profile")
        messages.error(request, "خطای سیستمی رخ داده است، دوباره سعی کنید!")
        return redirect("client:profile")


class ExhibitionView(LoginRequiredMixin, views.View):
    login_url = "signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        profile = CustomerModel.objects.filter(Q(user=user) & Q(is_active=True))
        if not profile:
            return render(request, "client/permission.html")
        req = RequestModel.objects.filter(customer__user=user).order_by("-modified_date")
        context = {
            "req":req,
        }
        return render(request, "client/exhibition.html", context)
    

class RequestDocumentAddView(LoginRequiredMixin, views.View):
    login_url = "signin"

    def post(self, request, rid):
        user = get_object_or_404(User, pk=request.user.id)
        req = get_object_or_404(RequestModel, pk=rid)
        form = DocumentAddForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get("file")
            doc = RequestDocumentsModel(
                request=req,
                file=file,
                user_created=user,
                user_modified=user,
            )
            doc.save()
            if req.state == req.STATE_DENY:
                req.state = req.STATE_WAIT
                req.save()
            return redirect("client:exhibition")
        return redirect("client:exhibition")
        

class RequestAddView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        exhibition = ExhibitionModel.objects.filter(is_active=True)
        customer = CustomerModel.objects.filter(Q(user=user) & Q(is_active=True))
        if not customer:
            return render(request, "client/permission.html")
        form = RequestAddForm()
        context = {
            "form":form,
            "exhibition":exhibition,
            "customer":customer,
        }
        return render(request, "client/request-add.html", context)

    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        exhibition = ExhibitionModel.objects.filter(is_active=True)
        customer = CustomerModel.objects.filter(Q(user=user) & Q(is_active=True))
        form = RequestAddForm(request.POST)
        context = {
            "form":form,
            "exhibition":exhibition,
            "customer":customer,
        }
        if form.is_valid():
            exhib = form.cleaned_data.get("exhibition")
            cus = form.cleaned_data.get("customer")
            rules = form.cleaned_data.get("rules")
            description = form.cleaned_data.get("description")
            req = RequestModel(
                exhibition=ExhibitionModel.objects.get(pk=exhib),
                customer=CustomerModel.objects.get(pk=cus),
                rules=rules,
                description=description,
            )
            try:
                req.save()
            except IntegrityError:
                messages.error(request, f"درخواست شما برای {ExhibitionModel.objects.get(pk=exhib).title} با نام تجاری {CustomerModel.objects.get(pk=cus).brand} قبلا ثبت شده است!")
                return render(request, "client/request-add.html", context)
            messages.success(request, f"درخواست شما برای نمایشگاه {req.exhibition.title} با نام تجاری {req.customer.brand} با موفقیت ارسال شد.")
            return redirect("client:exhibition")
        return render(request, "client/request-add.html", context)


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
        payments = PaymentModel.objects.filter(invoice=invoice)
        try:
            mobile = MobileModel.objects.get(user=user)
        except MobileModel.DoesNotExist:
            mobile = "-"
        pre_amount = int(int(invoice.amount) / 2)
        cash = 0
        for i in payments:
            cash += i.amount
        amount = str(int(invoice.amount) - cash)
        context = {
            "invoice":invoice,
            "wallet":wallet,
            "mobile":mobile,
            "pre_amount":pre_amount,
            "payments":payments,
            "amount":amount,
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

    def get(self, request, iid, pay):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        callback_url = f"https://www.portal.urmiafair.com/client/payment/{invoice.pk}/done"
        zb = zibal.zibal(merchant_id, callback_url)
        amount = pay
        request_to_zibal = zb.request(amount, invoice.pk)
        track_id = request_to_zibal['trackId']
        if request_to_zibal['result'] == 100:
            return HttpResponseRedirect(f"https://gateway.zibal.ir/start/{track_id}")
        return render(request, "client/error.html")
    

class PaymentDoneView(views.View):
    login_url = "accounts:signin"

    def get(self, request, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        wallet = get_object_or_404(WalletModel, user=user)
        track_id = request.GET.get("trackId")
        callback_url = f"https://www.portal.urmiafair.com/client/payment/{invoice.pk}/done"
        zb = zibal.zibal(merchant_id, callback_url)
        verify_zibal = zb.verify(track_id)
        result = verify_zibal["refNumber"]
        if verify_zibal["result"] == 100 and verify_zibal["status"] == 1:
            payment = PaymentModel(
                state=PaymentModel.STATE_IPG,
                invoice=invoice,
                wallet=wallet,
                amount=int(verify_zibal["amount"]),
                tracenumber=str(verify_zibal["refNumber"]),
                cardnumber=verify_zibal["cardNumber"],
                respcode=int(verify_zibal["status"]),
                respmsg=verify_zibal["message"],
                datepaid=verify_zibal["paidAt"]
            )
            payment.save()
            payments = PaymentModel.objects.filter(invoice=invoice)
            total = 0
            for p in payments:
                total += p.amount
            if invoice.amount == str(total):
                invoice.state = InvoiceModel.STATE_PAID
                invoice.save()
            else:
                cash = int(wallet.cash)
                cash += int(payment.amount)
                wallet.cash = str(cash)
                wallet.save()
            messages.success(request, f"تراکنش شما با موفقیت انجام شد، شماره پیگیری: {str(result)}.")
            return render(request, "client/payment-done.html", {"code":"100"})
        elif verify_zibal["result"] == 100 and verify_zibal["status"] == 2:
            verify_zibal = zb.verify(track_id)
            if verify_zibal["status"] == 2:
                payment = PaymentModel(
                    state=PaymentModel.STATE_IPG,
                    invoice=invoice,
                    wallet=wallet,
                    amount=int(verify_zibal["amount"]),
                    tracenumber=str(verify_zibal["refNumber"]),
                    cardnumber=verify_zibal["cardNumber"],
                    respcode=int(verify_zibal["status"]),
                    respmsg=verify_zibal["message"],
                    datepaid=verify_zibal["paidAt"]
                )
                payment.save()
                payments = PaymentModel.objects.filter(invoice=invoice)
                total = 0
                for p in payments:
                    total += p.amount
                if invoice.amount == str(total):
                    invoice.state = InvoiceModel.STATE_PAID
                    invoice.save()
                else:
                    cash = int(wallet.cash)
                    cash += int(payment.amount)
                    wallet.cash = str(cash)
                    wallet.save()
                    messages.success(request, f"تراکنش شما با موفقیت انجام شد، شماره پیگیری: {str(result)}.")
                    return render(request, "client/payment-done.html", {"code":"100"})
            messages.error(request, "تراکنش شما ناموفق بوده است، هیچ پاسخی از بانک دریافت نشد!.")
            return render(request, "client/payment-done.html", {"code":"202"})
        else:
            messages.error(request, "تراکنش شما ناموفق بوده است، لطفا دوباره اقدام فرمایید.")
            return render(request, "client/payment-done.html", {"code":"202"})
    

class RequestExhibitionView(LoginRequiredMixin, views.View):
    login_url = "accounts:signin"

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        pass