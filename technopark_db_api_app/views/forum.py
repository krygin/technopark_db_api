import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import validate_required_parameters, dictfetchone, validate_optional_parameters, \
    dictfetchall


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['name', 'short_name', 'user'])

        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO forums (name, short_name, user_id)
                       VALUES (%s, %s, (SELECT id FROM users WHERE email=%s))""",
            (parameters['name'], parameters['short_name'], parameters['user'],))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT forums.id AS id, forums.name AS name, forums.short_name as short_name, users.email AS user FROM forums INNER JOIN users ON forums.user_id = users.id WHERE forums.short_name = %s """,
            (parameters['short_name'],))
        forum = dictfetchone(cursor)
        cursor.close()
        response_json = {
            'code': 0,
            'response': forum,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


def details(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['forum'])
        validate_optional_parameters(parameters, ['related'], [[]])

        cursor = connection.cursor()
        cursor.execute(
            """SELECT forums.id AS id, forums.name AS name, forums.short_name as short_name, users.email AS user FROM forums INNER JOIN users ON forums.user_id = users.id WHERE forums.short_name = %s """,
            (parameters['forum'],))
        forum = dictfetchone(cursor)
        cursor.close()

        if not forum:
            raise Exception("Forum doesn't exists")
        if 'user' in parameters['related']:
            cursor = connection.cursor()
            cursor.execute("""SELECT email, id, isAnonymous, name
                       FROM users
                       WHERE email = %s""",
                           (forum['user'],))
            user = dictfetchone(cursor)
            cursor.close()
            if not user:
                raise Exception("User doesn't exists")
            user['isAnonymous'] = bool(user['isAnonymous'])
            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (forum['user'],))
            user['followers'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (forum['user'],))
            user['following'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT thread_id FROM Subscribtions WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
                (forum['user'],))
            user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
            cursor.close()
            forum['user'] = user
        response_json = {
            'code': 0,
            'response': forum,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


def listPosts(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['forum'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since'], ['0', 'desc', '1000-01-01 00:00:00'])

        cursor = connection.cursor()
        if parameters['limit'] != '0':
            cursor.execute(
                """SELECT posts.date AS date, posts.dislikes AS dislikes, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.likes AS likes, posts.message AS message, posts_parent.id as parent, (posts.likes - posts.dislikes) AS points, threads.id AS thread, users.email AS user
                FROM ((((posts INNER JOIN threads ON posts.thread_id = threads.id)
                INNER JOIN forums ON threads.forum_id = forums.id)
                INNER JOIN users ON posts.user_id = users.id)
                LEFT JOIN posts AS posts_parent ON posts.post_id = posts_parent.id)
                WHERE forums.short_name=%s AND posts.date > %s ORDER BY %s LIMIT %s""", (parameters['forum'], parameters['since'], parameters['order'], parameters['limit'],))
        else:
            cursor.execute(
                """SELECT posts.date AS date, posts.dislikes AS dislikes, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.likes AS likes, posts.message AS message, posts_parent.id as parent, (posts.likes - posts.dislikes) AS points, threads.id AS thread, users.email AS user
                FROM ((((posts INNER JOIN threads ON posts.thread_id = threads.id)
                INNER JOIN forums ON threads.forum_id = forums.id)
                INNER JOIN users ON posts.user_id = users.id)
                LEFT JOIN posts AS posts_parent ON posts.post_id = posts_parent.id)
                WHERE forums.short_name=%s AND posts.date > %s ORDER BY %s""", (parameters['forum'], parameters['since'], parameters['order'],))
        posts = dictfetchall(cursor)
        cursor.close()
        for post in posts:
            post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        if 'thread' in parameters['related']:
            for post in posts:
                cursor = connection.cursor()
                cursor.execute(
                    """SELECT threads.date AS date, threads.dislikes AS dislikes, forums.short_name AS forum, threads.id AS id, threads.isClosed AS isClosed, threads.isDeleted AS isDeleted, threads.likes AS likes, threads.message AS message, (threads.likes - threads.dislikes) AS points, COUNT(posts.id) AS posts, threads.slug AS slug, threads.title AS title, users.email AS user
                    FROM ((threads INNER JOIN forums ON threads.forum_id = forums.id)
                    INNER JOIN posts ON threads.id = posts.thread_id)
                    INNER JOIN users ON threads.user_id = users.id
                    WHERE threads.id=%s """, (int(post['thread']),))
                thread = dictfetchone(cursor)
                cursor.close()
                thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
                post['thread'] = thread

        if 'user' in parameters['related']:
            for post in posts:
                cursor = connection.cursor()
                cursor.execute(
                    """SELECT about, email, id, isAnonymous, name, username
                    FROM users
                    WHERE email=%s""", (post['user'],))
                user = dictfetchone(cursor)
                cursor.close()
                user['isAnonymous'] = bool(user['isAnonymous'])
                cursor = connection.cursor()
                cursor.execute(
                    """SELECT following_users.email
                    FROM (users INNER JOIN followers ON users.id = followers.followee_id)
                    INNER JOIN users AS following_users ON followers.follower_id = following_users.id
                    WHERE users.email=%s AND followers.follows = TRUE""",
                    (post['user'],))
                user['followers'] = [item['email'] for item in dictfetchall(cursor)]
                cursor.close()

                cursor = connection.cursor()
                cursor.execute(
                    """SELECT followed_users.email
                    FROM (users INNER JOIN followers ON users.id = followers.follower_id)
                    INNER JOIN users AS followed_users ON followers.followee_id = followed_users.id
                    WHERE users.email=%s AND followers.follows = TRUE""",
                    (post['user'],))
                user['following'] = [item['email'] for item in dictfetchall(cursor)]
                cursor.close()

                cursor = connection.cursor()
                cursor.execute(
                    """SELECT subscriptions.thread_id
                    FROM users INNER JOIN subscriptions ON users.id = subscriptions.user_id
                    WHERE users.email = %s AND subscribed = TRUE""",
                    (post['user'],))
                user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
                post['user'] = user
        if 'forum' in parameters['related']:
            for post in posts:
                cursor = connection.cursor()
                cursor.execute(
                    """SELECT forums.id AS id, forums.name AS name, forums.short_name as short_name, users.email AS user FROM forums INNER JOIN users ON forums.user_id = users.id WHERE forums.short_name = %s """,
                    (post['forum'],))
                forum = dictfetchone(cursor)
                cursor.close()
                post['forum'] = forum
        response_json = {
            'code': 0,
            'response': posts,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')