from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django import views
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.contrib import messages
from client.models import *
from accounts.models import MobileModel
from django.db.utils import IntegrityError
from accounts.payamak import send_sms

# Create your views here.
    
def persian_digits_to_english(s:str):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translate_table = str.maketrans(persian_digits, english_digits)
    return s.translate(translate_table)


class Test(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = []

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        print(user.get_all_permissions())
        if user.get_all_permissions():
            print("all:yes")
        print("--------")
        print(user.get_user_permissions())
        if user.get_user_permissions():
            print("user:yes")
        return render(request, 'office/test.html')
    

class HomeView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_customermodel']

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        customer = CustomerModel.objects.filter(is_active=True).order_by('-created_date')[:7]
        payment = PaymentModel.objects.all().order_by('-created_date')[:7]
        exhibition = ExhibitionModel.objects.filter(is_active=True)
        context = {
            'customer':customer,
            'payment':payment,
            'exhibition':exhibition,
            'user':user,
        }
        return render(request, 'office/home.html', context)
    

class UserAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_usermodel']

    def get(self, request):
        form = UserAddForm()
        return render(request, 'office/user-add.html', {'form':form})
    
    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            code = persian_digits_to_english(form.cleaned_data.get('code'))
            mobile = persian_digits_to_english(form.cleaned_data.get('mobile'))
            is_active = form.cleaned_data.get('is_active')
            is_staff = form.cleaned_data.get('is_staff')
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=code,
            )
            user.is_active = is_active
            user.is_staff = is_staff
            user.set_password(mobile)
            try:
                user.save()
            except IntegrityError:
                messages.error(request, f"کاربر با کدملی {code} قبلاً ثبت شده است!")
                return render(request, 'office/user-add.html', {'form':form})
            messages.success(request, f"کابر جدید با کدملی {code} با موفقیت ثبت شد.")
            return redirect('office:user-add')
        return render(request, 'office/user-add.html', {'form':form})

    
class CustomerListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_customermodel']

    def get(self, request):
        customer = CustomerModel.objects.filter(is_active=True).order_by('-created_date')
        mobile = MobileModel.objects.all()
        wallet = WalletModel.objects.all()
        context = {
            'customer':customer,
            "mobile":mobile,
            "wallet":wallet,
            }
        return render(request, 'office/customer-list.html', context)
    

class DeactiveCustomerListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_customermodel']

    def get(self, request):
        customer = CustomerModel.objects.filter(is_active=False).order_by('-created_date')
        mobiles = MobileModel.objects.all()
        context = {
            'customer':customer,
            'mobiles':mobiles,
            }
        return render(request, 'office/deactive-customer-list.html', context)
    

class CustomerAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_customermodel']

    def get(self, request):
        form = CustomerAddForm()
        return render(request, 'office/customer-add.html', {'form':form})
    
    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        form = CustomerAddForm(request.POST)
        submit_type = request.POST.get('submit_type')
        if form.is_valid():
            kind = form.cleaned_data.get("kind")
            sid = form.cleaned_data.get("sid")
            if sid:
                sid = sid
            else:
                sid = None
            is_active = form.cleaned_data.get("is_active")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            code = persian_digits_to_english(form.cleaned_data.get("code"))
            brand = form.cleaned_data.get("brand")
            ceoname = form.cleaned_data.get("ceoname")
            company = form.cleaned_data.get("company")
            ncode = persian_digits_to_english(form.cleaned_data.get("ncode"))
            mobile = persian_digits_to_english(form.cleaned_data.get("mobile"))
            phone = persian_digits_to_english(form.cleaned_data.get("phone"))
            fax = persian_digits_to_english(form.cleaned_data.get("fax"))
            email = form.cleaned_data.get("email")
            postalcode = persian_digits_to_english(form.cleaned_data.get("postalcode"))
            address = form.cleaned_data.get("address")
            if kind == "legal":
                if not ncode:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای شناسه ملی باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                elif not ceoname:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام مدیرعامل باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                elif not company:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام شرکت یا سازمان باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                else:
                    try:
                        cus = User.objects.get(username=code)
                    except User.DoesNotExist:
                        new = User(username=code)
                        new.first_name = first_name
                        new.last_name = last_name
                        new.set_password(mobile)
                        new.save()
                        v = WalletModel(user=new)
                        v.save()
                        m = MobileModel(user=new, mobile=mobile)
                        m.save()
                        obj = CustomerModel(
                            kind=kind,
                            sid=sid,
                            is_active=is_active,
                            brand=brand,
                            ceoname=ceoname,
                            company=company,
                            ncode=ncode,
                            phone=phone,
                            fax=fax,
                            email=email,
                            postalcode=postalcode,
                            address=address
                        )
                        obj.user = new
                        obj.user_modified = user
                        obj.user_created = user
                        try:
                            obj.save()
                        except IntegrityError:
                            messages.error(request, "این اطلاعات قبلاً ثبت شده است!")
                            return render(request, 'office/customer-add.html', {'form':form})
                        messages.success(request, f"مشتری حقوقی با نام تجاری {brand} با موفقیت ثبت شد.")
                        if submit_type == "save":
                            return redirect('office:customer-list')
                        return redirect("office:customer-add")
                    obj = CustomerModel(
                        kind=kind,
                        sid=sid,
                        is_active=is_active,
                        brand=brand,
                        ceoname=ceoname,
                        company=company,
                        ncode=ncode,
                        phone=phone,
                        fax=fax,
                        email=email,
                        postalcode=postalcode,
                        address=address
                    )
                    obj.user = cus
                    obj.user_modified = user
                    obj.user_created = user
                    try:
                        wallet = WalletModel.objects.get(user=cus)
                    except WalletModel.DoesNotExist:
                        wallet = WalletModel(user=cus)
                        wallet.save()
                    try:
                        m = MobileModel.objects.get(user=cus)
                        m.mobile = mobile
                        m.save()
                    except MobileModel.DoesNotExist:
                        m = MobileModel(user=cus, mobile=mobile)
                        m.save()
                    try:
                        obj.save()
                    except IntegrityError:
                        messages.error(request, "این اطلاعات قبلاً ثبت شده است!")
                        return render(request, 'office/customer-add.html', {'form':form})
                    messages.success(request, f"مشتری حقوقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                    if submit_type == "save":
                        return redirect('office:customer-list')
                    return redirect("office:customer-add")
            else:
                try:
                    cus = User.objects.get(username=code)
                except User.DoesNotExist:
                    new = User(username=code)
                    new.first_name = first_name
                    new.last_name = last_name
                    new.set_password(mobile)
                    new.save()
                    v = WalletModel(user=new)
                    v.save()
                    m = MobileModel(user=new, mobile=mobile)
                    m.save()
                    obj = CustomerModel(
                        kind=kind,
                        sid=sid,
                        is_active=is_active,
                        brand=brand,
                        ceoname=ceoname,
                        company=company,
                        ncode=ncode,
                        phone=phone,
                        fax=fax,
                        email=email,
                        postalcode=postalcode,
                        address=address
                    )
                    obj.user = new
                    obj.user_modified = user
                    obj.user_created = user
                    try:
                        obj.save()
                    except IntegrityError:
                        messages.error(request, "این اطلاعات قبلاً ثبت شده است!1")
                        return render(request, 'office/customer-add.html', {'form':form})
                    messages.success(request, f"مشتری حقیقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                    if submit_type == "save":
                        return redirect('office:customer-list')
                    return redirect("office:customer-add")
                obj = CustomerModel(
                    kind=kind,
                    sid=sid,
                    is_active=is_active,
                    brand=brand,
                    ceoname="",
                    company="",
                    ncode="",
                    phone=phone,
                    fax=fax,
                    email=email,
                    postalcode=postalcode,
                    address=address
                )
                obj.user = cus
                obj.user_modified = user
                obj.user_created = user
                try:
                    obj.save()
                except IntegrityError:
                    messages.error(request, "این اطلاعات قبلاً ثبت شده است!2")
                    return render(request, 'office/customer-add.html', {'form':form})
                messages.success(request, f"مشتری حقیقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                try:
                    wallet = WalletModel.objects.get(user=cus)
                except WalletModel.DoesNotExist:
                    wallet = WalletModel(user=cus)
                    wallet.save()
                try:
                    m = MobileModel.objects.get(user=cus)
                    m.mobile = mobile
                    m.save()
                except MobileModel.DoesNotExist:
                    m = MobileModel(user=cus)
                    m.mobile = mobile
                    m.save()
                if submit_type == "save":
                    return redirect('office:customer-list')
                return redirect("office:customer-add")
        return render(request, 'office/customer-add.html', {'form':form})
    

class CustomerChangeView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_customermodel']

    def get(self, request, cid):
        query = Q(pk=cid) & Q(is_active=True)
        customer = get_object_or_404(CustomerModel, query)
        mobile = get_object_or_404(MobileModel, user=customer.user)
        form = CustomerChangeForm(instance=customer)
        form2 = DocumentForm()
        context = {
            'form':form,
            'form2':form2,
            'customer':customer,
            'mobile':mobile,
        }
        return render(request, 'office/customer-change.html', context)
    
    def post(self, request, cid):
        query = Q(pk=cid) & Q(is_active=True)
        customer = get_object_or_404(CustomerModel, query)
        mobile = get_object_or_404(MobileModel, user=customer.user)
        user = get_object_or_404(User, pk=request.user.id)
        form = CustomerChangeForm(request.POST, instance=customer)
        context = {
            'form':form,
            'customer':customer,
            'mobile':mobile,
        }
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.kind == "legal":
                if not obj.ncode:
                    messages.error(request, f"مشارکت کننده با نوع حقوقی باید دارای شناسه ملی باشد.")
                    return redirect('office:customer-change', cid=customer.pk)
                elif not obj.ceoname:
                    messages.error(request, f"مشارکت کننده با نوع حقوقی باید دارای نام مدیرعامل باشد.")
                    return redirect('office:customer-change', cid=customer.pk)
                elif not obj.company:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام شرکت یا سازمان باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                else:
                    obj.user_modified = user
                    obj.save()
                    messages.success(request, f"اطلاعات {obj.brand} بروزرسانی شد.")
                    return render(request, 'office/customer-change.html', context)
            else:
                obj.ceoname = ''
                obj.ncode = ''
                obj.user_modified = user
                obj.save()
                messages.success(request, f"اطلاعات {obj.brand} بروزرسانی شد.")
                return render(request, 'office/customer-change.html', context)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, 'office/customer-change.html', context)


class ProfileAcceptView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_customermodel']

    def get(self, request, pid):
        profile = get_object_or_404(CustomerModel, pk=pid)
        mobile = get_object_or_404(MobileModel, user=profile.user)
        profile.is_active = True
        profile.save()
        ref = request.META.get('HTTP_REFERER')
        messages.success(request, f"مشارکت کننده با نام تجاری {profile.brand} با موفقیت تایید شد.")
        send_sms(id=330570, mobile=f"{mobile.mobile}", args=[profile.brand])
        return redirect(ref)
    

class ProfileDenyView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_customermodel']

    def get(self, request, pid):
        profile = get_object_or_404(CustomerModel, pk=pid)
        mobile = get_object_or_404(MobileModel, user=profile.user)
        profile.is_active = False
        profile.save()
        ref = request.META.get('HTTP_REFERER')
        messages.erro(request, f"مشارکت کننده با نام تجاری {profile.brand} تایید نشد!")
        send_sms(id=330867, mobile=f"{mobile.mobile}", args=[profile.brand])
        return redirect(ref)
    

class CustomerExhibitionView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel']

    def get(self , request, id):
        customer = get_object_or_404(CustomerModel, pk=id)
        invoice = InvoiceModel.objects.filter(Q(customer=customer) & Q(is_active=True)).order_by("-created_date")
        form = CustomerToExhibitionForm()
        context = {
            'customer':customer,
            'form':form,
            'invoice':invoice,
        }
        return render(request, "office/customer-exhibition.html", context)
    
    def post(self, request, id):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=id)
        mobile = get_object_or_404(MobileModel, user=customer.user)
        invoice = InvoiceModel.objects.filter(Q(customer=customer) & Q(is_active=True)).order_by("-created_date")
        wallet = get_object_or_404(WalletModel, user=customer.user)
        form = CustomerToExhibitionForm(request.POST)
        context = {
            'customer':customer,
            'form':form,
            'invoice':invoice,
        }
        if form.is_valid():
            exhibition = form.cleaned_data.get("exhibition")
            kind = form.cleaned_data.get("kind")
            area = persian_digits_to_english(form.cleaned_data.get("area"))
            discount = persian_digits_to_english(form.cleaned_data.get("discount"))
            booth_number = persian_digits_to_english(form.cleaned_data.get("booth_number"))
            invoice_n = InvoiceModel(
                customer=customer,
                wallet=wallet,
                exhibition=exhibition,
                booth_number=booth_number,
                area=area,
                price="0",
                value_added="0",
                amount="0",
                discount=discount,
                user_created=user,
            )
            try:
                invoice_n.save()
            except IntegrityError:
                messages.error(request, f"مشارکت کننده {customer.brand} قبلاً ثبت نام شده است!")
                return render(request, "office/customer-exhibition.html", context)
            exh = get_object_or_404(ExhibitionModel, pk=invoice_n.exhibition.pk)
            if kind == CustomerToExhibitionForm.KIND_PERCENT:
                if int(discount) > 100:
                    messages.error(request, "مقدار تخفیف با نوع درصد نباید از 100 بیشتر باشد!")
                    return render(request, "office/customer-exhibition.html", context)
                total = (int(area) * int(exh.price)) + float(int(exh.value_added) * (int(area) * int(exh.price))) / 100
                amount = int(total) - float(int(total) * int(discount)) /100
            else:
                total = (int(area) * int(exh.price)) + float(int(exh.value_added) * (int(area) * int(exh.price))) / 100
                amount = int(total) - float(int(total) * int(discount)) /100
            invoice_n.price = exh.price
            invoice_n.value_added = exh.value_added
            invoice_n.amount = int(amount)
            invoice_n.save()
            messages.success(request, f"مشارکت کننده {customer.brand} در {exh.title} با موفقیت ثبت‌نام شد.")
            send_sms(id=234357, mobile=f"{mobile.mobile}", args=[invoice_n.exhibition.title])
            return redirect("office:customer-exhibition", id=customer.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, "office/customer-exhibition.html", context)
    

class CustomerExhibitionEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_invoicemodel']

    def get(self , request, id):
        invo = get_object_or_404(InvoiceModel, pk=id)
        if invo.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"{invo.customer.brand} در {invo.exhibition.title} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:customer-exhibition", id=invo.customer.pk)
        init_data = {
            "exhibition":invo.exhibition,
            "booth_number":invo.booth_number,
            "area":invo.area,
            "discount":invo.discount,
        }
        invo_id = invo.pk
        invoice = InvoiceModel.objects.filter(Q(customer=invo.customer) & Q(is_active=True)).order_by("-created_date")
        form = CustomerToExhibitionForm(initial=init_data)
        context = {
            'invoice':invoice,
            'form':form,
            'invo':invo,
            'invo_id':invo_id,
        }
        return render(request, "office/customer-exhibition.html", context)
    
    def post(self, request, id):
        user = get_object_or_404(User, pk=request.user.id)
        invo = get_object_or_404(InvoiceModel, pk=id)
        mobile = get_object_or_404(MobileModel, user=invo.customer.user)
        if invo.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"{invo.customer.brand} در {invo.exhibition.title} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:customer-exhibition", id=invo.customer.pk)
        invoice = InvoiceModel.objects.filter(Q(customer=invo.customer) & Q(is_active=True)).order_by("-created_date")
        form = CustomerToExhibitionForm(request.POST)
        context = {
            'form':form,
            'invoice':invoice,
            'invo':invo,
        }
        if form.is_valid():
            exhibition = form.cleaned_data.get("exhibition")
            area = persian_digits_to_english(form.cleaned_data.get("area"))
            discount = persian_digits_to_english(form.cleaned_data.get("discount"))
            booth_number = persian_digits_to_english(form.cleaned_data.get("booth_number"))
            kind = form.cleaned_data.get("kind")
            invo.exhibition = exhibition
            invo.booth_number = booth_number
            invo.area = area
            invo.discount = discount
            try:
                invo.save()
            except IntegrityError:
                messages.error(request, f"مشارکت کننده {invo.customer.brand} قبلاً ثبت نام شده است!")
                return render(request, "office/customer-exhibition.html", context)
            exh = get_object_or_404(ExhibitionModel, pk=invo.exhibition.pk)
            if kind == CustomerToExhibitionForm.KIND_PERCENT:
                total = (int(area) * int(exh.price))
                total_v = int(total) - float(int(total) * int(discount)) /100
            else:
                total = (int(area) * int(exh.price))
                total_v = int(total) - int(discount)
            amount = int(total_v) + float(int(exh.value_added) * int(total_v)) / 100
            invo.price = exh.price
            invo.value_added = exh.value_added
            invo.amount = int(amount)
            invo.user_modified = user
            try:
                invo.save()
            except IntegrityError:
                messages.error(request, f"مشارکت کننده {invo.customer.brand} قبلاً ثبت نام شده است!")
                return render(request, "office/customer-exhibition.html", context)
            messages.success(request, f"مشارکت کننده {invo.customer.brand} در {exh.title} با موفقیت ویرایش شد.")
            send_sms(id=234357, mobile=f"{mobile.mobile}", args=[invo.exhibition.title])
            return redirect("office:customer-exhibition", id=invo.customer.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, "office/customer-exhibition.html", context)


class DocumentsAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_documentsmodel']

    def post(self, request, id):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=id)
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            obj = DocumentsModel(
                is_active = True,
                state = DocumentsModel.STATE_ACCEPT,
                file = file,
                user_created = user,
                customer = customer,
                description = "",
            )
            obj.save()
            messages.success(request, f"مدرک شما با موفقیت بارگذاری شد!")
            return redirect('office:customer-documents', cid=customer.pk)
        return redirect('office:customer-documents', cid=customer.pk)
    

class DocumentsDelView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.delete_documentsmodel']

    def get(self, request, fid):
        file = get_object_or_404(DocumentsModel, pk=fid)
        file.file.delete(save=True)
        file.delete()
        ref = request.META.get('HTTP_REFERER')
        messages.success(request, "مدرک انتخابی شما با موفقیت حذف شد.")
        return redirect(ref)
    

class DocumentsAcceptView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_documentsmodel']

    def get(self, request, fid):
        file = get_object_or_404(DocumentsModel, pk=fid)
        file.state = DocumentsModel.STATE_ACCEPT
        file.save()
        file.customer.is_active = True
        file.customer.save()
        ref = request.META.get('HTTP_REFERER')
        messages.success(request, f"مشارکت کننده با نام تجاری {file.customer.brand} با موفقیت تایید شد.")
        return redirect(ref)
    

class DocumentsDenyView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_documentsmodel']

    def get(self, request, fid):
        file = get_object_or_404(DocumentsModel, pk=fid)
        file.state = DocumentsModel.STATE_DENY
        file.save()
        ref = request.META.get('HTTP_REFERER')
        messages.warning(request, f"مدرک مشارکت کننده با نام تجاری {file.customer.company} به حالت تعلیق تغییر یافت!")
        return redirect(ref)



