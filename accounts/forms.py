from django import forms
from django.core.exceptions import ValidationError
from .models import TokenModel
    
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

class SignUpForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label="نام",
        required=True
    )
    last_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label="نام خانوادگی",
        required=True
    )
    code = forms.CharField(
        max_length=10,
        validators=[is_code],
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='کد ملی',
    )
    mobile = forms.CharField(
        max_length=11,
        validators=[is_mobile],
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='شماره موبایل',
    )

class LoginForm(forms.Form):
    code = forms.CharField(
        max_length=10,
        validators=[is_code],
        widget=forms.TextInput(attrs={'class':'form-control', 'title':'Please Enter valid email'}),
        label='کد ملی',
    )
    mobile = forms.CharField(
        max_length=11,
        validators=[is_mobile],
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='شماره موبایل',
    )

class TokenForm(forms.ModelForm):

    class Meta:
        model = TokenModel
        fields = (
            'otp',
        )
        widgets = {
            'otp': forms.TextInput(attrs={'class':'form-control'})
        }

class ChangeMobileForm(forms.Form):
    mobile = forms.CharField(
        max_length=11,
        validators=[is_mobile],
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='شماره موبایل',
    )