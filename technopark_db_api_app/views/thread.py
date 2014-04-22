import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import validate_required_parameters, validate_optional_parameters, dictfetchone
from technopark_db_api_app.queries import thread_queries

__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'])
        validate_optional_parameters(parameters, ['isDeleted'], [False])

        thread_queries.addThread(parameters['forum'],
                                 parameters['slug'],
                                 parameters['title'],
                                 parameters['message'],
                                 parameters['user'],
                                 parameters['date'],
                                 parameters['isClosed'],
                                 parameters['isDeleted'])
        thread = thread_queries.getAddedThread(parameters['forum'], parameters['slug'])
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


def details(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['thread'])
        validate_optional_parameters(parameters, ['related'], [[]])

        thread = thread_queries.getDetailedThread(parameters['thread'],
                                                  parameters['related'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['thread'])
        thread = thread_queries.closeThread(parameters['thread'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['thread'])
        thread = thread_queries.openThread(parameters['thread'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['thread'])
        thread = thread_queries.restoreThread(parameters['thread'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['thread'])
        thread = thread_queries.removeThread(parameters['thread'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['thread', 'vote'])
        thread = thread_queries.voteThread(parameters['thread'], parameters['vote'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['user', 'thread'])
        subscription = thread_queries.subscribeThread(parameters['user'], parameters['thread'])

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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['user', 'thread'])
        subscription = thread_queries.unsubscribeThread(parameters['user'], parameters['thread'],)
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['message', 'slug', 'thread'])

        thread_queries.updateThread(parameters['thread'], parameters['slug'], parameters['message'])
        thread = thread_queries.getDetailedThread(parameters['thread'], [])
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


def listPosts(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['thread'])
        validate_optional_parameters(parameters, ['since', 'limit', 'order'], [None, None, 'desc'])
        threads = thread_queries.getPostsList(parameters['thread'],
                                           parameters['since'],
                                           parameters['order'],
                                           parameters['limit'])
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


def list(request):
    try:
        parameters = request.GET.dict()
        validate_optional_parameters(parameters, ['since', 'limit', 'order'], [None, None, 'desc'])
        if 'user' in parameters and 'forum' not in parameters:
            from technopark_db_api_app.queries import user_queries
            threads = user_queries.getThreadsList(parameters['user'],
                                                  parameters['since'],
                                                  parameters['order'],
                                                  parameters['limit'])
        elif 'forum' in parameters and 'user' not in parameters:
            from technopark_db_api_app.queries import forum_queries
            threads = forum_queries.getThreadsList(parameters['forum'],
                                                  parameters['since'],
                                                  parameters['order'],
                                                  parameters['limit'], [])
        else:
            raise Exception("Wrong required parameters")
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