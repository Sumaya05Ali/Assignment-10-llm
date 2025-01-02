import scrapy
import json
import os
import re
import requests
import random

class TripHotelsSpider(scrapy.Spider):
    name = 'hotels'
    allowed_domains = ['uk.trip.com']
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def __init__(self, *args, **kwargs):
        super(TripHotelsSpider, self).__init__(*args, **kwargs)
        self.save_dir = 'scraped_data'
        os.makedirs(self.save_dir, exist_ok=True)

    def parse(self, response):
        # Step 1: Scrape city URLs
        script_contents = response.xpath('//script[contains(text(), "window.IBU_HOTEL")]/text()').get()

        if script_contents:
            try:
                # Extract JSON-like content containing inbound cities
                json_match = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', script_contents, re.DOTALL)

                if json_match:
                    json_str = json_match.group(1)

                    # Parse the JSON string
                    data = json.loads(json_str)

                    # Extract inbound cities
                    inbound_cities = data.get('initData', {}).get('htlsData', {}).get('inboundCities', [])

                    if inbound_cities:
                        # Randomly select one city from the list of inbound cities
                        selected_city = random.choice(inbound_cities)

                        # Extract city details
                        city_id = selected_city.get('id')
                        city_name = selected_city.get('name', 'Unknown City')
                        city_url = f'https://uk.trip.com/hotels/list?city={city_id}'

                        self.logger.info(f'Selected city: {city_name} ({city_id}) - {city_url}')

                        # Save selected city details to a JSON file
                        city_data = {
                            'city': city_name,
                            'url': city_url
                        }

                        urls_file_path = os.path.join(self.save_dir, f'selected_city_{city_name}.json')
                        with open(urls_file_path, 'w', encoding='utf-8') as urls_file:
                            json.dump(city_data, urls_file, indent=4, ensure_ascii=False)

                        self.logger.info(f'Successfully saved selected city URL to {urls_file_path}')

                        # Step 2: Send a new request to fetch hotel data for the selected city
                        yield scrapy.Request(url=city_url, callback=self.parse_city_hotels, meta={'city': city_name})

                    else:
                        self.logger.error('No inbound cities found')

            except json.JSONDecodeError as e:
                self.logger.error(f'JSON Decode Error: {e}')
            except Exception as e:
                self.logger.error(f'Unexpected error: {e}')
        else:
            self.logger.error('No script tag containing IBU_HOTEL data was found')

    def parse_city_hotels(self, response):
        city_name = response.meta['city']

        # Extract the script containing hotel data
        script_contents = response.xpath('//script[contains(text(), "window.IBU_HOTEL")]/text()').get()

        if script_contents:
            try:
                # Extract JSON data from the script using regex
                json_match = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', script_contents, re.DOTALL)

                if json_match:
                    json_str = json_match.group(1)

                    # Parse the JSON string
                    data = json.loads(json_str)

                    # Extract hotelList data
                    hotel_list = data.get('initData', {}).get('firstPageList', {}).get('hotelList', [])

                    extracted_data = []

                    if hotel_list:
                        for hotel in hotel_list:
                            # Extract required fields from hotel data
                            hotel_name = hotel.get('hotelBasicInfo', {}).get('hotelName', 'Unknown Hotel')
                            rating = hotel.get('commentInfo', {}).get('commentScore', 'No Rating')
                            location = hotel.get('hotelBasicInfo', {}).get('hotelAddress', 'No Address')
                            latitude = hotel.get('positionInfo', {}).get('mapCoordinate', [{}])[0].get('latitude', 'No Latitude')
                            longitude = hotel.get('positionInfo', {}).get('mapCoordinate', [{}])[0].get('longitude', 'No Longitude')
                            room_type = hotel.get('roomInfo', {}).get('physicalRoomName', 'Not Available')
                            price = hotel.get('hotelBasicInfo', {}).get('price', 'N/A')
                            image_url = hotel.get('hotelBasicInfo', {}).get('hotelImg', '')

                            # Save the image and get the file path
                            image_name = None
                            if image_url:
                                image_name = image_url.split('/')[-1]
                                image_path = os.path.join(self.save_dir, 'images', image_name)

                                # Download image and save it
                                try:
                                    with open(image_path, 'wb') as img_file:
                                        img_file.write(requests.get(image_url).content)
                                except Exception as img_err:
                                    self.logger.error(f'Error downloading image: {img_err}')

                            # Prepare the hotel data to save in JSON
                            hotel_data = {
                                'title': hotel_name,
                                'rating': rating,
                                'location': location,
                                'latitude': latitude,
                                'longitude': longitude,
                                'room_type': room_type,
                                'price': price,
                                'image': image_name if image_url else 'No Image',
                                'city': city_name
                            }
                            extracted_data.append(hotel_data)

                        # Pass data to pipeline
                        for hotel in extracted_data:
                            yield hotel

            except json.JSONDecodeError as e:
                self.logger.error(f'JSON Decode Error: {e}')
            except Exception as e:
                self.logger.error(f'Unexpected error: {e}')
