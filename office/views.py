from django.shortcuts import render, redirect, get_object_or_404
from django import views
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.db.models import Sum
from accounts.models import MobileModel
from client.models import *
from django.db.utils import IntegrityError

# Create your views here.

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
        customer = CustomerModel.objects.filter(is_active=False).order_by('-created_date')
        # req = RequestModel.objects.filter(state=RequestModel.STATE_WAIT).order_by('-created_date')
        exhibition = ExhibitionModel.objects.filter(is_active=True)
        context = {
            'customer':customer,
            'exhibition':exhibition,
            # 'req':req,
            'user':user,
        }
        return render(request, 'office/home.html', context)
    

class CustomerListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_customermodel']

    def get(self, request):
        customer = CustomerModel.objects.all().order_by('-created_date')
        return render(request, 'office/customer-list.html', {'customer':customer})
    

class CustomerAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_customermodel']

    def get(self, request):
        form = CustomerAddForm()
        return render(request, 'office/customer-add.html', {'form':form})
    
    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        form = CustomerAddForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.kind == "legal":
                if not obj.ncode:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای شناسه ملی باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                elif not obj.ceoname:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام مدیرعامل باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                elif not obj.company:
                    messages.error(request, f"مشتری با نوع حقوقی باید دارای نام شرکت یا سازمان باشد.")
                    return render(request, 'office/customer-add.html', {'form':form})
                else:
                    code = form.cleaned_data.get('code')
                    mobile = form.cleaned_data.get('mobile')
                    try:
                        cus = User.objects.get(username=code)
                    except User.DoesNotExist:
                        new = User(username=code)
                        new.set_password(mobile)
                        new.save()
                        obj.user = new
                        obj.user_modified = user
                        obj.user_created = user
                        obj.save()
                        messages.success(request, f"مشتری حقوقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                        try:
                            valet = ValetModel.objects.get(customer=obj)
                        except ValetModel.DoesNotExist:
                            valet = ValetModel(customer=obj)
                            valet.save()
                        return redirect('office:customer-change', cid=obj.id)
                    obj.user = cus
                    obj.user_modified = user
                    obj.user_created = user
                    obj.save()
                    messages.success(request, f"مشتری حقوقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                    try:
                        valet = ValetModel.objects.get(customer=obj)
                    except ValetModel.DoesNotExist:
                        valet = ValetModel(customer=obj)
                        valet.save()
                    return redirect('office:customer-change', cid=obj.id)
            else:
                code = form.cleaned_data.get('code')
                mobile = form.cleaned_data.get('mobile')
                try:
                    cus = User.objects.get(username=code)
                except User.DoesNotExist:
                    new = User(username=code)
                    new.set_password(mobile)
                    new.save()
                    obj.user = new
                    obj.ceoname = ''
                    obj.ncode = ''
                    obj.company = ''
                    obj.user_modified = user
                    obj.user_created = user
                    obj.save()
                    messages.success(request, f"مشتری حقیقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                    try:
                        valet = ValetModel.objects.get(customer=obj)
                    except ValetModel.DoesNotExist:
                        valet = ValetModel(customer=obj)
                        valet.save()
                    return redirect('office:customer-change', cid=obj.pk)
                obj.user = cus
                obj.ceoname = ''
                obj.ncode = ''
                obj.company = ''
                obj.user_modified = user
                obj.user_created = user
                obj.save()
                messages.success(request, f"مشتری حقیقی با نام تجاری {obj.brand} با موفقیت ثبت شد.")
                try:
                    valet = ValetModel.objects.get(customer=obj)
                except ValetModel.DoesNotExist:
                    valet = ValetModel(customer=obj)
                    valet.save()
                return redirect('office:customer-change', cid=obj.pk)
        return render(request, 'office/customer-add.html', {'form':form})
    

class CustomerChangeView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_customermodel']

    def get(self, request, cid):
        customer = get_object_or_404(CustomerModel, pk=cid)
        form = CustomerChangeForm(instance=customer)
        docs = DocumentsModel.objects.filter(customer=customer).order_by('-created_date')
        form2 = DocumentForm()
        context = {
            'form':form,
            'form2':form2,
            'customer':customer,
            'docs':docs,
        }
        return render(request, 'office/customer-change.html', context)
    
    def post(self, request, cid):
        customer = get_object_or_404(CustomerModel, pk=cid)
        user = get_object_or_404(User, pk=request.user.id)
        form = CustomerChangeForm(request.POST, instance=customer)
        context = {
            'form':form,
            'customer':customer,
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
                messages.success(request, f"اطلاعات {obj.company} بروزرسانی شد.")
                return render(request, 'office/customer-change.html', context)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, 'office/customer-change.html', context)
    

class CustomerExhibitionView(views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel']

    def get(self , request, id):
        customer = get_object_or_404(CustomerModel, pk=id)
        form = AddToExhibitionForm()
        context = {
            'customer':customer,
            'form':form,
        }
        return render(request, "office/customer-exhibition.html", context)
    
    def post(self, request, id):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=id)
        valet = get_object_or_404(ValetModel, customer=customer)
        form = AddToExhibitionForm(request.POST)
        context = {
            'customer':customer,
            'form':form,
        }
        if form.is_valid():
            exhibition = form.cleaned_data.get("exhibition")
            area = form.cleaned_data.get("area")
            discount = form.cleaned_data.get("discount")
            booth_number = form.cleaned_data.get("booth_number")
            exh = get_object_or_404(ExhibitionModel, title=exhibition)
            total = (int(area) * int(exh.price)) + float(int(exh.value_added) * (int(area) * int(exh.price))) / 100
            amount = int(total) - float(int(total) * int(discount)) /100
            invoice = InvoiceModel(
                valet=valet,
                exhibition=exh,
                booth_number=booth_number,
                area=area,
                price=exh.price,
                value_added=exh.value_added,
                amount=int(amount),
                user_created=user,
            )
            invoice.save()
            messages.success(request, f"مشارکت کننده {customer.brand} در نمایشگاه {exh.title} با موفقیت ثبت‌نام شد.")
            return redirect("office:exhibition-details", eid=exh.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, "office/customer-exhibition.html", context)


class DocumentsAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_documentsmodel']

    def post(self, request, id):
        user = get_object_or_404(User, pk=request.user.id)
        customer = get_object_or_404(CustomerModel, pk=id)
        form2 = DocumentForm(request.POST, request.FILES)
        if form2.is_valid():
            file = form2.cleaned_data['file']
            obj = DocumentsModel(
                is_active = True,
                state = DocumentsModel.STATE_ACCEPT,
                file = file,
                user = customer.user,
                user_created = user,
                user_modified = user,
                customer = customer,
            )
            obj.save()
            messages.success(request, f"مدرک شما با موفقیت بارگذاری شد!")
            return redirect('office:customer-change', cid=customer.pk)
        return redirect('office:customer-change', cid=customer.pk)
    

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
        ref = request.META.get('HTTP_REFERER')
        messages.success(request, f"مدرک مشارکت کننده با نام تجاری {file.customer.company} با موفقیت تایید شد.")
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



class DocumentsListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_documentsmodel']

    def get(self, request):
        doc = DocumentsModel.objects.filter(Q(state=DocumentsModel.STATE_WAIT) | Q(state=DocumentsModel.STATE_DENY)).order_by('-created_date')
        return render(request, 'office/documents-list.html', {'doc':doc})
    

# class RequestListView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.view_requestmodel']

#     def get(self, request):
#         req = RequestModel.objects.all().order_by('-created_date')
#         return render(request, 'office/request-list.html', {'req':req})
    

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
    

class InvoiceAddView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.add_invoicemodel']

    def get(self, request):
        form = InvoiceForm()
        return render(request, 'office/invoice-add.html', {'form':form})
    
    def post(self, request):
        form = InvoiceItemForm(request.POST)
        user = get_object_or_404(User, pk=request.user.id)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = CustomerModel.objects.get(company=form.cleaned_data.get('customer')).user
            obj.price = ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).price
            obj.value_added = ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).value_added
            total = int(ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).price) * int(form.cleaned_data.get('area'))
            amount = float(total + (total * int(ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).value_added) / 100))
            total_price = float(amount - float(amount * int(form.cleaned_data.get('discount')) / 100))
            obj.total_price = int(total_price)
            obj.user_created = user
            invoice = InvoiceModel(
                customer = CustomerModel.objects.get(company=form.cleaned_data.get('customer')),
                amount = int(total_price)
            )
            invoice.save()
            obj.invoice = invoice
            obj.save()
            messages.success(request, f'فاکتور برای مشارکت کننده نمایشگاه {obj.exhibition} با نام تجاری {obj.customer.company} با موفقیت ثبت شد.')
            return render(request, 'office/invoice-add.html', {'form':form})
        return render(request, 'office/invoice-add.html', {'form':form})
    

