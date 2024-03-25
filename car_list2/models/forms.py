
from django import forms
from mysqlconnection import connect_to_mysql

# Then, you can use the function to establish a database connection
conn = connect_to_mysql()


class ListingFilterForm(forms.Form):
    year_min = forms.IntegerField(label='Minimum Year', required=False)
    make = forms.CharField(label='Make', max_length=100, required=False)
