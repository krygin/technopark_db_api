import json

from django.db import connection
from django.http import HttpResponse


__author__ = 'Ivan'


def clear(request):
    try:
        cursor = connection.cursor()
        cursor.execute("""SET FOREIGN_KEY_CHECKS = 0""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE users""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE forums""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE posts""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE followers""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE threads""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE subscribers""")
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("""SET FOREIGN_KEY_CHECKS = 0""")
        cursor.close()
        response_json = {
            'code': 0,
            'response': 'Database cleared',
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')