class InvoiceListView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_invoicemodel']

    def get(self, request):
        invoices = InvoiceModel.objects.all().order_by('-created_date')
        return render(request, 'office/invoice-list.html', {'invoices':invoices})
    

class InvoiceUnpaidView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_invoicemodel']

    def get(self, request):
        invoices = InvoiceModel.objects.filter(Q(state=InvoiceModel.STATE_PREPAYMENT) | Q(state=InvoiceModel.STATE_UNPAID)).order_by('-created_date')
        return render(request, 'office/invoice-list.html', {'invoices':invoices})
    

class InvoiceDetailsView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['clent.change_invoicemodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        return render(request, 'office/invoice-details.html', {'invoice':invoice})
    

class InvoiceEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_invoiceitemmodel']

    def get(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        item = get_object_or_404(InvoiceItemModel, invoice=invoice)
        form = InvoiceItemForm(instance=item)
        context = {
            "form":form,
        }
        return render(request, 'office/invoice-add.html', context)
    
    def post(self, request, iid):
        invoice = get_object_or_404(InvoiceModel, pk=iid)
        item = get_object_or_404(InvoiceItemModel, invoice=invoice)
        form = InvoiceItemForm(request.POST, instance=item)
        user = get_object_or_404(User, pk=request.user.id)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = item.user
            obj.price = ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).price
            obj.value_added = ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).value_added
            total = int(ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).price) * int(form.cleaned_data.get('area'))
            amount = float(total + (total * int(ExhibitionModel.objects.get(pk=form.cleaned_data['exhibition'].id).value_added) / 100))
            total_price = float(amount - float(amount * int(form.cleaned_data.get('discount')) / 100))
            obj.total_price = int(total_price)
            obj.user_modified = user
            try:
                invoice = InvoiceModel.objects.get(customer=form.cleaned_data.get('customer'))
            except CustomerModel.DoesNotExist:
                return render(request, 'office/invoice-add.html', {'form':form})
            else:
                invoice.amount = int(total_price)
                invoice.save()
                obj.invoice = invoice
                obj.save()
                messages.success(request, f'فاکتور برای مشارکت کننده نمایشگاه {obj.exhibition} با نام تجاری {obj.customer.company} با موفقیت ویرایش شد.')
                return render(request, 'office/invoice-add.html', {'form':form})
        return render(request, 'office/invoice-add.html', {'form':form})
    

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
        form = InvoiceAddForm()
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
        return render(request, 'office/exhibition-details.html', context)
    
    def post(self, request, eid):
        user = get_object_or_404(User, pk=request.user.id)
        form = InvoiceAddForm(request.POST)
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
            valet = form.cleaned_data.get("valet")
            booth_number = form.cleaned_data.get("booth_number")
            area_c = form.cleaned_data.get("area")
            total = (int(area_c) * int(exhibition.price)) + float(int(exhibition.value_added) * (int(area_c) * int(exhibition.price))) / 100
            invoice = InvoiceModel(
                valet=valet,
                exhibition=exhibition,
                booth_number=booth_number,
                price=exhibition.price,
                area=area_c,
                value_added=exhibition.value_added,
                amount=int(total),
                user_created=user,
            )
            invoice.save()
            messages.success(request, f'مشارکت کننده {valet} در نمایشگاه {exhibition.title} با موفقیت ثبت نام شد.')
            return redirect("office:exhibition-details", eid=exhibition.pk)
        messages.error(request, "خطای سیستمی رخ داده است!")
        return render(request, 'office/exhibition-details.html', context)

    

