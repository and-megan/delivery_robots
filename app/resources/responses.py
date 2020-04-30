from flask import jsonify, make_response
from flask_restful import abort


def not_found_response(resource_name, id):
    return abort(404, error='{} {} could not be found'.format(resource_name, id))


def deleted_response():
    return make_response(jsonify(message='success'), 204)

def no_input_response():
    return abort(400, error='No input data provided')


def invalid_args_response(msgs):
    return abort(400, errors=msgs)
