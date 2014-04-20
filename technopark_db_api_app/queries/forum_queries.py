from django.db import connection
from technopark_db_api_app.functions import dictfetchone, dictfetchall


__author__ = 'Ivan'

def addForum(name, short_name, user):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO forums (name, short_name, user_id) "
            "VALUES (%s, %s, (SELECT id FROM users WHERE email=%s))",
            (name, short_name, user,))
        connection.commit()
    except Exception:
        raise
    finally:
        cursor.close()


def getAddedForum(short_name):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT "
            "forums.id AS id, "
            "forums.name AS name, "
            "forums.short_name as short_name, "
            "users.email AS user "
            "FROM forums JOIN users ON forums.user_id = users.id "
            "WHERE forums.short_name = %s """,
            (short_name,))
        forum = dictfetchone(cursor)
        cursor.close()
        if not forum:
            raise Exception("Forum doesn't exist")
    except Exception:
        raise
    else:
        return forum
    finally:
        cursor.close()


def getDetailedForum(short_name, related):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT "
            "forums.id AS id, "
            "forums.name AS name, "
            "forums.short_name AS short_name, "
            "users.email AS user "
            "FROM forums JOIN users ON forums.user_id = users.id "
            "WHERE forums.short_name = %s """,
            (short_name,)
        )
        forum = dictfetchone(cursor)
        cursor.close()
        if not forum:
            raise Exception("Forum doesn't exists")
        if 'user' in related:
            from technopark_db_api_app.queries import user_queries
            forum['user'] = user_queries.getDetailedUser(forum['user'])
    except Exception:
        raise
    else:
        return forum
    finally:
        cursor.close()

def getPostsList(short_name, since, order, limit, related):
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
            "posts.isSpam AS isSpam, "
            "posts.likes AS likes, "
            "posts.message AS message, "
            "posts.post_id as parent, "
            "posts.likes - posts.dislikes AS points, "
            "threads.id AS thread, users.email AS user "
            "FROM posts RIGHT JOIN threads ON posts.thread_id = threads.id "
            "RIGHT JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE forums.short_name=%r "
            % (str(short_name)))
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

        if 'user' in related:
            for post in posts:
                from technopark_db_api_app.queries import user_queries
                post['user'] = user_queries.getDetailedUser(post['user'])

        if 'thread' in related:
            for post in posts:
                from technopark_db_api_app.queries import thread_queries
                post['thread'] = thread_queries.getDetailedThread(post['thread'], [])

        if 'forum' in related:
            for post in posts:
                post['forum'] = getDetailedForum(post['forum'], [])

    except Exception:
        raise

    else:
        return posts
    finally:
        cursor.close()



def getThreadsList(short_name, since, order, limit, related):
    cursor = connection.cursor()
    try:
        query = (
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
            "FROM forums LEFT JOIN threads ON forums.id = threads.forum_id "
            "JOIN users ON threads.user_id = users.id "
            "LEFT JOIN posts ON posts.thread_id = thread_id "
            "WHERE forums.short_name= %r "
            "GROUP BY forums.short_name, threads.slug "
            % str(short_name))
        if since:
            query += "AND threads.date >= %r " % str(since)
        if order:
            query += "ORDER BY threads.date %s " % order
        if limit:
            query += "LIMIT %s " % limit
        cursor.execute(query)
        threads = dictfetchall(cursor)
        cursor.close()
        for thread in threads:
            thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
            thread['isClosed'] = bool(thread['isClosed'])
            thread['isDeleted'] = bool(thread['isDeleted'])

        if 'user' in related:
            for thread in threads:
                from technopark_db_api_app.queries import user_queries
                thread['user'] = user_queries.getDetailedUser(thread['user'])

        if 'forum' in related:
            for thread in threads:
                thread['forum'] = getDetailedForum(thread['forum'], [])

    except Exception:
        raise
    else:
        return threads
    finally:
        cursor.close()


def getUsersList(short_name, since_id, order, limit):
    cursor = connection.cursor()
    try:
        query = (
            "SELECT DISTINCT "
            "users.email AS email, "
            "users.id AS id, "
            "users.isAnonymous AS isAnonymous, "
            "users.name AS name, "
            "users.username AS username, "
            "users.about AS about "
            "FROM forums LEFT JOIN threads ON forums.id = threads.forum_id "
            "LEFT JOIN posts ON posts.thread_id = threads.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE forums.short_name=%r "
            % str(short_name)
        )
        if since_id:
            query += "AND users.id >= %s " % since_id
        if order:
            query += "ORDER BY users.id %s " % order
        if limit:
            query += "LIMIT %s " % limit

        cursor.execute(query)
        users = dictfetchall(cursor)

        cursor.close()
        for user in users:
            user['isAnonymous'] = bool(user['isAnonymous'])
    except Exception:
        raise
    else:
        return users
    finally:
        cursor.close()