class ExhibitionStatusView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.view_exhibitionmodel']

    def get(self, request, id):
        items = InvoiceModel.objects.filter(Q(exhibition__pk=id) & Q(is_active=True))
        context = {
            "items":items,
        }
        return render(request, "office/exhibition-status.html", context)
    

# class AddToExhibitionView(PermissionRequiredMixin, views.View):
#     login_url = 'accounts:signin'
#     permission_required = ['client.add_customermodel']

#     def get(self, request):
#         form = AddToExhibitionForm()
#         context = {
#             "form":form,
#         }
#         return render(request, "office/add-to-exhibition.html", context)
    
#     def post(self, request):
#         user = get_object_or_404(User, pk=request.user.id)
#         form = AddToExhibitionForm(request.POST)
#         if form.is_valid():
#             customer = form.cleaned_data.get("customer")
#             exhibition = form.cleaned_data.get("exhibition")
#             area = form.cleaned_data.get("area")
#             booth_number = form.cleaned_data.get("booth_number")
#             obj = InvoiceModel(
#                 customer=customer,
#                 exhibition=exhibition,
#                 amount="0",
#             )
#             try:
#                 obj.save()
#             except IntegrityError:
#                 messages.error(request, "")


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

    def get(self, request, id):
        invoice = get_object_or_404(InvoiceModel, pk=id)
        form = PaymentAddForm()
        context = {
            "invoice":invoice,
            "form":form,
        }
        return render(request, "office/payment-add.html", context)
    
    def post(self, request, id):
        invoice = get_object_or_404(InvoiceModel, pk=id)
        user = get_object_or_404(User, pk=request.user.id)
        form = PaymentAddForm(request.POST)
        context = {
            "invoice":invoice,
            "form":form,
        }
        if form.is_valid():
            state = form.cleaned_data.get("state")
            amount = form.cleaned_data.get("amount")
            check = form.cleaned_data.get("check")
            issuerbank = form.cleaned_data.get("issuerbank")
            name = form.cleaned_data.get("name")
            tracenumber = form.cleaned_data.get("tracenumber")
            datepaid = form.cleaned_data.get("datepaid")
            description = form.cleaned_data.get("description")
            payment = PaymentModel()
            if state == PaymentModel.STATE_CASHE:
                payment.state = PaymentModel.STATE_CASHE
                payment.amount = int(amount)
                payment.datepaid = datepaid
                payment.payload = description
                payment.user_created = user
                payment.invoice = invoice
                payment.save()
                messages.success(request, f"رسید پرداخت بصورت نقدی به مبلغ {amount} با موفقیت ثبت شد.")
            elif state == PaymentModel.STATE_CHECK:
                if check and issuerbank and name:
                    payment.state = PaymentModel.STATE_CHECK
                    payment.amount = int(amount)
                    payment.cardnumber = check
                    payment.issuerbank = issuerbank
                    payment.name = name
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_created = user
                    payment.invoice = invoice
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت چک بانکی به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت چک بانکی، شماره سریال چک، نام صاحب چک و نام بانک صادرکننده چک الزامی است!")
            elif state == PaymentModel.STATE_POS:
                if tracenumber:
                    payment.state = PaymentModel.STATE_POS
                    payment.amount = int(amount)
                    payment.tracenumber = tracenumber
                    payment.issuerbank = issuerbank
                    payment.datepaid = datepaid
                    payment.payload = description
                    payment.user_created = user
                    payment.invoice = invoice
                    payment.save()
                    messages.success(request, f"رسید پرداخت بصورت کارتخوان به مبلغ {amount} با موفقیت ثبت شد.")
                else:
                    messages.error(request, "برای رسید پرداخت بصورت پوز اینترنتی، شماره پیگیری الزامی است!")
            else:
                return render(request, "office/payment-add.html", context)
            payment_list = PaymentModel.objects.filter(invoice=invoice)
            total_amount = 0
            if payment_list:
                for i in payment_list:
                    total_amount += i.amount
                if total_amount >= int(invoice.amount):
                    invoice.state = InvoiceModel.STATE_PAID
                    invoice.save()
                else:
                    invoice.state = InvoiceModel.STATE_PREPAYMENT
                    invoice.save()
            return render(request, "office/payment-add.html", context)
        return render(request, "office/payment-add.html", context)
    