class DocumentListView(PermissionRequiredMixin, views.View):
    login_url = "accounts:signin"
    permission_required = ['client.view_documentsmodel']

    def get(self, request, cid):
        customer = get_object_or_404(CustomerModel, pk=cid)
        docs = DocumentsModel.objects.filter(customer__pk=cid).order_by("-created_date")
        req_docs = RequestDocumentsModel.objects.filter(request__customer__pk=cid)
        form = DocumentForm()
        context = {
            "docs":docs,
            "req_docs":req_docs,
            "form":form,
            "customer":customer,
        }
        return render(request, "office/document-list.html", context)
    
    def post(self, request, cid):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=cid)
        docs = DocumentsModel.objects.filter(customer__pk=cid).order_by("-created_date")
        req_docs = RequestDocumentsModel.objects.filter(request__customer__pk=cid)
        form = DocumentForm(request.POST, request.FILES)
        context = {
            "docs":docs,
            "req_docs":req_docs,
            "form":form,
            "customer":customer,
        }
        if form.is_valid():
            file = form.cleaned_data['file']
            obj = DocumentsModel(
                is_active = True,
                state = DocumentsModel.STATE_ACCEPT,
                file = file,
                user_created = user,
                customer = customer,
                description = "",
            )
            obj.save()
            messages.success(request, f"مدرک شما با موفقیت بارگذاری شد!")
            return render(request, "office/document-list.html", context)
        return render(request, "office/document-list.html", context)
    

class InvoiceListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_invoicemodel']

    def get(self, request):
        invoices = InvoiceModel.objects.all().order_by('-modified_date')
        return render(request, 'office/invoice-list.html', {'invoices':invoices})
    

class InvoiceRemoveView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['clent.delete_invoicemodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if invoice.state == InvoiceModel.STATE_UNPAID:
            invoice.is_active = False
            invoice.save()
            ref = request.META['HTTP_REFERER']
            messages.error(request, f"مشارکت کننده {invoice.customer.brand} از نمایشگاه {invoice.exhibition.title} حذف شد.")
            return HttpResponseRedirect(ref)
        messages.error(request, f"مشارکت کننده {invoice.customer.brand} تسویه حساب شده است و قابلیت حذف ندارد.")
        return HttpResponseRedirect(ref)
    

class InvoiceEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_invoicemodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"{invoice.customer.brand} در {invoice.exhibition.title} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:invoice-list")
        item = {
            "is_active":invoice.is_active,
            "wallet":invoice.wallet,
            "exhibition":invoice.exhibition,
            "booth_number":invoice.booth_number,
            "area":invoice.area,
            "discount":invoice.discount,
        }
        form = InvoiceEditForm(initial=item)
        context = {
            "invoice":invoice,
            "form":form,
        }
        return render(request, 'office/invoice-edit.html', context)
    
    def post(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"{invoice.customer.brand} در {invoice.exhibition.title} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:invoice-list")
        item = {
            "is_active":invoice.is_active,
            "wallet":invoice.wallet,
            "exhibition":invoice.exhibition,
            "booth_number":invoice.booth_number,
            "area":invoice.area,
            "discount":invoice.discount,
        }
        form = InvoiceEditForm(request.POST, initial=item)
        user = get_object_or_404(User, pk=request.user.id)
        if form.is_valid():
            is_active = form.cleaned_data.get("is_active")
            wallet = form.cleaned_data.get("wallet")
            exhibition = form.cleaned_data.get("exhibition")
            booth_number = persian_digits_to_english(form.cleaned_data.get("booth_number"))
            area = persian_digits_to_english(form.cleaned_data.get("area"))
            discount = persian_digits_to_english(form.cleaned_data.get("discount"))
            invoice.is_active = is_active
            invoice.wallet = wallet
            invoice.exhibition = exhibition
            invoice.booth_number = booth_number
            invoice.area = area
            invoice.discount = discount
            invoice.save()
            e_p = invoice.exhibition.price
            e_v = invoice.exhibition.value_added
            total = int(e_p) * int(area) - float(int(e_p) * int(area) * int(discount)) / 100
            amount = int(total) + float(int(total) * int(e_v)) /100
            invoice.value_added = str(e_v)
            invoice.price = str(e_p)
            invoice.amount = str(int(amount))
            invoice.user_modified = user
            invoice.save()
            messages.success(request, f'فاکتور برای مشارکت کننده {invoice.exhibition.title} با نام تجاری {invoice.customer.company} با موفقیت ویرایش شد.')
            return render(request, 'office/invoice-edit.html', {'form':form})
        return render(request, 'office/invoice-edit.html', {'form':form})
    

class PaymentListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_paymentmodel']

    def get(self, request):
        payments = PaymentModel.objects.all().order_by("-created_date")
        context = {
            "payments":payments,
        }
        return render(request, "office/payment-list.html", context)
    

class PaymentAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_paymentmodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        payments = PaymentModel.objects.filter(invoice=invoice)
        total = 0
        for i in payments:
            total += int(i.amount)
        if int(invoice.amount) - total < 0:
            debit = 0
            credit = total - int(invoice.amount)
        elif int(invoice.amount) - total > 0:
            debit = int(invoice.amount) - total
            credit = 0
        else:
            debit = 0
            credit = 0
        form = PaymentAddForm()
        context = {
            "invoice":invoice,
            "form":form,
            "payments":payments,
            "total":total,
            "debit":debit,
            "credit":credit,
        }
        return render(request, "office/payment-add.html", context)
    
    def post(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"{invoice.customer.brand} در {invoice.exhibition.title} تسویه حساب شده است و قابلیت پرداخت ندارد.")
            return redirect("office:invoice-list")
        user = get_object_or_404(User, pk=request.user.id)
        form = PaymentAddForm(request.POST)
        context = {
            "invoice":invoice,
            "form":form,
        }
        if form.is_valid():
            state = form.cleaned_data.get("state")
            bank = form.cleaned_data.get("bank")
            amount = int(persian_digits_to_english(str(form.cleaned_data.get("amount"))))
            check = form.cleaned_data.get("check")
            name = form.cleaned_data.get("name")
            tracenumber = persian_digits_to_english(form.cleaned_data.get("tracenumber"))
            datepaid = form.cleaned_data.get("datepaid")
            description = form.cleaned_data.get("description")
            payment = PaymentModel()
            if state == PaymentModel.STATE_CASH:
                payment.state = PaymentModel.STATE_CASH
                payment.amount = int(amount)
                payment.datepaid = datepaid
                payment.payload = description
                payment.user_created = user
                payment.wallet = invoice.wallet
                payment.bank = bank
                payment.invoice = invoice
                payment.save()
                messages.success(request, f"رسید پرداخت بصورت نقدی به مبلغ {amount} با موفقیت ثبت شد.")
            elif state == PaymentModel.STATE_CHECK:
                if check and name:
                    payment.state = PaymentModel.STATE_CHECK
                    payment.amount = int(amount)
                    payment.cardnumber = check
                    payment.name = name
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_created = user
                    payment.wallet = invoice.wallet
                    payment.bank = bank
                    payment.invoice = invoice
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت چک بانکی به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت چک بانکی، شماره سریال چک، نام صاحب چک و نام بانک صادرکننده چک الزامی است!")
                    return render(request, "office/payment-add.html", context)
            elif state == PaymentModel.STATE_POS:
                if tracenumber and bank:
                    payment.state = PaymentModel.STATE_POS
                    payment.amount = int(amount)
                    payment.tracenumber = tracenumber
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_created = user
                    payment.wallet = invoice.wallet
                    payment.bank = bank
                    payment.invoice = invoice
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت کارتخوان به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت پوز اینترنتی، شماره پیگیری و حساب بانکی الزامی است!")
                    return render(request, "office/payment-add.html", context)
            else:
                return render(request, "office/payment-add.html", context)
            wallet_c = get_object_or_404(WalletModel, pk=payment.wallet.pk)
            total = int(payment.amount) + int(wallet_c.cash)
            wallet_c.cash = str(int(total))
            wallet_c.save()
            return redirect("office:payment-add", iid=invoice.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, "office/payment-add.html", context)
    

class PaymentEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_paymentmodel']

    def get(self, request, iid, pid):
        payment = get_object_or_404(PaymentModel, pk=pid)
        if payment.invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {payment.invoice.pk} قبلاً تسویه حساب شده است.")
            return redirect("office:payment-add", iid=payment.invoice.pk)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        payments = PaymentModel.objects.filter(invoice=invoice)
        initial = {
            "state":payment.state,
            "check":payment.cardnumber,
            "name":payment.name,
            "issuerbank":payment.issuerbank,
            "amount":payment.amount,
            "tracenumber":payment.tracenumber,
            "datepaid":payment.datepaid,
            "description":payment.payload,
        }
        form = PaymentAddForm(initial=initial)
        context = {
            "payment":payment,
            "form":form,
            "invoice":invoice,
            "payments":payments,
        }
        return render(request, "office/payment-add.html", context)
    
    def post(self, request, iid, pid):
        payment = get_object_or_404(PaymentModel, pk=pid)
        if payment.invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {payment.invoice.pk} قبلاً تسویه حساب شده است.")
            return redirect("office:payment-add", iid=payment.invoice.pk)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        old_price = int(payment.amount)
        payments = PaymentModel.objects.filter(invoice=invoice)
        user = get_object_or_404(User, pk=request.user.id)
        initial = {
            "state":payment.state,
            "check":payment.cardnumber,
            "name":payment.name,
            "issuerbank":payment.issuerbank,
            "amount":payment.amount,
            "tracenumber":payment.tracenumber,
            "datepaid":payment.datepaid,
            "description":payment.payload,
        }
        form = PaymentAddForm(request.POST, initial=initial)
        context = {
            "payment":payment,
            "invoice":invoice,
            "form":form,
            "payments":payments,
        }
        if form.is_valid():
            state = form.cleaned_data.get("state")
            amount = persian_digits_to_english(str(form.cleaned_data.get("amount")))
            check = form.cleaned_data.get("check")
            issuerbank = form.cleaned_data.get("issuerbank")
            name = form.cleaned_data.get("name")
            tracenumber = persian_digits_to_english(form.cleaned_data.get("tracenumber"))
            datepaid = form.cleaned_data.get("datepaid")
            description = form.cleaned_data.get("description")
            if state == PaymentModel.STATE_CASH:
                payment.state = PaymentModel.STATE_CASH
                payment.amount = int(amount)
                payment.cardnumber = ""
                payment.issuerbank = ""
                payment.name = ""
                payment.datepaid = datepaid
                payment.payload = description
                payment.user_modified = user
                payment.save()
                messages.success(request, f"رسید پرداخت بصورت نقدی به مبلغ {amount} با موفقیت ثبت شد.")
            elif state == PaymentModel.STATE_CHECK:
                if check and issuerbank and name:
                    payment.state = PaymentModel.STATE_CHECK
                    payment.amount = int(amount)
                    payment.cardnumber = check
                    payment.issuerbank = issuerbank
                    payment.name = name
                    payment.tracenumber = ""
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_modified = user
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت چک بانکی به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت چک بانکی، شماره سریال چک، نام صاحب چک و نام بانک صادرکننده چک الزامی است!")
            elif state == PaymentModel.STATE_POS:
                if tracenumber:
                    payment.state = PaymentModel.STATE_POS
                    payment.amount = int(amount)
                    payment.tracenumber = tracenumber
                    payment.cardnumber = ""
                    payment.issuerbank = issuerbank
                    payment.name = ""
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_modified = user
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت کارتخوان به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت پوز اینترنتی، شماره پیگیری الزامی است!")
            else:
                return render(request, "office/payment-add.html", context)
            wallet_c = get_object_or_404(WalletModel, pk=payment.wallet.pk)
            total = int(payment.amount) + int(wallet_c.cash) - old_price
            wallet_c.cash = str(int(total))
            wallet_c.save()
            return redirect("office:payment-add", iid=payment.invoice.pk)
        return render(request, "office/payment-add.html", context)
    

class PaymentRemoveView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.delete_paymentmodel']

    def get(self, request, pid):
        payment = get_object_or_404(PaymentModel, pk=pid)
        wallet = get_object_or_404(WalletModel, pk=payment.wallet.pk)
        ref = request.META.get('HTTP_REFERER')
        if payment.invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"این رسید دریافت برای {payment.invoice.exhibition.title} محاسبه شده و قابلیت حذف ندارد.")
            return HttpResponseRedirect(ref)
        wallet.cash = str(int(wallet.cash) - int(payment.amount))
        wallet.save()
        number = payment.pk
        amount = payment.amount
        payment.delete()
        messages.success(request, f"رسید دریافت به شماره سند {number} به مبلغ {amount} ریال با موفقیت حذف گردید.")
        return HttpResponseRedirect(ref)
    

# class DepositAddView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.add_depositmodel']

#     def get(self, request):
#         deposits = DepositModel.objects.filter(state=DepositModel.STATE_DEPOSIT).order_by("-created_date")
#         form = DepositAddForm()
#         context = {
#             "form":form,
#             "deposits":deposits,
#         }
#         return render(request, "office/deposit-add.html", context)

