from drf_yasg.inspectors import SwaggerAutoSchema

class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys=None):
        # кастомный operationId
        return '_'.join(operation_keys)