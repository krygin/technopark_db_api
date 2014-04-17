import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from technopark_db_api_app import views

from technopark_db_api_app.functions import validate_required_parameters, validate_optional_parameters, dictfetchone, \
    dictfetchall


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['date', 'thread', 'message', 'user', 'forum'])
        validate_optional_parameters(parameters,
                                     ['parent', 'isApproved', 'isHighlighted', 'isEdited', 'isSpam', 'isDeleted'],
                                     [None, False, False, False, False, False])

        cursor = connection.cursor()
        cursor.execute("""INSERT INTO posts (thread_id, message, date, user_id, isApproved, isHighlighted, isEdited, isSpam, isDeleted, post_id)
                       VALUES ((SELECT threads.id FROM threads INNER JOIN forums ON threads.forum_id = forums.id WHERE forums.short_name = %s AND threads.id = %s), %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s, %s, %s, %s)""",
                       (parameters['forum'], int(parameters['thread']), parameters['message'], parameters['date'],
                        parameters['user'], bool(parameters['isApproved']), bool(parameters['isHighlighted']),
                        bool(parameters['isEdited']), bool(parameters['isSpam']), bool(parameters['isDeleted']),
                        parameters['parent'],))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT posts.date AS date, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.message AS message, threads.id AS thread, users.email AS user
                   FROM (((posts INNER JOIN threads ON posts.thread_id = threads.id)
                   INNER JOIN forums ON threads.forum_id = forums.id)
                   INNER JOIN users ON posts.user_id = users.id)
                   WHERE forums.short_name = %s AND threads.id = %s AND users.email=%s AND posts.date=%s""",
                       (parameters['forum'], parameters['thread'], parameters['user'], parameters['date']))
        post = dictfetchone(cursor)
        cursor.close()
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        post['isDeleted'] = bool(post['isDeleted'])
        response_json = {
            'code': 0,
            'response': post,
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
        validate_required_parameters(parameters, ['post'])
        validate_optional_parameters(parameters, ['related'], [[]])

        cursor = connection.cursor()
        cursor.execute(
            """SELECT posts.date AS date,
            posts.dislikes AS dislikes,
            forums.short_name AS forum,
            posts.id AS id,
            posts.isApproved AS isApproved,
            posts.isDeleted AS isDeleted,
            posts.isEdited AS isEdited,
            posts.isHighlighted AS isHighlighted,
            posts.isSpam AS isSpam,
            posts.likes AS likes,
            posts.message AS message,
            posts.post_id AS parent,
            posts.likes - posts.dislikes AS points,
            posts.thread_id AS thread,
            users.email AS user
            FROM ((posts INNER JOIN threads ON posts.thread_id = threads.id)
            INNER JOIN forums ON threads.forum_id = forums.id)
            INNER JOIN users ON posts.user_id = users.id
            WHERE posts.id = %s """, (parameters['post'],))
        post = dictfetchone(cursor)
        cursor.close()
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        if 'thread' in parameters['related']:
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
            cursor = connection.cursor()
            cursor.execute(
                """SELECT forums.id AS id, forums.name AS name, forums.short_name as short_name, users.email AS user FROM forums INNER JOIN users ON forums.user_id = users.id WHERE forums.short_name = %s """,
                (post['forum'],))
            forum = dictfetchone(cursor)
            cursor.close()
            post['forum'] = forum
        response_json = {
            'code': 0,
            'response': post,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def restore(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['post'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE posts SET isDeleted = FALSE WHERE id = %s""", (parameters['post'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS post FROM posts WHERE  id = %s """, (parameters['post'],))
        post = dictfetchone(cursor)
        cursor.close()

        if not post:
            raise Exception("Post doesn't exist")
        response_json = {
            'code': 0,
            'response': post,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def remove(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['post'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE posts SET isDeleted = TRUE WHERE id = %s""", (parameters['post'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS posts FROM threads WHERE  id = %s """, (parameters['post'],))
        post = dictfetchone(cursor)
        cursor.close()

        if not post:
            raise Exception("Post doesn't exist")
        response_json = {
            'code': 0,
            'response': post,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def vote(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['post', 'vote'])

        if parameters['vote'] == '1':
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE posts SET likes = likes + 1 WHERE id = %s""", (parameters['post'],))
            cursor.close()
        elif parameters['vote'] == '-1':
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE posts SET dislikes = dislikes + 1 WHERE id = %s""", (parameters['post'],))
            cursor.close()
        else:
            raise Exception("Wrong vote value")

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS post FROM posts WHERE  id = %s """, (parameters['post'],))
        post = dictfetchone(cursor)
        cursor.close()
        if not post:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': post,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def update(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['message', 'post'])
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM posts WHERE id = %s """, (parameters['post'],))
        exists = cursor.fetchone()
        if not exists:
            raise Exception("Post doesn't exist")
        cursor = connection.cursor()
        cursor.execute("""UPDATE posts SET message=%s WHERE id = %s """,
                       (parameters['message'], parameters['post'],))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT posts.date AS date, posts.dislikes AS dislikes, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.likes AS likes, posts.message AS message, posts_parent.id as parent, (posts.likes - posts.dislikes) AS points, threads.id AS thread, users.email AS user
            FROM ((((posts INNER JOIN threads ON posts.thread_id = threads.id)
            INNER JOIN forums ON threads.forum_id = forums.id)
            INNER JOIN users ON posts.user_id = users.id)
            LEFT JOIN posts AS posts_parent ON posts.post_id = posts_parent.id)
            WHERE posts.id = %s """, (parameters['post'],))
        post = dictfetchone(cursor)
        cursor.close()
        response_json = {
            'code': 0,
            'response': post,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')

def list(request):
    try:
        parameters = request.GET.dict()
        if 'forum' in parameters:
            return views.forum.listPosts(request)
        elif 'thread' in parameters:
            return views.thread.listPosts(request)
        else:
            raise Exception("Forum or thread requires")
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
        return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')