
from django.shortcuts import render, redirect, get_object_or_404
from django import views
from .forms import *
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import TokenModel, MobileModel
from datetime import datetime, timedelta
from django.http import JsonResponse
from .payamak import send_sms, send_token
from client.models import WalletModel

# Create your views here.

def persian_digits_to_english(s:str):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translate_table = str.maketrans(persian_digits, english_digits)
    return s.translate(translate_table)



class SignUpView(views.View):
    
    def get(self, request):
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form':form})
    
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            code = persian_digits_to_english(form.cleaned_data.get('code'))
            mobile = persian_digits_to_english(form.cleaned_data.get('mobile'))
            try:
                new_user = User.objects.get(username=code)
            except User.DoesNotExist:
                new_user = User(
                    username=code,
                    first_name=firstname,
                    last_name=lastname,
                )
                new_user.set_password(mobile)
                new_user.is_active = False
                new_user.save()
            if new_user.is_active:
                messages.error(request, 'قبلا با این کد ملی حساب کاربری ایجاد شده است!')
                return render(request, 'accounts/signup.html', {'form':form})
            try:
                wallet = WalletModel.objects.get(user=new_user)
                wallet.cash = "0"
                wallet.save()
            except WalletModel.DoesNotExist:
                wallet = WalletModel(
                    user=new_user,
                    cash="0",
                    user_created=new_user,
                )
                wallet.save()
            try:
                mobile_model = MobileModel.objects.get(user=new_user)
                mobile_model.mobile = mobile
                mobile_model.save
            except MobileModel.DoesNotExist:
                mobile_model = MobileModel(
                    user=new_user,
                    mobile=mobile,
                )
                mobile_model.save()
            try:
                tk = TokenModel.objects.get(user=new_user)
            except TokenModel.DoesNotExist:
                otp = send_token(mobile)
                tk = TokenModel(user=new_user, otp=otp['code'], status=otp['status'])
                tk.save()
                return redirect('accounts:verify', code=code)
            otp = send_token(mobile)
            tk.otp = otp['code']
            tk.status = otp['status']
            tk.save()
            return redirect('accounts:verify', code=code)
        else:
            return render(request, 'accounts/signup.html', {'form':form})

 
class MobileVerifyView(views.View):

    def get(self, request, code):
        user = get_object_or_404(User, username=code)
        if not user.is_active and not user.is_staff:
            try:
                mobile = MobileModel.objects.get(user=user)
            except MobileModel.DoesNotExist:
                messages.error(request, "شماره موبایل شما ثبت نشده است!")
                return redirect('accounts:change-mobile', code=code)
            form = TokenForm()
            return render(request, 'accounts/token.html', {'form':form, 'code':code})
        return redirect('accounts:signin')
    
    def post(self, request, code):
        user = get_object_or_404(User, username=code)
        if not user.is_active and not user.is_staff:
            try:
                mobile = MobileModel.objects.get(user=user)
            except MobileModel.DoesNotExist:
                messages.error(request, "شماره موبایل شما ثبت نشده است!")
                return redirect('accounts:change-mobile', code=code)
            form = TokenForm(request.POST)
            try:
                tk = TokenModel.objects.get(user=user)
            except TokenModel.DoesNotExist:
                messages.error(request, "خطای سیستمی رخ داده است، لطفا دوباره سعی کنید!")
                return redirect('accounts:signin')
            if form.is_valid():
                otp = persian_digits_to_english(form.cleaned_data['otp'])
                if tk.otp == otp:
                    if datetime.now() - datetime(
                        year=tk.modified_date.year, month=tk.modified_date.month, day=tk.modified_date.day, hour=tk.modified_date.hour, minute=tk.modified_date.minute, second=tk.modified_date.second, microsecond=tk.modified_date.microsecond) > timedelta(2):
                        messages.warning(request, "رمز یکبارمصرف شما منقضی شده، لطفا درخواست ارسال مجدد را کلیک کنید.")
                        return render(request, 'accounts/token.html', {'form':form, 'code':code})
                    user.is_active = True
                    user.save()
                    us = authenticate(username=code, password=mobile.mobile)
                    if us is not None:
                        login(request, user)
                        if user.get_all_permissions():
                            return redirect('office:home')
                        return redirect('client:index')
                    return render(request, 'accounts/token.html', {'form':form, 'code':code})
                else:
                    messages.error(request, 'رمز یکبارمصرف اشتباه است!')
                    return render(request, 'accounts/token.html', {'form':form, 'code':code})
            else:
                return render(request, 'accounts/token.html', {'form':form, 'code':code})
        else:
            return redirect('accounts:signin')
        

