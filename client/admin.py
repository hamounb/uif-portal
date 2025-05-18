from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(CustomerModel)
class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("brand", "company", "pk", "ncode", "sid", "user__username")
    list_display = ("kind", "pk", "sid", "user", "brand")
    autocomplete_fields = ("user",)
    
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
    search_fields = ("customer_brand",)
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
    search_fields = ("customer__brand", "amount", "exhibition__title", "booth_number", "wallet__user__username")
    list_display = ("pk", "state", "is_active", "customer", "exhibition", "amount")
    autocomplete_fields = ("customer", "exhibition", "wallet")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)

    
@admin.register(WalletModel)
class WalletAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("user__username", )
    list_display = ("pk", "user", "cash")
    autocomplete_fields = ("user",)
    
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
    search_fields = ("rrn", "invoice__pk", "tracenumber", "digitalreceipt", "datepaid", "wallet__user__username")
    list_display = ("pk", "state", "amount", "tracenumber", "rrn", "respcode", "datepaid")
    autocomplete_fields = ("wallet", "invoice")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    

@admin.register(RequestModel)
class RequestAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("customer__brand", )
    list_display = ("pk", "state", "customer", "exhibition", "rules")
    autocomplete_fields = ("customer", "exhibition")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user_modified = request.user
        else:
            obj.user_created = request.user
            obj.user_modified = request.user
        return super().save_model(request, obj, form, change)
    

@admin.register(RequestDocumentsModel)
class RequestDocumentsAdmin(admin.ModelAdmin):
    readonly_fields = ("user_created", "user_modified", "created_date", "modified_date")
    search_fields = ("request__pk", )
    list_display = ("pk", "request", "file")
    
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
#     list_display = ("pk", "state", "wallet", "invoice_number")
    
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