import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import validate_required_parameters, validate_optional_parameters, dictfetchone


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'])
        validate_optional_parameters(parameters, ['isDeleted'], [False])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM threads INNER JOIN forums ON threads.forum_id = forums.id WHERE threads.slug = %s AND forums.short_name = %s """,
            (parameters['slug'], parameters['forum'],))
        exists = cursor.fetchone()
        cursor.close()
        if not exists:
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO threads (forum_id, title, message, date, user_id, slug, isClosed, isDeleted)
                           VALUES ((SELECT id FROM forums WHERE short_name=%s), %s, %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s)""",
                           (parameters['forum'], parameters['title'], parameters['message'], parameters['date'],
                            parameters['user'], parameters['slug'], bool(parameters['isClosed']),
                            bool(parameters['isDeleted']),))
            connection.commit()
            cursor.close()
        else:
            raise Exception("Thread already exists")
        cursor = connection.cursor()
        cursor.execute("""SELECT threads.date AS date, forums.short_name AS forum, threads.id AS id, threads.isClosed AS isClosed, threads.isDeleted AS isDeleted, threads.message AS message, threads.slug AS slug, threads.title AS title, users.email AS user
                   FROM ((threads INNER JOIN forums ON threads.forum_id = forums.id)
                   INNER JOIN users ON threads.user_id = users.id)
                   WHERE forums.short_name = %s AND threads.slug = %s """,
                       (parameters['forum'], parameters['slug']))
        thread = dictfetchone(cursor)
        cursor.close()
        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
        thread['isClosed'] = bool(thread['isClosed'])
        thread['isDeleted'] = bool(thread['isDeleted'])
        response_json = {
            'code': 0,
            'response': thread,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def close(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['thread'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE threads SET isClosed = TRUE WHERE id = %s""", (parameters['thread'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS thread FROM threads WHERE  id = %s """, (parameters['thread'],))
        thread = dictfetchone(cursor)
        cursor.close()

        if not thread:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': thread,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def open(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['thread'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE threads SET isClosed = FALSE WHERE id = %s""", (parameters['thread'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS thread FROM threads WHERE  id = %s """, (parameters['thread'],))
        thread = dictfetchone(cursor)
        cursor.close()

        if not thread:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': thread,
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
        validate_required_parameters(parameters, ['thread'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE threads SET isDeleted = FALSE WHERE id = %s""", (parameters['thread'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS thread FROM threads WHERE  id = %s """, (parameters['thread'],))
        thread = dictfetchone(cursor)
        cursor.close()

        if not thread:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': thread,
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
        validate_required_parameters(parameters, ['thread'])

        cursor = connection.cursor()
        cursor.execute(
            """UPDATE threads SET isDeleted = TRUE WHERE id = %s""", (parameters['thread'],))
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS thread FROM threads WHERE  id = %s """, (parameters['thread'],))
        thread = dictfetchone(cursor)
        cursor.close()

        if not thread:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': thread,
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
        validate_required_parameters(parameters, ['thread', 'vote'])

        if parameters['vote'] == '1':
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE threads SET likes = likes + 1 WHERE id = %s""", (parameters['thread'],))
            cursor.close()
        elif parameters['vote'] == '-1':
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE threads SET dislikes = dislikes + 1 WHERE id = %s""", (parameters['thread'],))
            cursor.close()
        else:
            raise Exception("Wrong vote value")

        cursor = connection.cursor()
        cursor.execute("""SELECT id AS thread FROM threads WHERE  id = %s """, (parameters['thread'],))
        thread = dictfetchone(cursor)
        cursor.close()
        if not thread:
            raise Exception("Thread doesn't exist")
        response_json = {
            'code': 0,
            'response': thread,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def subscribe(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['user', 'thread'])
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO subscribers (user_id, thread_id, subscribed) VALUES ((SELECT id FROM users WHERE email=%s), %s, TRUE) ON DUPLICATE KEY UPDATE subscribed=TRUE""",
            (parameters['user'], int(parameters['thread']),))
        connection.commit()
        cursor.close()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT threads.id AS thread,
            users.email AS user
            FROM (threads INNER JOIN subscribers ON threads.id = subscribers.thread_id)
            INNER JOIN users ON subscribers.user_id = users.id
            WHERE users.email = %s AND threads.id = %s AND subscribers.subscribed = TRUE """,
            (parameters['user'], parameters['thread'],))
        subscription = dictfetchone(cursor)
        cursor.close()
        response_json = {
            'code': 0,
            'response': subscription,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def unsubscribe(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['user', 'thread'])
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO subscribers (user_id, thread_id, subscribed) VALUES ((SELECT id FROM users WHERE email=%s), %s, FALSE) ON DUPLICATE KEY UPDATE subscribed=FALSE""",
            (parameters['user'], int(parameters['thread']),))
        connection.commit()
        cursor.close()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT threads.id AS thread,
            users.email AS user
            FROM (threads INNER JOIN subscribers ON threads.id = subscribers.thread_id)
            INNER JOIN users ON subscribers.user_id = users.id
            WHERE users.email = %s AND threads.id = %s AND subscribers.subscribed = FALSE""",
            (parameters['user'], parameters['thread'],))
        subscription = dictfetchone(cursor)
        cursor.close()
        response_json = {
            'code': 0,
            'response': subscription,
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
        validate_required_parameters(parameters, ['message', 'slug', 'thread'])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM threads WHERE slug = %s AND forum_id = (SELECT forum_id FROM threads WHERE id = %s )""",
            (parameters['slug'], parameters['thread'],))
        exists = cursor.fetchone()
        cursor.close()
        if exists:
            raise Exception("Thread with the same slug already exists")
        cursor = connection.cursor()
        cursor.execute("""UPDATE threads SET message=%s, slug=%s WHERE id = %s """,
                       (parameters['message'], parameters['slug'], parameters['thread'],))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT threads.date AS date,
            threads.dislikes AS dislikes,
            forums.short_name AS forum,
            threads.id AS id,
            threads.isClosed AS isClosed,
            threads.isDeleted AS isDeleted,
            threads.likes AS likes,
            threads.message AS message,
            threads.likes - posts.dislikes AS points,
            COUNT(posts.id) AS posts,
            threads.slug AS slug,
            threads.title AS title,
            users.email AS user
            FROM ((forums INNER JOIN threads ON forums.id = threads.forum_id)
            INNER JOIN users ON threads.user_id = users.id)
            INNER JOIN posts ON posts.thread_id = thread_id
            WHERE threads.id = %s""", (parameters['thread'],))

        thread = dictfetchone(cursor)
        cursor.close()
        thread['isClosed'] = bool(thread['isClosed'])
        thread['isDeleted'] = bool(thread['isDeleted'])
        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
        response_json = {
            'code': 0,
            'response': thread,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')