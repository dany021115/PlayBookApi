from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class APIVersionView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "name": "PlayBookApi",
            "version": "0.1.0",
            "docs": "/api/docs/",
            "schema": "/api/schema/",
        })
