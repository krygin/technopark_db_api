from django.db import connection
from technopark_db_api_app.functions import dictfetchone, dictfetchall

__author__ = 'Ivan'


def addThread(forums_short_name, slug, title, message, user, date, isClosed, isDeleted):
    cursor = connection.cursor()
    try:
        if not __threadExists(forums_short_name, slug):
            cursor.execute(
                " INSERT INTO threads (forum_id, title, message, date, user_id, slug, isClosed, isDeleted) "
                "VALUES ((SELECT id FROM forums WHERE short_name=%s), %s, %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s)",
                (forums_short_name, title, message, date, user, slug, bool(isClosed),bool(isDeleted),))
            connection.commit()
            cursor.close()
        else:
            raise Exception("Thread already exists")
    except Exception:
        raise
    finally:
        cursor.close()

def getAddedThread(forums_short_name, threads_slug):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT "
            "threads.date AS date, "
            "forums.short_name AS forum, "
            "threads.id AS id, "
            "threads.isClosed AS isClosed, "
            "threads.isDeleted AS isDeleted, "
            "threads.message AS message, "
            "threads.slug AS slug, "
            "threads.title AS title, "
            "users.email AS user "
            "FROM threads JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON threads.user_id = users.id "
            "WHERE forums.short_name = %s AND threads.slug = %s ",
            (forums_short_name, threads_slug,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
        thread['isClosed'] = bool(thread['isClosed'])
        thread['isDeleted'] = bool(thread['isDeleted'])
        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()

def __threadExists(forums_short_name, threads_slug):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT * "
            "FROM threads JOIN forums ON threads.forum_id = forums.id "
            "WHERE threads.slug = %s AND forums.short_name = %s """,
            (threads_slug, forums_short_name,))
        thread = cursor.fetchone()
        cursor.close()
    except Exception:
        raise
    else:
        return bool(thread)
    finally:
        cursor.close()


def getDetailedThread(id, related):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT "
            "threads.date AS date, "
            "threads.dislikes AS dislikes, "
            "forums.short_name AS forum, "
            "threads.id AS id, "
            "threads.isClosed AS isClosed, "
            "threads.isDeleted AS isDeleted, "
            "threads.likes AS likes, "
            "threads.message AS message, "
            "threads.likes - threads.dislikes AS points, "
            "COUNT(posts.id) AS posts, "
            "threads.slug AS slug, "
            "threads.title AS title, "
            "users.email AS user "
            "FROM forums JOIN threads ON forums.id = threads.forum_id "
            "JOIN users ON threads.user_id = users.id "
            "JOIN posts ON posts.thread_id = threads.id "
            "WHERE threads.id = %s""", (id,))

        thread = dictfetchone(cursor)
        cursor.close()
        thread['isClosed'] = bool(thread['isClosed'])
        thread['isDeleted'] = bool(thread['isDeleted'])
        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")

        if 'user' in related:
            from technopark_db_api_app.queries import user_queries
            thread['user'] = user_queries.getDetailedUser(thread['user'])

        if 'forum' in related:
            from technopark_db_api_app.queries import forum_queries
            thread['forum'] = forum_queries.getDetailedForum(thread['forum'], [])

    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()

def closeThread(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE threads SET isClosed = TRUE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS thread FROM threads WHERE  id = %s AND isClosed = TRUE", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()


def openThread(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE threads SET isClosed = FALSE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS thread FROM threads WHERE  id = %s AND isClosed = FALSE", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()


def restoreThread(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE threads SET isDeleted = FALSE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS thread FROM threads WHERE  id = %s AND isDeleted = FALSE", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()


def removeThread(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE threads SET isDeleted = TRUE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS thread FROM threads WHERE  id = %s AND isDeleted = TRUE", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()



def voteThread(id, vote):
    cursor = connection.cursor()
    try:
        if vote == '1':
            cursor.execute("UPDATE threads SET likes = likes + 1 WHERE id = %s ", (id,))
        elif vote == '-1':
            cursor.execute("UPDATE threads SET dislikes = dislikes + 1 WHERE id = %s ", (id,))
        else:
            raise Exception("Wrong vote value")
        cursor.execute("SELECT id AS thread FROM threads WHERE  id = %s ", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()

def subscribeThread(users_email, id):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO subscribers (user_id, thread_id, subscribed) "
            "VALUES ((SELECT id FROM users WHERE email = %s), %s, TRUE) "
            "ON DUPLICATE KEY UPDATE subscribed=TRUE",
            (users_email, int(id),))
        connection.commit()
        cursor.execute(
            "SELECT "
            "threads.id AS thread, "
            "users.email AS user "
            "FROM threads JOIN subscribers ON threads.id = subscribers.thread_id "
            "JOIN users ON subscribers.user_id = users.id "
            "WHERE users.email = %s AND threads.id = %s AND subscribers.subscribed = TRUE", (users_email, id, ))
        thread = dictfetchone(cursor)
        cursor.close()
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()

def unsubscribeThread(users_email, id):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO subscribers (user_id, thread_id, subscribed) "
            "VALUES ((SELECT id FROM users WHERE email = %s), %s, FALSE) "
            "ON DUPLICATE KEY UPDATE subscribed=FALSE ",
            (users_email, int(id),))
        connection.commit()
        cursor.execute(
            "SELECT "
            "threads.id AS thread, "
            "users.email AS user "
            "FROM threads JOIN subscribers ON threads.id = subscribers.thread_id "
            "JOIN users ON subscribers.user_id = users.id "
            "WHERE users.email = %s AND threads.id = %s AND subscribers.subscribed = FALSE ", (users_email, id, ))
        thread = dictfetchone(cursor)
        cursor.close()
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()



def updateThread(id, slug, message):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT * FROM threads WHERE slug = %s AND forum_id = (SELECT forum_id FROM threads WHERE id = %s)", (slug, id,))
        thread = cursor.fetchone()
        if thread:
            raise Exception("Thread with the same slug already exists in this forum")
        cursor.execute("UPDATE threads SET message=%s, slug=%s WHERE id = %s ", (message, slug, id,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()


def getPostsList(id, since, order, limit):
    cursor = connection.cursor()
    try:
        query = (
            "SELECT "
            "posts.date AS date, "
            "posts.dislikes AS dislikes, "
            "forums.short_name AS forum, "
            "posts.id AS id, "
            "posts.isApproved AS isApproved, "
            "posts.isDeleted AS isDeleted, "
            "posts.isEdited AS isEdited, "
            "posts.isHighlighted AS isHighlighted, "
            "posts.isSpam AS isSpam, posts.likes AS likes, "
            "posts.message AS message, "
            "posts.post_id as parent, "
            "posts.likes - posts.dislikes AS points, "
            "threads.id AS thread, "
            "users.email AS user "
            "FROM posts JOIN threads ON posts.thread_id = threads.id "
            "JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE threads.id = %s """
            % (id,))
        if since:
            query += "AND posts.date >= %r " % str(since)
        if order:
            query += "ORDER BY posts.date %s " % order
        if limit:
            query += "LIMIT %s " % limit
        cursor.execute(query)
        posts = dictfetchall(cursor)
        cursor.close()
        for post in posts:
            post['isApproved'] = bool(post['isApproved'])
            post['isDeleted'] = bool(post['isDeleted'])
            post['isEdited'] = bool(post['isEdited'])
            post['isHighlighted'] = bool(post['isHighlighted'])
            post['isSpam'] = bool(post['isSpam'])
            post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        raise
    else:
        return posts
    finally:
        cursor.close()