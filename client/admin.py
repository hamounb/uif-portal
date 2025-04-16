from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(CustomerModel)
class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("brand", "company", "pk", "ncode", "sid")
    list_display = ("kind", "pk", "sid", "user", "brand")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    
@admin.register(DocumentsModel)
class DocumentsAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("customer",)
    list_display = ("state", "customer", "file")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Delete the associated file before deleting the object
        if obj.file:  # Assuming your file field is named 'your_file_field'
            obj.file.delete(save=False)  # Delete the file from storage
        
        # Call the parent class delete_model method to perform the actual deletion
        super().delete_model(request, obj)
    
@admin.register(ExhibitionModel)
class ExhibitionAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("title",)
    list_display = ("is_active", "sid", "title")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)

# @admin.register(RequestModel)
# class RequestsAdmin(admin.ModelAdmin):
#     readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
#     search_fields = ("customer",)
    
#     def save_model(self, request, obj, form, change):
#         if change:
#             obj.user_modified = request.user
#         else:
#             obj.user_created = request.user
#             obj.user_modified = request.user
#         return super().save_model(request, obj, form, change)
    

# @admin.register(MessagesModel)
# class MessagesAdmin(admin.ModelAdmin):
#     readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
#     search_fields = ("customer",)
    
#     def save_model(self, request, obj, form, change):
#         if change:
#             obj.user_modified = request.user
#         else:
#             obj.user_created = request.user
#             obj.user_modified = request.user
#         return super().save_model(request, obj, form, change)


# @admin.register(MessageChangeModel)
# class MessageChangeAdmin(admin.ModelAdmin):
#     readonly_fields = ("user_modified", "modified_date")
#     search_fields = ("message__customer",)
    
#     def save_model(self, request, obj, form, change):
#         if change:
#             obj.user_modified = request.user
#         else:
#             obj.user_modified = request.user
#         return super().save_model(request, obj, form, change)

    
@admin.register(InvoiceModel)
class InvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("customer", "valet", "amount", "exhibition", "booth_number")
    list_display = ("pk", "state", "is_active", "customer", "exhibition", "amount")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)

    
@admin.register(ValetModel)
class ValetAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("user", )
    list_display = ("pk", "user", "cash")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    

@admin.register(BankModel)
class BankAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("name", "account_number")
    list_display = ("kind", "name", "account_number")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    

@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("rrn", "invoice", "tracenumber", "digitalreceipt", "datepaid")
    list_display = ("pk", "state", "amount", "tracenumber", "rrn", "respcode", "datepaid")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)

    
# @admin.register(DepositModel)
# class DepositAdmin(admin.ModelAdmin):
#     readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
#     search_fields = ("invoice_number", "customer")
#     list_display = ("pk", "state", "valet", "invoice_number")
    
#     def save_model(self, request, obj, form, change):
#         if change:
#             obj.user_modified = request.user
#         else:
#             obj.user_created = request.user
#             obj.user_modified = request.user
#         return super().save_model(request, obj, form, change)
    

# @admin.register(DepositPaymentModel)
# class DepositPaymentAdmin(admin.ModelAdmin):
#     readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
#     search_fields = ("deposit", "tracenumber", "date")
#     list_display = ("deposit", "amount", "tracenumber", "date")
    
#     def save_model(self, request, obj, form, change):
#         if change:
#             obj.user_modified = request.user
#         else:
#             obj.user_created = request.user
#             obj.user_modified = request.user
#         return super().save_model(request, obj, form, change)