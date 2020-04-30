from flask import jsonify, request
from flask_restful import Resource
from app.models import InvalidArguments, NotFound
from app.resources.responses import not_found_response, deleted_response, no_input_response, invalid_args_response

class BaseAPI(Resource):
    @staticmethod
    def _parse_request_json(data):
        raise NotImplemented()

    def get(self, id):
        instance = self.model_cls.get(id)
        if not instance:
            return not_found_response(self.model_cls.__name__, id)

        json_result = self.model_schema.dump(instance)
        return jsonify(json_result.data)

    def put(self, id):
        instance = self.model_cls.get(id)
        if not instance:
            return not_found_response(self.model_cls.__name__, id)

        json_data = request.get_json()
        if not json_data:
            return no_input_response()

        data = self.model_update_schema.load(json_data)
        if data.errors:
            return invalid_args_response(data.errors)

        kwargs = self._parse_request_json(request.json)

        try:
            instance.update(**kwargs)
        except InvalidArguments as e:
            return invalid_args_response(e.args[0])

        json_result = self.model_schema.dump(instance)
        return jsonify(json_result.data)

    def delete(self, id):
        instance = self.model_cls.get(id)
        if not instance:
            return not_found_response(self.model_cls.__name__, id)

        instance.delete()
        return deleted_response()


class BaseListAPI(Resource):
    @staticmethod
    def _parse_schema_data(data):
        raise NotImplemented()

    def get(self):
        qs = request.query_string
        try:
            instances = self.model_cls.get_all(query_string=qs)
        except NotFound as e:
            e_args = e.args[0]
            return not_found_response(e_args['resource_name'], e_args['id'])
        except InvalidArguments as e:
            return invalid_args_response(e.args[0])

        result = self.models_schema.dump(instances)
        return jsonify(result.data)

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return no_input_response()

        data = self.model_schema.load(json_data)
        if data.errors:
            return invalid_args_response(data.errors)

        args = self._parse_schema_data(data)

        try:
            instance = self.model_cls.create(*args)
        except InvalidArguments as e:
            return invalid_args_response(e.args[0])

        schema_result = self.model_schema.dump(instance)
        return jsonify(schema_result.data)

