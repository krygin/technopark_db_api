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
        validate_required_parameters(parameters, ['date', 'thread', 'message', 'user', 'forum'])
        validate_optional_parameters(parameters,
                                     ['parent', 'isApproved', 'isHighlighted', 'isEdited', 'isSpam', 'isDeleted'],
                                     [None, False, False, False, False, False])

        cursor = connection.cursor()
        cursor.execute("""INSERT INTO posts (thread_id, message, date, user_id, isApproved, isHighlighted, isEdited, isSpam, isDeleted, post_id)
                       VALUES ((SELECT threads.id FROM threads INNER JOIN forums ON threads.forum_id = forums.id WHERE forums.short_name = %s AND threads.id = %s), %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s, %s, %s, %s)""",
                       (parameters['forum'], int(parameters['thread']), parameters['message'], parameters['date'], parameters['user'], bool(parameters['isApproved']), bool(parameters['isHighlighted']), bool(parameters['isEdited']),bool(parameters['isSpam']), bool(parameters['isDeleted']), parameters['parent'],))
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