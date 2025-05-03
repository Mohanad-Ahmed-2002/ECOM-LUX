from django import forms
from .models import Government,CustomerOrder


class OrderForm(forms.ModelForm):

    government = forms.ModelChoiceField(
        queryset=Government.objects.all(),
        empty_label="Select your governorate",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model=CustomerOrder
        fields=['name','email','address','phone','government']