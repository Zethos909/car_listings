from django.shortcuts import render
from .forms import ListingFilterForm
import requests

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
