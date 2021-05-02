from drf_yasg.generators import OpenAPISchemaGenerator

from api.docs import carts, recovery, activate, covers, subscriber, \
    articles, events, subscriptions


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, request=None, public=False):
        """Generate a :class:`.Swagger` object with custom tags"""

        swagger = super().get_schema(request, public)
        swagger.tags = [
            {
                "name": "carts",
                "description": carts.CartsDocs.common
            },
            {
                "name": "activate",
                "description": activate.ActivateDocs.common
            },
            {
                "name": "recovery",
                "description": recovery.RecoveryDocs.common
            },
            {
                "name": "covers",
                "description": covers.CoversDocs.common
            },
            {
                "name": "subscribe",
                "description": subscriber.SubscriberDocs.common
            },
            {
                "name": "articles",
                "description": articles.ArticlesDocs.common
            },
            {
                "name": "events",
                "description": events.EventsDocs.common
            },
            {
                "name": "subscriptions",
                "description": subscriptions.SubscriptionsDocs.common
            },
        ]

        return swagger
