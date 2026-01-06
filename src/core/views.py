import os

from django.http import HttpResponse
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response


def api_ok(request):
    hostname = os.getenv("HOSTNAME", "localhost")
    return HttpResponse(f"<h1>KMDMC ERP Server is running on: {hostname}</h1>")


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()


class HealthCheckView(generics.GenericAPIView):
    serializer_class = HealthCheckSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "Health Check OK.",
                "data": {"status": "Server is running"},
            },
            status=status.HTTP_200_OK,
        )
