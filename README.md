# Assignment-10-llm
# Django CLI Application for Property Information Rewrite

This project is a Django-based CLI application that integrates with the Gemini-2.0-Flash-Exp language model to rewrite property titles and descriptions. The application reads existing property information from a PostgreSQL database, processes it using the model, and stores rewritten titles, descriptions, summaries, ratings, and reviews back into the database.

## Features
- Rewrites property titles and descriptions using the Gemini-2.0-Flash-Exp model.
- Generates property summaries based on the scraped property data.
- Generates ratings and reviews using a Large Language Model (LLM).
- Stores the rewritten information, summary, rating, and review in separate PostgreSQL tables.
- Uses Django ORM for database interactions and a Django management command to run the tasks.

## Requirements
- Python 3.x
- Django 4.x
- PostgreSQL
- A valid API key for the Gemini-2.0-Flash-Exp model

## Setup
1. Clone the repository:

```bash
git clone https://github.com/Sumaya05Ali/Assignment-10-llm.git
cd Assignment-10-llm-main
 ```
2. Create a virtual environment and activate it:

```bash

python3 -m venv .venv
source .venv/bin/activate
 ```
3. API key

```bash
GEMINI_API_KEY = 'AIzaSyAq32r9K9sjKDKfDfUWZ-CAG-PW8I4c0EM'
  ```
4. Build and run the application with Docker
Ensure Docker and Docker Compose are installed, then run the following commands:

```bash
docker-compose up --build
 ```
This will:

Start a PostgreSQL database container.
Build and run the Django application on http://localhost:8000.
Prepare Scrapy to run on the same PostgreSQL database.

5. Run migrations to set up the database tables
In another terminal, execute the following commands to run database migrations and create the required tables:

```bash
docker-compose exec django python manage.py migrate
  ```
6. Create a Django superuser to access the admin interface
Run the following command to create a superuser:

```bash
docker-compose exec django python manage.py createsuperuser
  ```
7. Scrape property data with Scrapy
You can trigger Scrapy to start crawling property data using this command:

```bash
docker-compose exec scraper scrapy crawl hotels
 ```
This will scrape the property data and store it in the PostgreSQL database.

8. Rewrite property titles and descriptions
You can run the Django CLI management command to process the property information and store the results:

```bash
docker-compose exec django python manage.py rewrite_property  AIzaSyAq32r9K9sjKDKfDfUWZ-CAG-PW8I4c0EM
docker-compose exec django python manage.py generate_summaries AIzaSyAq32r9K9sjKDKfDfUWZ-CAG-PW8I4c0EM
docker-compose exec django python manage.py generate_reviews   AIzaSyAq32r9K9sjKDKfDfUWZ-CAG-PW8I4c0EM

 ```

9. Access the Django admin interface
Open your browser and go to http://localhost:8000/admin/. Log in using the superuser credentials you created, where you can view and manage property information, summaries, reviews, and ratings.

## Docker Configuration
'docker-compose.yml'
This file defines three services:

- db: A PostgreSQL database that stores property data.
- django: The Django service that handles the application logic.
- scraper: The Scrapy service for scraping property data.

 ```bash
services:
  db:
    image: postgres:latest
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: shared_db
    volumes:
      - db_data:/var/lib/postgresql/data

  django:
    build: .
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/shared_db
    volumes:
      - ./trip_scraper:/code 
    ports:
      - "8000:8000"
    depends_on:
      - db
    command: python manage.py runserver 0.0.0.0:8000

  scraper:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/shared_db
    volumes:
      - .:/code 
    depends_on:
      - db
    command: scrapy crawl hotels

volumes:
  db_data:
  ```
## License
This project is licensed under the MIT License.
