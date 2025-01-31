from django import forms
from .models import *
from client.models import *
from django.core.exceptions import ValidationError
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

def is_code(value):
    if len(value) != 10 or not str(value).isnumeric():
        raise ValidationError('کد ملی صحیح نمی‌باشد!')
    
def is_mobile(value):
    if not str(value).isnumeric() or len(value) !=11 or str(value)[0] != '0':
        raise ValidationError('شماره موبایل صحیح نمی‌باشد!')
    
def is_phone(value):
    if not str(value).isnumeric() or len(value) !=11 or str(value)[0] != '0':
        raise ValidationError('شماره تلفن صحیح نمی‌باشد!')
    
def is_ncode(value):
    if len(value) != 11 or not str(value).isnumeric():
        raise ValidationError("شناسه ملی صحیح نمی‌باشد.")
    
def is_postal(value):
    if len(value) != 10 or not str(value).isnumeric():
        raise ValidationError('کد پستی صحیح نمی‌باشد!')
    
def is_positive(value):
    if not str(value).isnumeric():
        raise ValidationError('لطفاً فقط عدد وارد کنید!')
    if str(value).isnumeric():
        if int(value) < 1:
            raise ValidationError('عدد باید بزرگتر از صفر باشد!')
        
def is_discount(value):
    if not str(value).isnumeric():
        raise ValidationError('لطفاً فقط عدد وارد کنید!')
    if str(value).isnumeric():
        if int(value) < 0:
            raise ValidationError('کمترین مقدار می‌تواند عدد صفر باشد!')


class CustomerAddForm(forms.ModelForm):
    code = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="کد ملی", validators=[is_code])
    mobile = forms.CharField(max_length=11, required=True, widget=forms.TextInput(attrs={'class':'form-control'}), label="موبایل", validators=[is_mobile])
    ncode = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شناسه ملی", validators=[is_ncode])
    phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شماره ثابت", validators=[is_phone])
    fax = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="شماره فکس", validators=[is_phone])
    postalcode = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class':'form-control'}), label="کد پستی", validators=[is_postal])

    class Meta:
        model = CustomerModel
        fields = (
                  'kind',
                  'sid',
                  'is_active',
                  'first_name',
                  'last_name',
                  'code',
                  'brand',
                  'ceoname',
                  'company',
                  'ncode',
                  'mobile',
                  'phone',
                  'fax',
                  'email',
                  'postalcode',
                  'address',
                  )
        widgets = {
            'kind': forms.Select(attrs={'class':'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-control', 'style': 'float:right', "checked":True}),
            'sid': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'brand': forms.TextInput(attrs={'class':'form-control'}),
            'ceoname': forms.TextInput(attrs={'class':'form-control'}),
            'company': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'address': forms.Textarea(attrs={'class':'form-control', 'rows':3}),
        }


class CustomerChangeForm(CustomerAddForm):
    code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'hidden':True}), validators=[is_code])
    mobile = forms.CharField(max_length=11, required=True, widget=forms.TextInput(attrs={'class':'form-control', 'hidden':True}), label="موبایل", validators=[is_mobile])


class DocumentForm(forms.Form):
    file = forms.FileField(label='مدرک')


class MessageForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':2}), label="توضیحات", required=False)


# class MessageAddForm(forms.ModelForm):

#     class Meta:
#         model = MessagesModel
#         fields = (
#             'customer',
#             'text',
#         )
#         widgets = {
#             'customer': forms.Select(attrs={'class':'form-control', 'id':'id_user'}),
#             'text': forms.Textarea(attrs={'class':'form-control', 'rows':2}),
#         }


class RequestAcceptForm(forms.Form):
    area = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label="متراژ", validators=[is_positive])
    discount = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label="تخفیف", required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':2}), label="توضیحات", required=False)


class ExhibitionForm(forms.ModelForm):

    class Meta:
        model = ExhibitionModel
        fields = (
            'is_active',
            'sid',
            'title',
            'price',
            'value_added',
            'min_area',
            'date',
        )
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class':'form-control', 'style': 'float:right', 'checked':True}),
            'sid': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'price': forms.TextInput(attrs={'class':'form-control'}),
            'value_added': forms.TextInput(attrs={'class':'form-control'}),
            'min_area': forms.TextInput(attrs={'class':'form-control'}),
            'date': forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ExhibitionForm, self).__init__(*args, **kwargs)
        self.fields['date'] = JalaliDateField(label="تاریخ برگزاری", # date format is  "yyyy-mm-dd"
            widget=AdminJalaliDateWidget() # optional, to use default datepicker
        )


class InvoiceAddForm(forms.Form):
    valet = forms.ModelChoiceField(queryset=ValetModel.objects.filter(customer__is_active=True), label="مشارکت کننده")
    booth_number = forms.CharField(label="شماره غرفه", max_length=4, required=False, validators=[is_positive], widget=forms.TextInput(attrs={'class':'form-control'}))
    area = forms.CharField(label="متراژ(مترمربع)", max_length=6, required=True, validators=[is_positive], widget=forms.TextInput(attrs={'class':'form-control'}))


class AddToExhibitionForm(forms.Form):
    valet = forms.ModelChoiceField(queryset=ValetModel.objects.filter(customer__is_active=True), label="مشارکت کننده")
    booth_number = forms.CharField(max_length=50, required=False, label="شماره غرفه", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_positive])
    discount = forms.CharField(max_length=50, required=True, label="تخفیف(درصد)", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_discount])
    area = forms.CharField(max_length=15, required=True, label="متراژ(مترمربع)", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_positive])


class InvoiceEditForm(forms.Form):
    is_active = forms.BooleanField(label="فعال", widget=forms.CheckboxInput(attrs={'class':'form-control', 'style': 'float:right'}))
    valet = forms.ModelChoiceField(queryset=ValetModel.objects.filter(customer__is_active=True), label="مشارکت کننده", widget=forms.Select(attrs={'class':'form-control'}))
    exhibition = forms.ModelChoiceField(queryset=ExhibitionModel.objects.filter(is_active=True), label="نمایشگاه", widget=forms.Select(attrs={'class':'form-control'}))
    booth_number = forms.CharField(max_length=50, required=False, label="شماره غرفه", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_positive])
    area = forms.CharField(max_length=15, required=True, label="متراژ(مترمربع)", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_positive])
    discount = forms.CharField(max_length=50, required=True, label="تخفیف(درصد)", widget=forms.TextInput(attrs={'class':'form-control'}), validators=[is_discount])


class PaymentAddForm(forms.Form):
    STATE_CHECK = 'check'
    STATE_CASHE = 'cashe'
    STATE_POS = 'pos'
    STATE_CHOICES = (
        (STATE_POS, 'پوز بانکی'),
        (STATE_CHECK, 'چک بانکی'),
        (STATE_CASHE, 'نقدی'),
    )
    state = forms.CharField(widget=forms.Select(attrs={"class":"form-control"}, choices=STATE_CHOICES), label="نوع پرداخت")
    bank = forms.ModelChoiceField(queryset=BankModel.objects.all(), required=False, label="حساب بانکی", widget=forms.Select(attrs={'class':'form-control'}))
    amount = forms.IntegerField(widget=forms.TextInput(attrs={"class":"form-control"}), min_value=0, label="مبلغ")
    check = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label="سریال چک", required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label="نام صاحب چک", required=False)
    tracenumber = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label="شماره پیگیری", required=False)
    datepaid = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label="تاریخ پرداخت")
    description = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "rows":2}), label="توضیحات", required=False)