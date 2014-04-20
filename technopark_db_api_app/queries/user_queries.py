from django.db import connection

from technopark_db_api_app.functions import dictfetchone, dictfetchall


__author__ = 'Ivan'


def getDetailedUser(email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT about, email, id, isAnonymous, name, username "
            "FROM users "
            "WHERE email = %s",
            (email,))
        user = dictfetchone(cursor)
        if not user:
            raise Exception("User doesn't exist")
        user['followers'] = __getFollowers(email)
        user['following'] = __getFollowees(email)
        user['subscriptions'] = __getSubscriptions(email)
        user['isAnonymous'] = bool(user['isAnonymous'])
    except Exception:
        raise
    else:
        return user
    finally:
        cursor.close()


def __getFollowers(email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT following_users.email "
            "FROM users JOIN followers ON users.id = followers.followee_id "
            "JOIN users AS following_users ON followers.follower_id = following_users.id "
            "WHERE users.email=%s AND followers.follows = TRUE",
            (email,))
        followers = [item['email'] for item in dictfetchall(cursor)]
    except Exception:
        raise
    else:
        return followers
    finally:
        cursor.close()


def __getFollowees(email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT followed_users.email "
            "FROM users JOIN followers ON users.id = followers.follower_id "
            "JOIN users AS followed_users ON followers.followee_id = followed_users.id "
            "WHERE users.email=%s AND followers.follows = TRUE",
            (email,))
        following = [item['email'] for item in dictfetchall(cursor)]
    except Exception:
        raise
    else:
        return following
    finally:
        cursor.close()


def __getSubscriptions(email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT subscribers.thread_id "
            "FROM users JOIN subscribers ON users.id = subscribers.user_id "
            "WHERE users.email = %s AND subscribed = TRUE",
            (email,))
        subscriptions = [item['thread_id'] for item in dictfetchall(cursor)]
    except Exception:
        raise
    else:
        return subscriptions
    finally:
        cursor.close()


def createUser(email, username, name, about, isAnonymous):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, username, name, about, isAnonymous) "
            "VALUES (%s, %s, %s, %s, %s)",
            (email, username, name, about, isAnonymous,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()


def getCreatedUser(email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT about, email, id, isAnonymous, name, username "
            "FROM users "
            "WHERE email = %s ",
            (email,))
        user = dictfetchone(cursor)
        if not user:
            raise Exception("User doesn't exist")
        user['isAnonymous'] = bool(user['isAnonymous'])
    except Exception:
        raise
    else:
        return user
    finally:
        cursor.close()


def followUser(follower_email, followee_email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO followers (follower_id, followee_id, follows) "
            "VALUES ((SELECT id FROM users WHERE email=%s), (SELECT id FROM users WHERE email=%s), TRUE)"
            "ON DUPLICATE KEY UPDATE follows=TRUE",
            (follower_email, followee_email,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()


def unfollowUser(follower_email, followee_email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO followers (follower_id, followee_id, follows) "
            "VALUES ((SELECT id FROM users WHERE email=%s), (SELECT id FROM users WHERE email=%s), FALSE ) "
            "ON DUPLICATE KEY UPDATE follows=FALSE ",
            (follower_email, followee_email,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()


def getFolloweesList(email, since_id, order, limit):
    cursor = connection.cursor()
    try:
        query = (
             "SELECT "
             "followed_user.about AS about, "
             "followed_user.email AS email, "
             "followed_user.id AS id, "
             "followed_user.isAnonymous AS isAnonymous, "
             "followed_user.name AS name, "
             "followed_user.username AS username "
             "FROM users JOIN followers ON users.id = followers.follower_id "
             "JOIN users AS followed_user ON followers.followee_id = followed_user.id "
             "WHERE users.email = %r AND followers.follows = TRUE "
             % (str(email)))
        if since_id:
            query += "AND followed_user.id >= %s " % since_id
        if order:
            query += "ORDER BY followed_user.name %s " % order
        if limit:
            query += "LIMIT %s " % limit

        cursor.execute(query)
        users = dictfetchall(cursor)
        for user in users:
            user['followers'] = __getFollowers(user['email'])
            user['following'] = __getFollowees(user['email'])
            user['subscriptions'] = __getSubscriptions(user['email'])
            user['isAnonymous'] = bool(user['isAnonymous'])
    except Exception:
        raise
    else:
        return users
    finally:
        cursor.close()


def getFollowersList(email, since_id, order, limit):
    cursor = connection.cursor()
    try:
        query = (
            "SELECT "
            "following_user.about AS about, "
            "following_user.email AS email, "
            "following_user.id AS id, "
            "following_user.isAnonymous AS isAnonymous, "
            "following_user.name AS name, "
            "following_user.username AS username "
            "FROM users JOIN followers ON users.id = followers.followee_id "
            "JOIN users AS following_user ON followers.follower_id = following_user.id "
            "WHERE users.email = %r AND followers.follows = TRUE "
            % (str(email)))
        if since_id:
            query += "AND following_user.id >= %s " % since_id
        if order:
            query += "ORDER BY following_user.name %s " % order
        if limit:
            query += "LIMIT %s " % limit
        cursor.execute(query)
        users = dictfetchall(cursor)

        for user in users:
            user['followers'] = __getFollowers(user['email'])
            user['following'] = __getFollowees(user['email'])
            user['subscriptions'] = __getSubscriptions(user['email'])
            user['isAnonymous'] = bool(user['isAnonymous'])
    except Exception:
        raise
    else:
        return users
    finally:
        cursor.close()


def updateUser(email, name, about):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE users SET about=%s, name=%s WHERE email=%s",
                       (email, name, about,))
        connection.commit()
        cursor.close()
    except Exception:
        raise
    finally:
        cursor.close()


def getPostsList(email, since, order, limit):
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
            "FROM posts RIGHT JOIN threads ON posts.thread_id = threads.id "
            "RIGHT JOIN forums ON threads.forum_id = forums.id "
            "JOIN users ON posts.user_id = users.id "
            "WHERE users.email=%r """
            % (str(email)))
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


def getThreadsList(email, since, order, limit):
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
            "threads.likes - posts.dislikes AS points, "
            "COUNT(posts.id) AS posts, "
            "threads.slug AS slug, "
            "threads.title AS title, users.email AS user "
            "FROM forums LEFT JOIN threads ON forums.id = threads.forum_id "
            "JOIN users ON threads.user_id = users.id "
            "LEFT JOIN posts ON posts.thread_id = thread_id "
            "WHERE users.email=%r "
            "GROUP BY forums.short_name, threads.slug "
            % str(email))
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
    except Exception:
        raise
    else:
        return threads
    finally:
        cursor.close()