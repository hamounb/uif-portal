from django import forms
from .models import *
from django.core.exceptions import ValidationError
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from crm.settings import Terminal_id
    
def persian_digits_to_english(s:str):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translate_table = str.maketrans(persian_digits, english_digits)
    return s.translate(translate_table)

def is_code(value):
    if len(value) != 10 or not str(persian_digits_to_english(value)).isnumeric():
        raise ValidationError('کد ملی صحیح نمی‌باشد!')
    
def is_mobile(value):
    if not str(persian_digits_to_english(value)).isnumeric() or len(value) !=11 or str(persian_digits_to_english(value))[0] != '0':
        raise ValidationError('شماره موبایل صحیح نمی‌باشد!')
    
def is_phone(value):
    if not str(persian_digits_to_english(value)).isnumeric() or len(value) !=11 or str(persian_digits_to_english(value))[0] != '0':
        raise ValidationError('شماره تلفن صحیح نمی‌باشد!')
    
def is_ncode(value):
    if len(value) != 11 or not str(persian_digits_to_english(value)).isnumeric():
        raise ValidationError("شناسه ملی صحیح نمی‌باشد.")
    
def is_postal(value):
    if len(value) != 10 or not str(persian_digits_to_english(value)).isnumeric():
        raise ValidationError('کد پستی صحیح نمی‌باشد!')
    
def is_positive(value):
    if not str(persian_digits_to_english(value)).isnumeric():
        raise ValidationError('لطفاً فقط عدد وارد کنید!')
    if str(persian_digits_to_english(value)).isnumeric():
        if int(value) < 1:
            raise ValidationError('عدد باید بزرگتر از صفر باشد!')
        
def is_discount(value):
    if not str(persian_digits_to_english(value)).isnumeric():
        raise ValidationError('لطفاً فقط عدد وارد کنید!')
    if str(persian_digits_to_english(value)).isnumeric():
        if int(value) < 0:
            raise ValidationError('کمترین مقدار می‌تواند عدد صفر باشد!')
        

class PaymentCreateForm(forms.Form):
    TerminalID = forms.CharField(widget=forms.TextInput(attrs={'name':'TerminalID'}))
    token = forms.CharField(widget=forms.TextInput(attrs={'name':'token'}))
        

class ProfileAddForm(forms.Form):
    KIND_REAL = 'real'
    KIND_LEGAL = 'legal'
    KIND_CHOICES = (
        (KIND_REAL, 'حقیقی'),
        (KIND_LEGAL, 'حقوقی')
    )
    kind = forms.CharField(widget=forms.Select(attrs={"class":"form-control"}, choices=KIND_CHOICES), label="نوع مشارکت کننده")
    first_name = forms.CharField(max_length=250, required=False, disabled=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="نام")
    last_name = forms.CharField(max_length=250, required=False, disabled=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="نام خانوادگی")
    code = forms.CharField(max_length=10, required=False, disabled=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="کد ملی", validators=[is_code])
    brand = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="نام تجاری")
    ceoname = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="نام مدیرعامل")
    company = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="نام شرکت")
    ncode = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شناسه ملی", validators=[is_ncode])
    mobile = forms.CharField(max_length=11, required=False, disabled=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="موبایل", validators=[is_mobile])
    phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شماره ثابت", validators=[is_phone])
    fax = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شماره فکس", validators=[is_phone])
    email = forms.EmailField(max_length=250, required=False, widget=forms.EmailInput(attrs={'class':'form-control'}), label="ایمیل")
    postalcode = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="کد پستی", validators=[is_postal])
    address = forms.CharField(max_length=250, required=True, widget=forms.Textarea(attrs={'class':'form-control', 'rows':3}), label="آدرس")


class DocumentAddForm(forms.Form):
    file = forms.FileField(label="مدارک")


class RequestAddForm(forms.Form):
    exhibition = forms.CharField(label="عنوان نمایشگاه", required=True, widget=forms.Select())
    customer = forms.CharField(label="حساب کاربری", required=True, widget=forms.Select())
    rules = forms.BooleanField(label="قوانین و مقررات", required=True)
    description = forms.CharField(label="توضیحات", required=True, widget=forms.Textarea(attrs={"class":"form-control", "rows":"5"}))