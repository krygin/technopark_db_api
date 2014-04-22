import json

from django.views.decorators.csrf import csrf_exempt

from technopark_db_api_app.queries import user_queries
from technopark_db_api_app.functions import *


__author__ = 'Ivan'


@csrf_exempt
def create(request):
    try:
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ["email", "username", "name", "about"])

        validate_optional_parameters(parameters, ["isAnonymous"], [False])

        user_queries.createUser(parameters['email'],
                                parameters['username'],
                                parameters['name'],
                                parameters['about'],
                                parameters['isAnonymous'])
        user = user_queries.getCreatedUser(parameters['email'])
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
        user = user_queries.getDetailedUser(parameters['user'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['follower', 'followee'])
        user_queries.followUser(parameters['follower'], parameters['followee'])
        user = user_queries.getDetailedUser(parameters['follower'])
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
        validate_optional_parameters(parameters, ['limit', 'order', 'since_id'], [None, 'desc', None])

        users = user_queries.getFollowersList(parameters['user'],
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


def listFollowing(request):
    try:
        parameters = request.GET.dict()
        validate_required_parameters(parameters, ['user'])
        validate_optional_parameters(parameters, ['limit', 'order', 'since_id'], [None, 'desc', None])

        users = user_queries.getFolloweesList(parameters['user'],
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


@csrf_exempt
def unfollow(request):
    try:
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['follower', 'followee'])
        user_queries.unfollowUser(parameters['follower'], parameters['followee'])
        user = user_queries.getDetailedUser(parameters['follower'])
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
        parameters = json.loads(request.body, encoding='utf-8')
        validate_required_parameters(parameters, ['about', 'user', 'name'])

        user_queries.updateUser(parameters['user'], parameters['name'], parameters['about'])
        user = user_queries.getDetailedUser(parameters['user'])

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
        validate_optional_parameters(parameters, ['limit', 'order', 'since'],
                                     [None, 'desc', None])

        posts = user_queries.getPostsList(parameters['user'],
                                           parameters['since'],
                                           parameters['order'],
                                           parameters['limit'])
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