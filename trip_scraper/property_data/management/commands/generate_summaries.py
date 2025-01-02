# management/commands/generate_summaries.py

import google.generativeai as genai
from django.core.management.base import BaseCommand
from property_data.models import Hotel, PropertySummary  # Replace 'your_app' with your actual app name
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

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

def generate_property_summaries(api_key):
    genai.configure(api_key=api_key)
    base_model = genai.GenerativeModel('gemini-pro')
    model = RateLimitedGenerativeModel(base_model, delay=2.0)
    
    hotels = Hotel.objects.all()
    total_hotels = len(hotels)
    
    for index, hotel in enumerate(hotels, 1):
        try:
            print(f"Processing hotel {hotel.id} ({index}/{total_hotels})...")
            
            summary_prompt = f"""Create a comprehensive summary of this hotel property:

            Property Details:
            - Name: {hotel.title}
            - Location: {hotel.location}
            - Price: ${hotel.price}
            - Rating: {hotel.rating}
            - Room Type: {hotel.room_type}
            - Description: {hotel.description}
            - Coordinates: {hotel.latitude}, {hotel.longitude}

            Rules:
            1. Write a detailed 3-4 sentence summary
            2. Highlight unique features and location benefits
            3. Include price point and value proposition
            4. Mention the rating and room type
            5. Keep it professional and factual

            Summary:"""
            
            # Generate summary
            summary_response = generate_with_retry(model, summary_prompt)
            summary = summary_response.text.strip()
            
            # Verify the summary isn't empty
            if not summary:
                raise ValueError("Received empty response from API")
            
            # Save to PropertySummary table
            PropertySummary.objects.update_or_create(
                property_id=hotel.id,
                defaults={'summary': summary}
            )
            
            print(f"Successfully generated summary for hotel {hotel.id}")
            print(f"Summary: {summary}")
            print("-" * 50)
            
            # Add delay before processing next hotel
            time.sleep(3)
            
        except Exception as e:
            print(f"Error processing hotel {hotel.id}: {str(e)}")
            print("Waiting 120 seconds before continuing...")
            time.sleep(120)
            continue

class Command(BaseCommand):
    help = 'Generate property summaries using Gemini AI'
    
    def add_arguments(self, parser):
        parser.add_argument('api_key', type=str, help='Gemini AI API key')
    
    def handle(self, *args, **options):
        generate_property_summaries(options['api_key'])