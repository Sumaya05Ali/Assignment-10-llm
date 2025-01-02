from django.db import models

class Hotel(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    rating = models.CharField(max_length=10)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    room_type = models.CharField(max_length=255)
    price = models.FloatField()
    image = models.CharField(max_length=255)
    city_id = models.IntegerField()
    description = models.TextField(null=True, blank=True)  # Add this line

    class Meta:
        db_table = 'hotels'
        managed = False

    def __str__(self):
        return self.title
    
class PropertySummary(models.Model):
    property_id = models.IntegerField()
    summary = models.TextField()

    class Meta:
        db_table = 'property_summaries'    

class PropertyReview(models.Model):
    property_id = models.IntegerField(primary_key=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()
    
    class Meta:
        db_table = 'property_reviews'
