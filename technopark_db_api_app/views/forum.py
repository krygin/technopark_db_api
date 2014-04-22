import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import validate_required_parameters, dictfetchone, validate_optional_parameters, \
    dictfetchall
from technopark_db_api_app.queries import forum_queries


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['name', 'short_name', 'user'])

        forum_queries.addForum(parameters['name'], parameters['short_name'], parameters['user'])
        forum = forum_queries.getAddedForum(parameters['short_name'])
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
        forum = forum_queries.getDetailedForum(parameters['forum'], parameters['related'])
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
        validate_optional_parameters(parameters, ['limit', 'order', 'since', 'related'], [None, 'desc', None, []])

        posts = forum_queries.getPostsList(parameters['forum'],
                                           parameters['since'],
                                           parameters['order'],
                                           parameters['limit'],
                                           parameters['related'])
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



def listThreads(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['forum'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since', 'related'], [None, 'desc', None, []])

        threads = forum_queries.getThreadsList(parameters['forum'],
                                               parameters['since'],
                                               parameters['order'],
                                               parameters['limit'],
                                               parameters['related'])
        response_json = {
            'code': 0,
            'response': threads,
        }
    except Exception as e:
        response_json = {
            'code': 1,
            'response': str(e),
        }
    return HttpResponse(json.dumps(response_json, ensure_ascii=False), content_type='application/json')


def listUsers(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['forum'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since_id'], [None, 'desc', None])

        users = forum_queries.getUsersList(parameters['forum'],
                                           parameters['since_id'],
                                           parameters['order'],
                                           parameters['limit'])
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