import google.generativeai as genai
from django.core.management.base import BaseCommand
from property_data.models import Hotel  
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import re
from google.api_core.exceptions import ResourceExhausted

class RateLimitedGenerativeModel:
    def __init__(self, model, delay=2.0):  # Increased default delay
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

def clean_title(text):
    # Remove any markdown formatting
    text = re.sub(r'\*+', '', text)
    # Remove numbered lists and bullets
    text = re.sub(r'^[IVX]+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*+\s+', '', text, flags=re.MULTILINE)
    # Remove brackets and contained text
    text = re.sub(r'\[.*?\]', '', text)
    # Remove special characters
    text = re.sub(r'[:#\[\]{}]', '', text)
    # Take first line only
    text = text.split('\n')[0].strip()
    # Remove any "options" or similar text
    text = re.sub(r'^.*?options:?\s*', '', text, flags=re.IGNORECASE)
    # Remove any remaining special formatting
    text = re.sub(r'[^a-zA-Z0-9\s:-]', '', text)
    # Clean up multiple spaces
    text = ' '.join(text.split())
    return text[:50].strip()

@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(5)
)
def generate_with_retry(model, prompt):
    return model.generate_content(prompt)

def enhance_hotel_data(api_key):
    genai.configure(api_key=api_key)
    base_model = genai.GenerativeModel('gemini-pro')
    model = RateLimitedGenerativeModel(base_model, delay=2.0)  # Increased delay
    
    hotels = Hotel.objects.all()
    total_hotels = len(hotels)
    
    for index, hotel in enumerate(hotels, 1):
        try:
            print(f"Processing hotel {hotel.id} ({index}/{total_hotels})...")
            
            title_prompt = f"""Task: Create ONE SHORT, ELEGANT hotel title (maximum 50 characters).
            Hotel details:
            - Current name: {hotel.title}
            - Location: {hotel.location}
            - Price range: ${hotel.price}
            - Rating: {hotel.rating}

            Rules:
            1. Provide ONLY the new title
            2. NO explanations or alternatives
            3. NO formatting or special characters
            4. Must be under 50 characters

            Example format:
            Seaside Haven at Palm Beach

            New title:"""
            
            description_prompt = f"""Task: Write ONE brief, elegant hotel description in 2-3 sentences.
            Hotel details:
            - Location: {hotel.location}
            - Price: ${hotel.price}
            - Rating: {hotel.rating}

            Rules:
            1. Provide ONLY the description
            2. NO alternatives or options
            3. NO formatting or special characters
            4. Focus on location and value
            
            Description:"""
            
            # Generate new title
            title_response = generate_with_retry(model, title_prompt)
            new_title = clean_title(title_response.text)
            
            # Add extra delay between requests
            time.sleep(2)
            
            # Generate new description
            description_response = generate_with_retry(model, description_prompt)
            new_description = description_response.text.strip()
            
            # Verify the results aren't empty
            if not new_title or not new_description:
                raise ValueError("Received empty response from API")
            
            # Update the hotel record
            hotel.description = new_description
            hotel.title = new_title
            hotel.save()
            
            print(f"Successfully updated hotel {hotel.id}:")
            print(f"New title: {new_title}")
            print(f"New description: {new_description}")
            print("-" * 50)
            
            # Add delay before processing next hotel
            time.sleep(3)
            
        except Exception as e:
            print(f"Error processing hotel {hotel.id}: {str(e)}")
            print("Waiting 120 seconds before continuing...")  # Increased wait time
            time.sleep(120)  # Increased wait time after errors
            continue

class Command(BaseCommand):
    help = 'Enhance hotel titles and generate descriptions using Gemini AI'
    
    def add_arguments(self, parser):
        parser.add_argument('api_key', type=str, help='Gemini AI API key')
    
    def handle(self, *args, **options):
        enhance_hotel_data(options['api_key'])
