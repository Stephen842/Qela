from rest_framework_simplejwt.authentication import JWTAuthentication

class GraphQLJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
            if user:
                request.user = user
        except:
            pass

        return self.get_response(request)
