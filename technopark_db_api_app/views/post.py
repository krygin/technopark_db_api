import json

from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.functions import validate_required_parameters, validate_optional_parameters, dictfetchone
from technopark_db_api_app.queries import post_queries


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['date', 'thread', 'message', 'user', 'forum'])
        validate_optional_parameters(parameters,
                                     ['parent', 'isApproved', 'isHighlighted', 'isEdited', 'isSpam', 'isDeleted'],
                                     [None, False, False, False, False, False])
        post_queries.addPost(parameters['forum'],
                             parameters['thread'],
                             parameters['user'],
                             parameters['message'],
                             parameters['date'],
                             parameters['parent'],
                             parameters['isApproved'],
                             parameters['isHighlighted'],
                             parameters['isEdited'],
                             parameters['isSpam'],
                             parameters['isDeleted'])
        post = post_queries.getAddedPost(parameters['forum'],
                                         parameters['thread'],
                                         parameters['user'],
                                         parameters['date'])
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

        post = post_queries.getDetailedPost(parameters['post'], parameters['related'])

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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['post'])

        post = post_queries.restorePost(parameters['post'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['post'])
        post = post_queries.removePost(parameters['post'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['post', 'vote'])
        post = post_queries.votePost(parameters['post'], parameters['vote'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['message', 'post'])
        post_queries.updatePost(parameters['post'], parameters['message'])
        post = post_queries.getDetailedPost(parameters['post'], [])
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
        validate_optional_parameters(parameters, ['since', 'limit', 'order'], [None, None, 'desc'])
        if 'forum' in parameters and 'thread' not in parameters:
            from technopark_db_api_app.queries import forum_queries

            posts = forum_queries.getPostsList(parameters['forum'],
                                               parameters['since'],
                                               parameters['order'],
                                               parameters['limit'], [])
        elif 'thread' in parameters and 'forum' not in parameters:
            from technopark_db_api_app.queries import thread_queries

            posts = thread_queries.getPostsList(parameters['thread'],
                                                parameters['since'],
                                                parameters['order'],
                                                parameters['limit'])
        else:
            raise Exception("Wrong required parameters")
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


