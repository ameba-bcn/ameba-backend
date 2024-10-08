from drf_yasg.generators import OpenAPISchemaGenerator

from api.docs import carts, recovery, activate, covers, subscriber, \
    articles, events, subscriptions, user, member_register, members, \
    profile_images


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, request=None, public=False):
        """Generate a :class:`.Swagger` object with custom tags"""

        swagger = super().get_schema(request, public)
        swagger.tags = [
            {
                "name": "users",
                "description": user.UserDocs.common
            },
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
            {
                "name": "member_register",
                "description": member_register.MemberRegisterDocs.common
            },
            {
                "name": "members",
                "description": members.MembersDocs.common
            },
            {
                "name": "profile_images",
                "description": profile_images.ProfileImagesDocs.common
            }
        ]

        return swagger
