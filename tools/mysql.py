import pymysql

db = pymysql.connect(host='localhost', user='root', password='howyoung', database='novel')
cursor = db.cursor()


def select_books():
    sql = "select * from book"
    print(sql)
    try:
        cursor.execute(sql)
    except:
        print("Could not execute query: " + sql)
    res = cursor.fetchall()
    return res


def select_book_by_name(name):
    sql = "select * from book where name = '{}'".format(name)
    print(sql)
    try:
        cursor.execute(sql)
    except:
        print("Could not execute query: " + sql)
    res = cursor.fetchall()
    # print(res)
    return res


def insert_book(book):
    sql = "insert into book (name, cover, hot, status, description, category, author, word, updated)" \
          "values ('{}', '{}', '{}', {}, '{}', '{}', '{}', '{}','{}')".format(
        book.name, book.cover, book.hot, book.status, book.description, book.category, book.author, book.word, book.update)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("Could not insert book: " + sql)
        db.rollback()


def insert_chapter(id, name, content):
    sql = "insert into chapter (bookid, name, content)" \
          "values ({}, '{}', '{}')".format(id, name, content)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("Could not insert book: " + sql)
        db.rollback()


def insert_collect(id):
    sql = "insert into collect(bookid) values({})".format(id)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("could not insert collect: " + sql)
        db.rollback()


def insert_rank(id):
    sql = "insert into `rank`(bookid) values({})".format(id)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("could not insert rank: " + sql)
        db.rollback()


def insert_recommend(id):
    sql = "insert into recommend(bookid) values({})".format(id)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("could not insert recommend: " + sql)
        db.rollback()


def insert_top(id):
    sql = "insert into top(bookid) values({})".format(id)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("could not insert top: " + sql)
        db.rollback()


def close():
    cursor.close()
    db.close()
