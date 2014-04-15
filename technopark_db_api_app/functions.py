from django.db import connection
from django.http import HttpResponse

__author__ = 'Ivan'


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor):
    desc = cursor.description
    row = cursor.fetchone()
    if row is None:
        return {}
    else:
        return dict(zip([col[0] for col in desc], row))


def validate_required_parameters(parameters, required):
    for parameter in required:
        if parameter not in parameters:
            raise Exception("Parameter " + str(parameter) + " requires")


def validate_optional_parameters(parameters, optional, defaults):
    i = 0
    for parameter in optional:
        if parameter not in parameters:
            parameters[parameter] = defaults[i]
        i += 1