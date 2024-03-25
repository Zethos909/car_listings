from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import ListingFilterForm
import requests
from mysqlconnection import connect_to_mysql

# Then, you can use the function to establish a database connection
conn = connect_to_mysql()


def listings_view(request):
    form = ListingFilterForm(request.GET)
    params = {}

    if form.is_valid():
        year_min = form.cleaned_data.get('year_min')
        make = form.cleaned_data.get('make')

        if year_min:
            params['year_min'] = year_min
        if make:
            params['make'] = make

    # Make the API request with the updated parameters
    url = 'https://auto.dev/api/listings'
    headers = {'Authorization': 'Bearer YOUR_API_KEY'}
    response = requests.get(url, headers=headers, params=params)
    data = response.json() if response.status_code == 200 else {'records': []}

    listings = data.get('records', [])

    # Extracting relevant data for each listing
    formatted_listings = []
    for listing in listings:
        formatted_listing = {
            'make': listing.get('make', ''),
            'model': listing.get('model', ''),
            'price': listing.get('price', ''),
            'image_url': listing.get('primaryPhotoUrl', ''),
            'detail_url': listing.get('clickoffUrl', '')  # Updated to use clickoffUrl
        }

        # Check if the detail_url is valid and contains 'vdp'
        if formatted_listing['detail_url'] and 'vdp' in formatted_listing['detail_url']:
            # If it contains 'vdp', keep the original detail_url
            formatted_listing['detail_url'] = formatted_listing['detail_url']
        else:
            # If not, append 'vdp' to the URL
            formatted_listing['detail_url'] = formatted_listing['detail_url'] + 'vdp'

        formatted_listings.append(formatted_listing)

    return render(request, 'listings.html', {'listings': formatted_listings, 'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Replace 'home' with the name of your home page URL pattern
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Replace 'home' with the name of your home page URL pattern
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})