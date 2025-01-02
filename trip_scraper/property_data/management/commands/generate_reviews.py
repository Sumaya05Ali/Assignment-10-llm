# management/commands/generate_reviews.py 

import google.generativeai as genai
from django.core.management.base import BaseCommand
from property_data.models import Hotel, PropertyReview  
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
import random
from decimal import Decimal

class RateLimitedGenerativeModel:
    def __init__(self, model, delay=2.0):
        self.model = model
        self.delay = delay
        self.last_request_time = 0

    def generate_content(self, prompt):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.delay:
            time.sleep(self.delay - time_since_last_request)
        
        response = self.model.generate_content(prompt)
        self.last_request_time = time.time()
        return response

@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(5)
)
def generate_with_retry(model, prompt):
    return model.generate_content(prompt)

def generate_property_reviews(api_key):
    genai.configure(api_key=api_key)
    base_model = genai.GenerativeModel('gemini-pro')
    model = RateLimitedGenerativeModel(base_model, delay=2.0)
    
    hotels = Hotel.objects.all()
    total_hotels = len(hotels)
    
    for index, hotel in enumerate(hotels, 1):
        try:
            print(f"Processing hotel {hotel.id} ({index}/{total_hotels})...")
            
            # Calculate a realistic rating based on the hotel's existing rating
            try:
                base_rating = float(hotel.rating)
            except (ValueError, TypeError):
                base_rating = 4.0
            
            # Add small random variation while keeping within 0.5 of original
            variation = random.uniform(-0.5, 0.5)
            new_rating = round(max(1.0, min(5.0, base_rating + variation)), 1)
            
            review_prompt = f"""Generate a detailed hotel review based on these details:

            Hotel Information:
            - Name: {hotel.title}
            - Location: {hotel.location}
            - Price: ${hotel.price}
            - Room Type: {hotel.room_type}
            - Current Rating: {new_rating}
            
            Requirements:
            1. Write a detailed, authentic-sounding review (150-200 words)
            2. Match the tone to the {new_rating}/5.0 rating
            3. Include specific details about location and amenities
            4. Mention the room type and value for money
            5. Keep it balanced and realistic
            
            Write ONLY the review text, no additional formatting or rating numbers.
            """
            
            # Generate review
            review_response = generate_with_retry(model, review_prompt)
            review_text = review_response.text.strip()
            
            # Verify the review isn't empty
            if not review_text:
                raise ValueError("Received empty response from API")
            
            # Save to PropertyReview table
            PropertyReview.objects.update_or_create(
                property_id=hotel.id,
                defaults={
                    'rating': Decimal(str(new_rating)),
                    'review': review_text
                }
            )
            
            print(f"Successfully generated review for hotel {hotel.id}")
            print(f"Rating: {new_rating}")
            print(f"Review: {review_text[:100]}...")
            print("-" * 50)
            
            # Add delay before processing next hotel
            time.sleep(3)
            
        except Exception as e:
            print(f"Error processing hotel {hotel.id}: {str(e)}")
            print("Waiting 120 seconds before continuing...")
            time.sleep(120)
            continue

class Command(BaseCommand):
    help = 'Generate property reviews using Gemini AI'
    
    def add_arguments(self, parser):
        parser.add_argument('api_key', type=str, help='Gemini AI API key')
    
    def handle(self, *args, **options):
        generate_property_reviews(options['api_key'])