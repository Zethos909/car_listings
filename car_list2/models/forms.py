
from django import forms

class ListingFilterForm(forms.Form):
    year_min = forms.IntegerField(label='Minimum Year', required=False)
    make = forms.CharField(label='Make', max_length=100, required=False)
