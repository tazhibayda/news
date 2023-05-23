import imghdr
import os
import sqlite3
import time

import requests
import json

if __name__ == '__main__':
    conn = sqlite3.connect('C:\\Users\\akimi\\PycharmProjects\\news\\db.sqlite3')
    cursor = conn.cursor()

    i = 1

    response_API = requests.get('https://newsapi.org/v2/everything?apiKey=f4ebddcdcb9d4c34a1987ca5fef20267&pageSize=8&q=Economics')
    data = response_API.text
    parse_json = json.loads(data)
    articles = parse_json['articles']
    for article in articles:
        source = article['author']
        author = article['source']
        title = article['title']
        description = article['description']
        image = article['urlToImage']
        url = article['url']
        date = article['publishedAt']
        content = article['content']
        genre = 1
        name = None
        if image is not None:
            img_data = requests.get(image).content
            directory = 'C:\\Users\\akimi\PycharmProjects\\news\media\\article_images\\'
            timestamp = int(time.time() * 1000)
            form = imghdr.what(None, h=img_data)
            filename = f"{timestamp}_{len(img_data)}.{form}"
            name = filename
            filepath = os.path.join(directory, filename)
            with open(filepath, 'wb') as handler:
                handler.write(img_data)

        cursor.execute('''insert into
                articles_article (title, content, author_id, created_at, date_posted, source, image, url)
                values (?,?,?,?,?,?,?,?);''',(title,content,1,date,date,source,name,url))
        conn.commit()
        print(i," Created")
        i = i+1
    cursor.close()
    conn.close()

    # print(active_case)

    # title = models.CharField(max_length=100)
    # source = models.CharField(max_length=100, null=True)
    # content = models.TextField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True)
    # date_posted = models.DateTimeField(auto_now=True)
    # image = models.ImageField(upload_to='article_images', blank=True, null=True)
