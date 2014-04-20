from django.db import connection

from technopark_db_api_app.functions import dictfetchone


__author__ = 'Ivan'


def addPost(forums_short_name, threads_id, user, message, date, parent, isApproved, isHighlighted, isEdited, isSpam,
            isDeleted):
    cursor = connection.cursor()
    try:
        if not __postExists(forums_short_name, threads_id, user, date):
            cursor.execute(
                "INSERT INTO posts (thread_id, message, date, user_id, isApproved, isHighlighted, isEdited, isSpam, isDeleted, post_id)"
                "VALUES ((SELECT threads.id FROM threads JOIN forums ON threads.forum_id = forums.id WHERE forums.short_name = %s AND threads.id = %s), %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s, %s, %s, %s)""",
                (forums_short_name, int(threads_id), message, date, user,
                 bool(isApproved), bool(isDeleted), bool(isEdited), bool(isHighlighted), bool(isDeleted), parent,))
            connection.commit()
        else:
            raise Exception("Post already exists")
    except Exception:
        raise
    finally:
        cursor.close()


def getAddedPost(forums_short_name, threads_id, users_email, date):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT "
            "posts.date AS date, "
            "forums.short_name AS forum, "
            "posts.id AS id, "
            "posts.isApproved AS isApproved, "
            "posts.isDeleted AS isDeleted, "
            "posts.isEdited AS isEdited, "
            "posts.isHighlighted AS isHighlighted, "
            "posts.isSpam AS isSpam, "
            "posts.message AS message, "
            "threads.id AS thread, "
            "users.email AS user "
            "FROM posts RIGHT JOIN threads ON posts.thread_id = threads.id "
            "RIGHT JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE forums.short_name = %s AND threads.id = %s AND users.email=%s AND posts.date=%s""",
            (forums_short_name, threads_id, users_email, date))
        post = dictfetchone(cursor)
        cursor.close()
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        post['isDeleted'] = bool(post['isDeleted'])
    except Exception:
        raise
    else:
        return post
    finally:
        cursor.close()


def __postExists(forums_short_name, threads_id, users_email, date):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT * "
            "FROM posts JOIN threads ON posts.thread_id = threads.id "
            "JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE forums.short_name = %s AND threads.id = %s AND users.email=%s AND posts.date=%s""",
            (forums_short_name, threads_id, users_email, date))
        post = cursor.fetchone()
    except Exception:
        raise
    else:
        return bool(post)
    finally:
        cursor.close()



def getDetailedPost(id, related):
    cursor = connection.cursor()
    try:
        cursor.execute(
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
            "posts.post_id AS parent, "
            "posts.likes - posts.dislikes AS points, "
            "posts.thread_id AS thread, "
            "users.email AS user "
            "FROM posts RIGHT JOIN threads ON posts.thread_id = threads.id "
            "RIGHT JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE posts.id = %s """, (id,))
        post = dictfetchone(cursor)
        cursor.close()
        if not post:
            raise Exception("Post doesn't exist")
        if 'user' in related:
            from technopark_db_api_app.queries import user_queries
            post['user'] = user_queries.getDetailedUser(post['user'])
        if 'thread' in related:
            from technopark_db_api_app.queries import thread_queries
            post['thread'] = thread_queries.getDetailedThread(post['thread'],[])
        if 'forum' in related:
            from technopark_db_api_app.queries import forum_queries
            post['forum'] = forum_queries.getDetailedForum(post['forum'], [])

        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        raise
    else:
        return post
    finally:
        cursor.close()

def restorePost(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE posts SET isDeleted = FALSE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS post FROM posts WHERE  id = %s AND isDeleted = FALSE", (id,))
        post = dictfetchone(cursor)
        cursor.close()
        if not post:
            raise Exception("Post doesn't exist")
    except Exception:
        raise
    else:
        return post
    finally:
        cursor.close()


def removePost(id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE posts SET isDeleted = TRUE WHERE id = %s", (id,))
        connection.commit()
        cursor.execute("SELECT id AS post FROM posts WHERE  id = %s AND isDeleted = TRUE", (id,))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Post doesn't exist")
    except Exception:
        raise
    else:
        return thread
    finally:
        cursor.close()


def votePost(id, vote):
    cursor = connection.cursor()
    try:
        if vote == '1':
            cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = %s ", (id,))
        elif vote == '-1':
            cursor.execute("UPDATE posts SET dislikes = dislikes + 1 WHERE id = %s ", (id,))
        else:
            raise Exception("Wrong vote value")
        cursor.execute("SELECT id AS post FROM posts WHERE  id = %s ", (id,))
        post = dictfetchone(cursor)
        cursor.close()
    except Exception:
        raise
    else:
        return post
    finally:
        cursor.close()


def updatePost(id, message):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE posts SET message=%s WHERE id = %s ", (message, id,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()