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
        cursor.execute("""INSERT INTO threads (forum_id, title, message, date, user_id, slug, isClosed, isDeleted)
                       VALUES ((SELECT id FROM forums WHERE short_name=%s), %s, %s, %s, (SELECT id FROM users WHERE email=%s), %s, %s, %s)""",
                       (parameters['forum'], parameters['title'], parameters['message'], parameters['date'], parameters['user'], parameters['slug'], bool(parameters['isClosed']), bool(parameters['isDeleted']),))
        connection.commit()
        cursor.close()

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
