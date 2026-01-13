import os
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions, status

from core.resources.upload_client import FileUploadClient
from common.serializers import DeleteMediaSerializer, UploadMediaSerializer
from utils.response import Response



class UploadMediaView(generics.GenericAPIView):
    serializer_class = UploadMediaSerializer
    permission_classes = [permissions.AllowAny]
    upload_client = FileUploadClient
    parser_classes = [MultiPartParser, FormParser] 

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={"user": user})
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        image = serializer.validated_data.get("image")

        cloudinary_folder = f"KND"
        obj = self.upload_client.execute(
            file=image, cloudinary_folder=cloudinary_folder
        )

        if not obj["success"]:
            return Response(**obj)

        return Response(
            success=True,
            message=obj["message"],
            data=obj["data"],
            status_code=status.HTTP_200_OK,
        )


class DeleteMediaView(generics.GenericAPIView):
    serializer_class = DeleteMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    upload_client = FileUploadClient

    def delete(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        public_id = serializer.validated_data.get("public_id")
        obj = self.upload_client.delete_file(public_id)

        if not obj["success"]:
            return Response(**obj)

        return Response(
            success=True,
            message=obj["message"],
            status_code=status.HTTP_200_OK,
        )
