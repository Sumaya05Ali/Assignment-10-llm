from django.core.management.base import BaseCommand
import google.generativeai as genai
from property_data.models import Hotel
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates new titles and descriptions for hotels using Gemini AI'

    def handle(self, *args, **options):
        # Configure Gemini
        GEMINI_API_KEY = 'AIzaSyAq32r9K9sjKDKfDfUWZ-CAG-PW8I4c0EM'  # Replace with your actual API key
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Get all hotels
        hotels = Hotel.objects.all()
        total_hotels = hotels.count()
        
        logger.info(f"Starting to process {total_hotels} hotels")

        for hotel in hotels:
            try:
                logger.info(f"Processing hotel ID: {hotel.id}")
                
                # Generate new title based on the original title with more precise instructions
                title_prompt = f"Rewrite this hotel title to make it more professional and appealing, and output only the rewritten title without explanations or commentary. Title: '{hotel.title}'"
                response = model.generate_content(title_prompt)
                
                # Ensure we're only capturing the first line or direct output without extra information
                new_title = response.text.strip().split('\n')[0]

                time.sleep(2)  # Wait between API calls
                
                # Generate description based on hotel information
                description_prompt = f"""
                Create a detailed hotel description based on the following details:
                - Location: {hotel.location}
                - Coordinates: {hotel.latitude}, {hotel.longitude}
                - Rating: {hotel.rating}
                - Room Type: {hotel.room_type}
                - Price: ${hotel.price}

                Highlight the hotel's location, amenities, and overall value, and make it sound appealing for potential guests.
                Maximum 500 characters.
                """
                new_description = model.generate_content(description_prompt).text.strip()

                # Save updates in the database
                hotel.title = new_title
                hotel.description = new_description
                hotel.save()

                logger.info(f"""
                Updated hotel {hotel.id}:
                New title: {new_title}
                Description preview: {new_description[:100]}...
                """)

                time.sleep(3)  # Wait between hotels

            except Exception as e:
                logger.error(f"Error processing hotel {hotel.id}: {str(e)}")
                continue

        logger.info("Finished processing all hotels")

        # Verify updates
        sample_hotel = Hotel.objects.first()
        if sample_hotel and sample_hotel.description:
            logger.info("Updates successful! Sample hotel data:")
            logger.info(f"Title: {sample_hotel.title}")
            logger.info(f"Description: {sample_hotel.description[:100]}...")
        else:
            logger.error("Updates may not have been saved correctly")
