import json

from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import *


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['email', 'username', 'name', 'about'])
        validate_optional_parameters(parameters, ['isAnonymous'], [False])

        cursor = connection.cursor()
        cursor.execute("""INSERT INTO users (email, username, name, about, isAnonymous)
                       VALUES (%s, %s, %s, %s, %s)""",
                       (parameters['email'], parameters['username'], parameters['name'], parameters['about'],
                        parameters['isAnonymous']))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM users
                   WHERE email = %s""",
                       (parameters['email'],))
        user = dictfetchone(cursor)
        cursor.close()
        user['isAnonymous'] = bool(user['isAnonymous'])
        response_json = {
            'code': 0,
            'response': user,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def details(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['user'])

        cursor = connection.cursor()
        cursor.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM users
                   WHERE email = %s""",
                       (parameters['user'],))
        user = dictfetchone(cursor)
        cursor.close()
        if not user:
            raise Exception("User doesn't exists")
        user['isAnonymous'] = bool(user['isAnonymous'])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['user'],))
        user['followers'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['user'],))
        user['following'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
            (parameters['user'],))
        user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
        cursor.close()
        response_json = {
            'code': 0,
            'response': user,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def follow(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['follower', 'followee'])
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO followers (follower_id, followee_id, follows) VALUES ((SELECT id FROM users WHERE email=%s), (SELECT id FROM users WHERE email=%s), 1) ON DUPLICATE KEY UPDATE follows=1""",
            (parameters['follower'], parameters['followee']))
        connection.commit()
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM users
                   WHERE email = %s""",
                       (parameters['follower'],))
        user = dictfetchone(cursor)
        cursor.close()
        if not user:
            raise Exception("User doesn't exists")
        user['isAnonymous'] = bool(user['isAnonymous'])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['follower'],))
        user['followers'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['follower'],))
        user['following'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
            (parameters['follower'],))
        user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
        cursor.close()
        response_json = {
            'code': 0,
            'response': user,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


def listFollowers(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['user'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since_id'], ['0', 'desc', '0'])

        cursor = connection.cursor()
        if parameters['limit'] != '0':
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM users WHERE id >= %s AND id IN(SELECT follower_id FROM  followers WHERE followee_id = (SELECT id FROM users WHERE email=%s)) ORDER BY 'name' %s LIMIT %s""",
                (parameters['since_id'], parameters['user'], parameters['order'], int(parameters['limit']),))
        else:
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM users WHERE id >= %s AND id IN(SELECT follower_id FROM  followers WHERE followee_id = (SELECT id FROM users WHERE email=%s)) ORDER BY 'name' %s""",
                (int(parameters['since_id']), parameters['user'], parameters['order'],))
        users = dictfetchall(cursor)
        cursor.close()

        for user in users:
            user['isAnonymous'] = bool(user['isAnonymous'])
            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (user['email'],))
            user['followers'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (user['email'],))
            user['following'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
                (user['email'],))
            user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
            cursor.close()
        response_json = {
            'code': 0,
            'response': users,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


def listFollowing(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['user'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since_id'], ['0', 'desc', '0'])

        cursor = connection.cursor()
        if parameters['limit'] != '0':
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM users WHERE id >= %s AND id IN(SELECT followee_id FROM  followers WHERE follower_id = (SELECT id FROM users WHERE email=%s)) ORDER BY 'name' %s LIMIT %s""",
                (parameters['since_id'], parameters['user'], parameters['order'], int(parameters['limit']),))
        else:
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM users WHERE id >= %s AND id IN(SELECT followee_id FROM  followers WHERE follower_id = (SELECT id FROM users WHERE email=%s)) ORDER BY 'name' %s""",
                (int(parameters['since_id']), parameters['user'], parameters['order'],))
        users = dictfetchall(cursor)
        cursor.close()

        for user in users:
            user['isAnonymous'] = bool(user['isAnonymous'])
            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (user['email'],))
            user['followers'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
                (user['email'],))
            user['following'] = [item['email'] for item in dictfetchall(cursor)]
            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
                (user['email'],))
            user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
            cursor.close()
        response_json = {
            'code': 0,
            'response': users,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def unfollow(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['follower', 'followee'])
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO followers (follower_id, followee_id, follows) VALUES ((SELECT id FROM users WHERE email=%s), (SELECT id FROM users WHERE email=%s), 0) ON DUPLICATE KEY UPDATE follows=0""",
            (parameters['follower'], parameters['followee']))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM users
                   WHERE email = %s""",
                       (parameters['follower'],))
        user = dictfetchone(cursor)
        cursor.close()
        if not user:
            raise Exception("User doesn't exists")
        user['isAnonymous'] = bool(user['isAnonymous'])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['follower'],))
        user['followers'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['follower'],))
        user['following'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
            (parameters['follower'],))
        user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
        cursor.close()
        response_json = {
            'code': 0,
            'response': user,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


@csrf_exempt
def updateProfile(request):
    try:
        parameters = request.POST.dict()
        validate_required_parameters(parameters, ['about', 'user', 'name'])

        cursor = connection.cursor()
        cursor.execute("""UPDATE users SET about=%s, name=%s WHERE email=%s""",
                       (parameters['about'], parameters['name'], parameters['user'],))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM users
                   WHERE email = %s""",
                       (parameters['user'],))
        user = dictfetchone(cursor)
        cursor.close()
        if not user:
            raise Exception("User doesn't exists")
        user['isAnonymous'] = bool(user['isAnonymous'])
        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT follower_id from followers WHERE followee_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['user'],))
        user['followers'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT email from users WHERE id IN (SELECT followee_id from followers WHERE follower_id = (SELECT id FROM users WHERE email=%s) AND follows=TRUE)""",
            (parameters['user'],))
        user['following'] = [item['email'] for item in dictfetchall(cursor)]
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(
            """SELECT thread_id FROM subscribers WHERE user_id = (SELECT id FROM users WHERE email=%s) AND subscribed=TRUE""",
            (parameters['user'],))
        user['subscriptions'] = [item['thread_id'] for item in dictfetchall(cursor)]
        cursor.close()
        response_json = {
            'code': 0,
            'response': user,
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
        validate_required_parameters(parameters, ['user'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since', 'related'],
                                     ['0', 'desc', '1000-01-01 00:00:00', []])

        cursor = connection.cursor()
        if parameters['limit'] != '0':
            cursor.execute(
                """SELECT posts.date AS date, posts.dislikes AS dislikes, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.likes AS likes, posts.message AS message, posts.post_id as parent, (posts.likes - posts.dislikes) AS points, threads.id AS thread, users.email AS user
                FROM (((posts INNER JOIN threads ON posts.thread_id = threads.id)
                INNER JOIN forums ON threads.forum_id = forums.id)
                INNER JOIN users ON posts.user_id = users.id)
                WHERE users.email=%s AND posts.date > %s ORDER BY %s LIMIT %s""",
                (parameters['user'], parameters['since'], parameters['order'], parameters['limit'],))
        else:
            cursor.execute(
                """SELECT posts.date AS date, posts.dislikes AS dislikes, forums.short_name AS forum, posts.id AS id, posts.isApproved AS isApproved, posts.isDeleted AS isDeleted, posts.isEdited AS isEdited, posts.isHighlighted AS isHighlighted, posts.isSpam AS isSpam, posts.likes AS likes, posts.message AS message, posts.post_id as parent, (posts.likes - posts.dislikes) AS points, threads.id AS thread, users.email AS user
                FROM ((((posts INNER JOIN threads ON posts.thread_id = threads.id)
                INNER JOIN forums ON threads.forum_id = forums.id)
                INNER JOIN users ON posts.user_id = users.id)
                LEFT JOIN posts AS posts_parent ON posts.post_id = posts_parent.id)
                WHERE users.email=%s AND posts.date > %s ORDER BY %s""",
                (parameters['user'], parameters['since'], parameters['order'],))
        posts = dictfetchall(cursor)
        cursor.close()
        for post in posts:
            post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
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