#     def post(self, request):
#         user = get_object_or_404(User, pk=request.user.id)
#         deposits = DepositModel.objects.filter(state=DepositModel.STATE_DEPOSIT).order_by("-created_date")
#         form = DepositAddForm(request.POST)
#         context = {
#             "form":form,
#             "deposits":deposits,
#         }
#         if form.is_valid():
#             wallet = form.cleaned_data.get("wallet")
#             invoice_number = form.cleaned_data.get("invoice_number")
#             tracenumber = form.cleaned_data.get("tracenumber")
#             amount = form.cleaned_data.get("amount")
#             date = form.cleaned_data.get("date")
#             description = form.cleaned_data.get("description")
#             try:
#                 deposit = DepositModel.objects.get(Q(invoice_number=invoice_number))
#             except DepositModel.DoesNotExist:
#                 deposit = DepositModel(
#                     state=DepositModel.STATE_DEPOSIT,
#                     wallet=wallet,
#                     invoice_number=invoice_number,
#                     description=description,
#                     user_created=user,
#                 )
#                 deposit.save()
#                 item = DepositPaymentModel(
#                     deposit=deposit,
#                     tracenumber=tracenumber,
#                     date=date,
#                     amount=amount,
#                     user_created=user,
#                 )
#                 item.save()
#                 messages.success(request, f"بیعانه با شماره سند {invoice_number} برای مشارکت کننده {deposit.wallet.customer.brand}({deposit.wallet.customer.first_name} {deposit.wallet.customer.last_name}) با موفقیت ثبت شد.")
#                 return redirect("office:deposit-add")
#             if deposit.wallet == wallet and deposit.state == DepositModel.STATE_DEPOSIT:
#                 item = DepositPaymentModel(
#                     deposit=deposit,
#                     tracenumber=tracenumber,
#                     date=date,
#                     amount=amount,
#                     user_created=user,
#                 )
#                 item.save()
#                 messages.success(request, f"بیعانه با شماره سند {invoice_number} برای مشارکت کننده {deposit.wallet.customer.brand}({deposit.wallet.customer.first_name} {deposit.wallet.customer.last_name}) با موفقیت ثبت شد.")
#                 return redirect("office:deposit-add")
#             messages.error(request, f"بیعانه با شماره سند {invoice_number} برای مشارکت کننده {deposit.wallet.customer.brand}({deposit.wallet.customer.first_name} {deposit.wallet.customer.last_name}) قبلاً ثبت شده است.")
#             return render(request, "office/deposit-add.html", context)
#         context = {
#             "form":form,
#         }
#         return render(request, "office/deposit-add.html", context)
    

# class DepositListView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.view_depositmodel']

#     def get(self, request):
#         deposits = DepositModel.objects.filter(Q(state=DepositModel.STATE_DEPOSIT))
#         form = DepositExhibitionForm()
#         context = {
#             "deposits":deposits,
#             "form":form,
#         }
#         return render(request, "office/deposit-list.html", context)
    

# class DepositStateAddView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.view_depositmodel', 'client.add_invoicemodel']

#     def post(self, request, did):
#         deposit = get_object_or_404(DepositModel, pk=did)
#         form = DepositExhibitionForm(request.POST)
#         if form.is_valid():
#             deposit_payment = DepositPaymentModel.objects.filter(deposit=deposit)
#             exhibition = form.cleaned_data.get("exhibition")
#             wallet = get_object_or_404(walletModel, pk=deposit.wallet.pk)
#             invoice = get_object_or_404(InvoiceModel, Q(exhibition=exhibition) & Q(wallet=wallet) & Q(is_active=True))
#             total = 0
#             for i in deposit_payment:
#                 total += int(i.amount)
#                 payment = PaymentModel(
#                     state=PaymentModel.STATE_POS,
#                     invoice=invoice,
#                     wallet=wallet,
#                     amount=i.amount,
#                     tracenumber=i.tracenumber,
#                     datepaid=i.date,
#                 )
#                 payment.save()
#             wallet.cash = str(int(wallet.cash) + int(total))
#             wallet.save()
#             deposit.state = DepositModel.STATE_PAYMENT
#             deposit.save()
#             messages.success(request, f"بیعانه با شماره سند {deposit.invoice_number} و مبلغ {total} به {exhibition.title} اضافه شد.")
#             return redirect("office:deposit-list")
#         messages.error(request, "خطای سیستمی رخ داده استُ لطفا دوباره اقدام کنید!")
#         return redirect("office:deposit-list")
        

class CheckoutView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel', 'client.add_paymentmodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if not invoice.is_active:
            return redirect("office:payment-add", iid=invoice.pk)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {invoice.pk} قبلاً تسویه حساب شده است.")
            return redirect("office:payment-add", iid=invoice.pk)
        user = get_object_or_404(User, pk=request.user.id)
        payments = PaymentModel.objects.filter(invoice=invoice)
        credit = 0
        for i in payments:
            credit += int(i.amount)
        if int(invoice.amount) > credit:
            messages.error(request, "موجودی حساب برای تسویه حساب کافی  نیست.")
            return redirect("office:payment-add", iid=invoice.pk)
        wallet = get_object_or_404(WalletModel, pk=invoice.wallet.pk)
        invoice.state = InvoiceModel.STATE_PAID
        invoice.user_modified = user
        wallet.cash = str(int(wallet.cash) - int(invoice.amount))
        invoice.save()
        wallet.save()
        messages.success(request, f"حساب مشارکت کننده {invoice.customer.brand} برای {invoice.exhibition.title} با موفقیت تسویه شد.")
        return redirect("office:payment-add", iid=invoice.pk)
    

