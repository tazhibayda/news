import requests
from django.core.management.base import BaseCommand
from articles.models import Article, Genre
from django.contrib.auth.models import User

API_KEY = 'f4ebddcdcb9d4c34a1987ca5fef20267'
BASE_URL = 'https://newsapi.org/v2/everything?q=all&apiKey=' + API_KEY


class Command(BaseCommand):
    help = 'Fetch news articles from the API and save them to the database'

    def handle(self, *args, **kwargs):
        page = 1
        while True:
            # Fetch data from API with pagination
            response = requests.get(f'{BASE_URL}&page={page}')

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total_results = data.get('totalResults', 0)

                # If no articles or page is empty, stop fetching
                if not articles:
                    self.stdout.write(self.style.SUCCESS('No more articles to fetch.'))
                    break

                # Process each article in the current page
                for item in articles:
                    title = item.get('title')
                    content = item.get('content')
                    author_name = item.get('author') if item.get('author') else "Anonymous"
                    source_name = item['source'].get('name')
                    url = item.get('url')
                    url_to_image = item.get('urlToImage')
                    published_at = item.get('publishedAt')

                    # Fetch or create the author (Anonymous if null)
                    author, created = User.objects.get_or_create(username=author_name)

                    # Create or update the article in the database
                    article, created = Article.objects.get_or_create(
                        title=title,
                        defaults={
                            'content': content or 'No content available',
                            'author': author,
                            'source': source_name,
                            'url': url,
                            'image': url_to_image,
                            'created_at': published_at,
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'{"Created" if created else "Updated"} article: {article.title}'))

                self.stdout.write(self.style.SUCCESS(f'Fetched page {page} with {len(articles)} articles.'))

                # If we've processed all the results, stop
                if page * 20 >= total_results:  # Assuming each page contains 20 articles
                    break

                # Move to the next page
                page += 1
            else:
                self.stdout.write(self.style.ERROR('Failed to fetch data from the API'))
                break
