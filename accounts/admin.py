from django.contrib import admin
from .models import TokenModel, MobileModel

# Register your models here.

@admin.register(TokenModel)
class TokenAdmin(admin.ModelAdmin):
    readonly_fields = ("created_date",)
    search_fields = ("user__username",)
    list_display = ("user", "otp", "status")
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.user = request.user
        else:
            obj.user = request.user
        return super().save_model(request, obj, form, change)
    

@admin.register(MobileModel)
class MobileAdmin(admin.ModelAdmin):
    readonly_fields = ("created_date", )
    search_fields = ("user__username", "mobile")
    list_display = ("user", "mobile")