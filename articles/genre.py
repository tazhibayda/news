import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('C:\\Users\\akimi\\PycharmProjects\\news\\db.sqlite3')
    cursor = conn.cursor()
    for i in range(33,41):
        cursor.execute('''insert into
                        articles_article_genres (article_id, genre_id)
                        values (?,?);''',(i,5))
        conn.commit()
        print("added")
    cursor.close()
    conn.close()