class ChangeMobileView(views.View):

    def get(self, request, code):
        user = get_object_or_404(User, username=code)
        if not user.is_active and not user.is_staff:
            form = ChangeMobileForm()
            return render(request, 'accounts/change-mobile.html', {'form':form, 'code':code})
        return redirect('accounts:signin')
    
    def post(self, request, code):
        user = get_object_or_404(User, username=code)
        if not user.is_active and not user.is_staff:
            form = ChangeMobileForm(request.POST)
            if form.is_valid():
                mobile = persian_digits_to_english(form.cleaned_data.get('mobile'))
                user.set_password(mobile)
                user.save()
                otp = send_token(mobile)
                try:
                    tk = TokenModel.objects.get(user=user)
                except TokenModel.DoesNotExist:
                    tk = TokenModel(user=user)
                tk.otp = otp['code']
                tk.status = otp['status']
                tk.save()
                try:
                    number = MobileModel.objects.get(user=user)
                except MobileModel.DoesNotExist:
                    number = MobileModel(user=user)
                number.mobile = mobile
                number.save()
                messages.success(request, f"شماره موبایل شما به {mobile} تغییر یافت.")
                return redirect('accounts:verify', code=code)
            return render(request, 'accounts/change-mobile.html', {'form':form, 'code':code})
        return redirect('accounts:signin')
    

class ReTokenView(views.View):

    def get(self, request, code):
        user = get_object_or_404(User, username=code)
        try:
            mobile = MobileModel.objects.get(user=user)
        except MobileModel.DoesNotExist:
            return redirect('accounts:change-mobile', code=code)
        try:
            tk = TokenModel.objects.get(user=user)
        except TokenModel.DoesNotExist:
            tk = TokenModel(user=user)
        otp = send_token(mobile.mobile)
        tk.otp = otp['code']
        tk.status = otp['status']
        tk.save()
        data = {
            'message': 'Done',
        }
        return JsonResponse(data)


class SignInView(views.View):

    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=request.user.id)
            if user.is_staff:
                if user.is_active:
                    return redirect('office:home')
                messages.error(request, "کاربر گرامی حساب شما غیرفعال شده است!")
                return redirect('accounts:signin')
            return redirect('client:index')
        form = LoginForm()
        return render(request, 'accounts/signin.html', {'form':form})
    
    def post(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=request.user.id)
            if user.is_staff:
                if user.is_active:
                    return redirect('office:home')
                messages.error(request, "کاربر گرامی حساب شما غیرفعال شده است!")
                return redirect('accounts:signin')
            return redirect('client:index')
        form = LoginForm(request.POST)
        if form.is_valid():
            code = persian_digits_to_english(form.cleaned_data.get('code'))
            mobile = persian_digits_to_english(form.cleaned_data.get('mobile'))
            try:
                user = User.objects.get(username=code)
            except User.DoesNotExist:
                messages.error(request, 'حساب کاربری با این کد ملی وجود ندارد، لطفا ابتدا ثبت نام کنید!')
                return render(request, 'accounts/signin.html', {'form':form})
            auser = authenticate(username=code, password=mobile)
            if auser is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('office:home')
                return redirect('client:index')
            elif not user.is_active and user.check_password(mobile):
                try:
                    tk = TokenModel.objects.get(user=user)
                except TokenModel.DoesNotExist:
                    tk = TokenModel(user=user)
                otp = send_token(mobile)
                tk.otp = otp['code']
                tk.status = otp['status']
                tk.save()
                return redirect('accounts:verify', code=user.username)
            else:
                messages.error(request, 'شماره موبایل اشتباه است!')
                return render(request, 'accounts/signin.html', {'form':form})
        else:
            return render(request, 'accounts/signin.html', {'form':form})
        

class SignOutView(views.View):

    def get(self, request):
        logout(request)
        return redirect('accounts:signin')