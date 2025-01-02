from .models import Hotel, City, init_db

import os

class PostgresPipeline:
    def __init__(self):
        self.session = init_db()

    def process_item(self, item, spider):
        # Process the hotel data
        hotel = Hotel(
            title=item['title'],
            rating=item['rating'],
            location=item['location'],
            latitude=item['latitude'],
            longitude=item['longitude'],
            room_type=item['room_type'],
            price=item['price'],
            image=item['image']  # Save image reference path
        )

        # Check if the city exists, if not, create a new city record
        city_name = item['city']
        city = self.session.query(City).filter_by(name=city_name).first()
        if not city:
            city = City(name=city_name)
            self.session.add(city)
            self.session.commit()

        # Assign the city to the hotel
        hotel.city_id = city.id
        self.session.add(hotel)
        self.session.commit()

        return item

    def close_spider(self, spider):
        self.session.close()