class PaymentEditView(PermissionRequiredMixin, views.View):
    login_url = 'accounts:signin'
    permission_required = ['client.change_paymentmodel']

    def get(self, request, id):
        payment = get_object_or_404(PaymentModel, pk=id)
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
        }
        return render(request, "office/payment-edit.html", context)
    
    def post(self, request, id):
        payment = get_object_or_404(PaymentModel, pk=id)
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
            "form":form,
        }
        if form.is_valid():
            state = form.cleaned_data.get("state")
            amount = form.cleaned_data.get("amount")
            check = form.cleaned_data.get("check")
            issuerbank = form.cleaned_data.get("issuerbank")
            name = form.cleaned_data.get("name")
            tracenumber = form.cleaned_data.get("tracenumber")
            datepaid = form.cleaned_data.get("datepaid")
            description = form.cleaned_data.get("description")
            if state == PaymentModel.STATE_CASHE:
                payment.state = PaymentModel.STATE_CASHE
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
                return render(request, "office/payment-edit.html", context)
            payment_list = PaymentModel.objects.filter(invoice=payment.invoice)
            invoice = get_object_or_404(InvoiceModel, pk=payment.invoice.pk)
            total_amount = 0
            if payment_list:
                for i in payment_list:
                    total_amount += i.amount
                if total_amount >= int(invoice.amount):
                    invoice.state = InvoiceModel.STATE_PAID
                    invoice.save()
                else:
                    invoice.state = InvoiceModel.STATE_PREPAYMENT
                    invoice.save()
            return render(request, "office/payment-edit.html", context)
        return render(request, "office/payment-edit.html", context)
        