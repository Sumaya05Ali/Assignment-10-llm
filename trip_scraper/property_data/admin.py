# admin.py

from django.contrib import admin
from .models import Hotel

class HotelAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'location', 'price', 'city_id')  # Add other fields as needed
    search_fields = ('title', 'location')
    list_filter = ('rating', 'city_id')
    
    # Make sure description is visible in the form
    fields = ('title', 'rating', 'location', 'latitude', 'longitude', 'room_type', 'price', 'city_id', 'description')

admin.site.register(Hotel, HotelAdmin)