class InvoicePrintView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel', 'client.add_paymentmodel']

    def get(self, request, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if not invoice.is_active:
            return redirect("office:payment-add", iid=invoice.pk)
        if invoice.state != InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {invoice.pk} تسویه حساب نشده است.")
            return redirect("office:payment-add", iid=invoice.pk)
        try:
            mobile_model = MobileModel.objects.get(user=invoice.wallet.user)
        except MobileModel.DoesNotExist:
            messages.error(request, f"شماره موبایل برای مشارکت کننده {invoice.customer.brand} ثبت نشده است!")
            return redirect("office:payment-add", iid=invoice.pk)
        mobile = mobile_model.mobile
        context = {
            "invoice":invoice,
            "mobile":mobile,
            "user":user,
        }
        return render(request, "office/invoice-print.html", context)
    

class ExitPermitView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel', 'client.add_paymentmodel']

    def get(self, request, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        if not invoice.is_active:
            return redirect("office:payment-add", iid=invoice.pk)
        if invoice.state != InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {invoice.pk} تسویه حساب نشده است.")
            return redirect("office:payment-add", iid=invoice.pk)
        context = {
            "invoice":invoice,
            "user":user,
        }
        return render(request, "office/exit-permit.html", context)
        
    

class ExhibitionAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_exhibitionmodel']

    def get(self, request):
        form = ExhibitionForm()
        return render(request, 'office/exhibition-add.html', {'form':form})
    
    def post(self, request):
        form = ExhibitionForm(request.POST)
        user = get_object_or_404(User, pk=request.user.id)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_created = user
            obj.user_modified = user
            obj.price = int(form.cleaned_data.get('price'))
            obj.save()
            messages.success(request, f"عنوان جدید {obj.title} با موفقیت ثبت شد.")
            return redirect('office:exhibition-add')
        return render(request, 'office/exhibition-add.html', {'form':form})
    

class ExhibitionListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_exhibitionmodel']

    def get(self, request):
        exh = ExhibitionModel.objects.all().order_by('-created_date')
        return render(request, 'office/exhibition-list.html', {'exh':exh})
    

class ExhibitionDetailsView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_exhibitionmodel']

    def get(self, request, eid):
        form = AddToExhibitionForm()
        cus = InvoiceModel.objects.filter(Q(exhibition=eid) & Q(is_active=True))
        total = 0
        area = 0
        for i in cus:
            total += int(i.amount)
            area += int(i.area)
        exhibition = get_object_or_404(ExhibitionModel, pk=eid)
        context = {
            'cus':cus,
            'exh':exhibition,
            'total':total,
            'area':area,
            'form':form,
        }
        return render(request, 'office/exhibition-details.html', context)
    
    def post(self, request, eid):
        user = get_object_or_404(User, pk=request.user.id)
        form = AddToExhibitionForm(request.POST)
        cus = InvoiceModel.objects.filter(Q(exhibition=eid) & Q(is_active=True))
        total = 0
        area = 0
        for i in cus:
            total += float(i.amount)
            area += int(i.area)
        exhibition = get_object_or_404(ExhibitionModel, pk=eid)
        context = {
            'cus':cus,
            'exh':exhibition,
            'total':total,
            'area':area,
            'form':form,
        }
        if form.is_valid():
            customer = form.cleaned_data["customer"]
            kind = form.cleaned_data["kind"]
            customer_id = get_object_or_404(CustomerModel, pk=customer.id)
            wallet = get_object_or_404(WalletModel, user=customer_id.user)
            mobile = get_object_or_404(MobileModel, user=wallet.user)
            booth_number = persian_digits_to_english(form.cleaned_data.get("booth_number"))
            area_c = persian_digits_to_english(form.cleaned_data.get("area"))
            discount = persian_digits_to_english(form.cleaned_data.get("discount"))
            if kind == AddToExhibitionForm.KIND_PERCENT:
                pre_price = int(area_c) * int(exhibition.price) - float(int(area_c) * int(exhibition.price) * int(discount)) / 100
                total = (int(pre_price)) + float(int(exhibition.value_added) * (int(pre_price))) / 100
            else:
                pre_price = int(area_c) * int(exhibition.price) - int(discount)
                total = (int(pre_price)) + float(int(exhibition.value_added) * (int(pre_price))) / 100
            invoice = InvoiceModel(
                wallet=wallet,
                customer=customer,
                exhibition=exhibition,
                booth_number=booth_number,
                price=exhibition.price,
                area=area_c,
                value_added=exhibition.value_added,
                discount=discount,
                amount=int(total),
                user_created=user,
            )
            try:
                invoice.save()
            except IntegrityError:
                messages.error(request, f"مشارکت کننده {invoice.customer.brand} قبلاً ثبت نام شده است!")
                return render(request, 'office/exhibition-details.html', context)
            messages.success(request, f'مشارکت کننده {wallet} در نمایشگاه {exhibition.title} با موفقیت ثبت نام شد.')
            send_sms(id=234357, mobile=f"{mobile.mobile}", args=[invoice.exhibition.title])
            return redirect("office:exhibition-details", eid=exhibition.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, 'office/exhibition-details.html', context)
    

class ExhibitionDetailsEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_exhibitionmodel']

    def get(self, request, eid, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        exhibition = get_object_or_404(ExhibitionModel, pk=eid)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {invoice.pk} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:exhibition-details", eid=exhibition.pk)
        initial = {
            "customer":invoice.customer,
            "booth_number":invoice.booth_number,
            "area":invoice.area,
            "discount":invoice.discount,
        }
        form = AddToExhibitionForm(initial=initial)
        cus = InvoiceModel.objects.filter(Q(exhibition=eid) & Q(is_active=True))
        total = 0
        area = 0
        for i in cus:
            total += int(i.amount)
            area += int(i.area)
        context = {
            'cus':cus,
            'exh':exhibition,
            'total':total,
            'area':area,
            'form':form,
            "invoice":invoice,
        }
        return render(request, 'office/exhibition-details.html', context)
    
    def post(self, request, eid, iid):
        user = get_object_or_404(User, pk=request.user.id)
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        exhibition = get_object_or_404(ExhibitionModel, pk=eid)
        if invoice.state == InvoiceModel.STATE_PAID:
            messages.error(request, f"فاکتور شماره {invoice.pk} تسویه حساب شده است و قابلیت ویرایش ندارد.")
            return redirect("office:exhibition-details", eid=exhibition.pk)
        initial = {
            "customer":invoice.customer,
            "booth_number":invoice.booth_number,
            "area":invoice.area,
            "discount":invoice.discount,
        }
        form = AddToExhibitionForm(request.POST, initial=initial)
        cus = InvoiceModel.objects.filter(Q(exhibition=eid) & Q(is_active=True))
        total = 0
        area = 0
        for i in cus:
            total += float(i.amount)
            area += int(i.area)
        context = {
            'cus':cus,
            'exh':exhibition,
            'total':total,
            'area':area,
            'form':form,
            "invoice":invoice,
        }
        if form.is_valid():
            customer = form.cleaned_data.get("customer")
            kind = form.cleaned_data.get("kind")
            wallet = get_object_or_404(WalletModel, user=customer.user)
            mobile = get_object_or_404(MobileModel, user=wallet.user)
            booth_number = persian_digits_to_english(form.cleaned_data.get("booth_number"))
            area_c = persian_digits_to_english(form.cleaned_data.get("area"))
            discount = persian_digits_to_english(form.cleaned_data.get("discount"))
            if kind == AddToExhibitionForm.KIND_PERCENT:
                pre_price = int(area_c) * int(exhibition.price) - float(int(area_c) * int(exhibition.price) * int(discount)) / 100
                total = (int(pre_price)) + float(int(exhibition.value_added) * (int(pre_price))) / 100
            else:
                pre_price = int(area_c) * int(exhibition.price) - int(discount)
                total = (int(pre_price)) + float(int(exhibition.value_added) * (int(pre_price))) / 100
            invoice.wallet = wallet
            invoice.customer = customer
            invoice.booth_number = booth_number
            invoice.price = exhibition.price
            invoice.area = area_c
            invoice.value_added = exhibition.value_added
            invoice.discount = discount
            invoice.amount = int(total)
            invoice.user_modified = user
            try:
                invoice.save()
            except IntegrityError:
                messages.error(request, f"مشارکت کننده {invoice.customer.brand} قبلاً ثبت نام شده است!")
                return render(request, 'office/exhibition-details.html', context)
            messages.success(request, f'مشارکت کننده {invoice.customer.brand} در {exhibition.title} با موفقیت ویرایش شد.')
            send_sms(id=234357, mobile=f"{mobile.mobile}", args=[invoice.exhibition.title])
            return redirect("office:exhibition-details", eid=exhibition.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, 'office/exhibition-details.html', context)
    

class ExhibitionStatusView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_exhibitionmodel']

    def get(self, request, id):
        items = InvoiceModel.objects.filter(Q(exhibition__pk=id) & Q(is_active=True))
        exhibition = get_object_or_404(ExhibitionModel, pk=id)
        total_price = 0
        total_area = 0
        for i in items:
            total_price += int(i.amount)
            total_area += int(i.area)
        context = {
            "items":items,
            "total_price":total_price,
            "total_area":total_area,
            "exhibition":exhibition,
        }
        return render(request, "office/exhibition-status.html", context)
    

class RequestListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_requestmodel']

    def get(self, request):
        req = RequestModel.objects.all().order_by('-created_date')
        form = RequestStateForm()
        return render(request, 'office/request-list.html', {'req':req, 'form':form})
    

class RequestStateView(PermissionRequiredMixin, views.View):
    login_url = "accounts:signin"
    permission_required = ['client.view_requestmodel', 'client.change_requestmodel']

    def post(self, request, rid):
        req = get_object_or_404(RequestModel, pk=rid)
        mobile = get_object_or_404(MobileModel, user=req.customer.user)
        form = RequestStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data.get("state")
            message = form.cleaned_data.get("message")
            req.state = state
            req.message = message
            req.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد.")
            send_sms(id=330572, mobile=mobile.mobile, args=[f"{req.customer.brand}"])
            return redirect("office:request-list")
        messages.error(request, "خطای سیستمی رخ داده است و پیام شما ارسال نشد!")
        return redirect("office:request-list")

    

# class RequestDetailsView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.add_requestmodel', 'client.add_invoicemodel', 'client.add_messagesmodel']

#     def get(self, request, rid):
#         req = get_object_or_404(RequestModel, pk=rid)
#         mes = MessagesModel.objects.filter(customer=req.customer)
#         form = MessageForm()
#         form2 = RequestAcceptForm()
#         context = {
#             'req':req,
#             'mes':mes,
#             'form':form,
#             'form2':form2,
#         }
#         return render(request, 'office/request-details.html', context)
    
    # def post(self, request, rid):
    #     req = get_object_or_404(RequestModel, pk=rid)
    #     mes = MessagesModel.objects.filter(customer=req.customer)
    #     form = MessageForm(request.POST)
    #     form2 = RequestAcceptForm(request.POST)
    #     context = {
    #         'req':req,
    #         'mes':mes,
    #         'form':form,
    #         'form':form2,
    #     }
    #     if form.is_valid() and 'btn1' in request.POST:
    #         text = form.cleaned_data.get('text')
    #         mes = MessagesModel()
    #         mes.text = text
    #         mes.is_active = True
    #         mes.customer = req.customer
    #         mes.save()
    #         req.state = req.STATE_DENY
    #         req.save()
    #         messages.success(request, 'پیغام شما با موفقیت ارسال شد.')
    #         return render(request, 'office/request-details.html', context)
    #     if form2.is_valid() and 'btn2' in request.POST:
    #         area = form2.cleaned_data.get('area')
    #         discount = form2.cleaned_data.get('discount')
    #         description = form2.cleaned_data.get('description')
    #         total = int(req.exhibition.price) * int(area) + int(int(req.exhibition.price) * int(area) * int(req.exhibition.value_added) / 100)
    #         invoice = InvoiceModel(
    #             is_active=True,
    #             user=req.user,
    #             customer=req.customer,
    #             exhibition=req.exhibition,
    #             price=req.exhibition.price,
    #             area=area,
    #             value_added=req.exhibition.value_added,
    #             discount=discount,
    #             total_price=total,
    #             description=description,
    #         )
    #         invoice.save()
    #         req.state = req.STATE_ACCEPT
    #         req.save()
    #         messages.success(request, f'موافقت شما با درخواست {req.customer.company} برای نمایشگاه {req.exhibition.title} به متراژ {area} ثبت شد.')
    #         return render(request, 'office/request-details.html', context)
    #     messages.error(request, 'درخواست عملیات شما با خطا مواجه شد!', extra_tags="danger")
    #     return redirect('office:request-details', rid=req.pk)


# class MessagesListView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.view_messagesmodel']

#     def get(self, request):
#         mes = MessagesModel.objects.all().order_by('-created_date')
#         form = MessageAddForm()
#         return render(request, 'office/messages-list.html', {'mes':mes, 'form':form})
    

# class MessageAddView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.add_messagesmodel']

#     def post(self, request):
#         user = get_object_or_404(User, pk=request.user.id)
#         form = MessageAddForm(request.POST)
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.user_created = user
#             obj.user_modified = user
#             obj.is_active = True
#             obj.save()
#             messages.success(request, f"پیغام شما برای مشارکت کننده {obj.customer.company} ({obj.customer.firstname} {obj.customer.firstname}) با موفقیت ارسال شد.")
#             return redirect('office:message-list')
#         messages.warning(request, "خطا در انجام عملیات رخ داده است، لطفا دوباره سعی کنید!")
#         return redirect('office:message-list')
    

# class MessageChangeView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.change_messagesmodel', 'client.add_messagechangemodel']

#     def get(self, request, mid):
#         mes = get_object_or_404(MessagesModel, pk=mid)
#         form = MessageForm(initial={'text':mes.text})
#         context = {
#             'mes':mes,
#             'form':form,
#         }
#         return render(request, 'office/message-change.html', context)
    
#     def post(self, request, mid):
#         user = get_object_or_404(User, pk=request.user.id)
#         mes = get_object_or_404(MessagesModel, pk=mid)
#         form = MessageForm(request.POST)
#         context = {
#             'mes':mes,
#             'form':form,
#         }
#         if form.is_valid():
#             text = form.cleaned_data.get('text')
#             old = MessageChangeModel()
#             old.text = mes.text
#             old.user_modified = mes.user_modified
#             old.modified_date = mes.modified_date
#             old.message = mes
#             old.save()
#             messages.success(request, f"پیغام شما برای مشارکت کننده {mes.customer.company} با موفقیت ویرایش شد.")
#             mes.user_modified = user
#             mes.text = text
#             mes.save()
#             return redirect('office:message-list')
#         return render(request, 'office/message-change.html', context)