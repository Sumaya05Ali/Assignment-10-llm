# admin.py

from django.contrib import admin
from .models import Hotel, PropertySummary

class HotelAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'location', 'price', 'city_id')  # Add other fields as needed
    search_fields = ('title', 'location')
    list_filter = ('rating', 'city_id')
    
    # Make sure description is visible in the form
    fields = ('title', 'rating', 'location', 'latitude', 'longitude', 'room_type', 'price', 'city_id', 'description')


class PropertySummaryAdmin(admin.ModelAdmin):
    list_display = ('property_id', 'truncated_summary')
    search_fields = ('property_id', 'summary')
    list_select_related = True  # For better performance when displaying related hotel info
    
    def truncated_summary(self, obj):
        """Display a truncated version of the summary in the list view"""
        return obj.summary[:100] + '...' if len(obj.summary) > 100 else obj.summary
    truncated_summary.short_description = 'Summary'

    def hotel_title(self, obj):
        """Display the related hotel title"""
        try:
            hotel = Hotel.objects.get(id=obj.property_id)
            return hotel.title
        except Hotel.DoesNotExist:
            return 'N/A'
    hotel_title.short_description = 'Hotel Title'

    # Add hotel title to list display
    list_display = ('property_id', 'hotel_title', 'truncated_summary')
    
    # Add readonly fields
    readonly_fields = ('property_id',)    

admin.site.register(Hotel, HotelAdmin)
admin.site.register(PropertySummary, PropertySummaryAdmin)
