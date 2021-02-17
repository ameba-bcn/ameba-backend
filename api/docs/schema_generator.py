from drf_yasg.generators import OpenAPISchemaGenerator

from api.docs import carts


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, request=None, public=False):
        """Generate a :class:`.Swagger` object with custom tags"""

        swagger = super().get_schema(request, public)
        swagger.tags = [
            {
                "name": "carts",
                "description": carts.CartsDocs.common
            },
        ]

        return swagger
