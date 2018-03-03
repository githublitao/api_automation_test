from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from api_test.serializers import TokenSerializer
from api_test.common.api_response import JsonResponse
from api_test.common import GlobalStatusCode


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # token, created = Token.objects.get_or_create(user=user)
        data = TokenSerializer(Token.objects.get(user=user)).data
        return JsonResponse(data=data, code_msg=GlobalStatusCode.success())


obtain_auth_token = ObtainAuthToken.as_view()