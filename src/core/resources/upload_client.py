import os
from datetime import datetime

import cloudinary
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.uploader import destroy, upload


class FileUploadClient:
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    MAX_FILE_SIZE_BYTES = {
        "image": 2 * 1024 * 1024,  # 2 MB
        "pdf": 5 * 1024 * 1024,  # 5 MB
        "csv": 1 * 1024 * 1024,  # 1 MB
        "default": 2 * 1024 * 1024,  # 2 MB for anything else
    }

    RESOURCE_TYPE_MAP = {
        "jpg": "image",
        "jpeg": "image",
        "png": "image",
        "gif": "image",
        "pdf": "raw",
        "csv": "raw",
    }

    @classmethod
    def initialize_cloudinary(cls):
        cloudinary.config(
            cloud_name=cls.CLOUDINARY_CLOUD_NAME,
            api_key=cls.CLOUDINARY_API_KEY,
            api_secret=cls.CLOUDINARY_API_SECRET,
        )

    @classmethod
    def _get_extension(cls, uploaded_file):
        return uploaded_file.name.rsplit(".", 1)[-1].lower()

    @classmethod
    def _get_resource_type(cls, ext):
        return cls.RESOURCE_TYPE_MAP.get(ext, "raw")

    @classmethod
    def is_allowed_format(cls, uploaded_file):
        ext = cls._get_extension(uploaded_file)
        return ext in cls.RESOURCE_TYPE_MAP

    @classmethod
    def is_valid_size(cls, uploaded_file):
        ext = cls._get_extension(uploaded_file)
        limit = cls.MAX_FILE_SIZE_BYTES.get(ext, cls.MAX_FILE_SIZE_BYTES["default"])
        return uploaded_file.size <= limit

    @classmethod
    def execute(cls, file, cloudinary_folder="MYBALANCE"):
        ext = cls._get_extension(file)
        if not cls.is_allowed_format(file):
            return {
                "message": f"Invalid file format. Allowed: {', '.join(cls.RESOURCE_TYPE_MAP.keys())}",
                "success": False,
                "status_code": 400,
            }

        if not cls.is_valid_size(file):
            return {
                "message": f"{ext.upper()} size must be {cls.MAX_FILE_SIZE_BYTES.get(ext)//(1024*1024)}MB or less",
                "success": False,
                "status_code": 400,
            }

        cls.initialize_cloudinary()
        public_id = file.name.rsplit(".", 1)[0].replace(" ", "_")
        resource_type = cls._get_resource_type(ext)

        try:
            result = upload(
                file,
                public_id=public_id,
                folder=cloudinary_folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=False,  # disable Cloudinary’s random suffix
                overwrite=True,  # We will allow replacing an existing asset
            )
            return {
                "message": "Upload Successful",
                "success": True,
                "status_code": 200,
                "data": {
                    "url": result.get("secure_url") or result.get("url"),
                    "public_id": result["public_id"],
                    "resource_type": resource_type,
                },
            }
        except CloudinaryError as e:
            return {
                "message": f"Cloudinary Error: {e}",
                "success": False,
                "status_code": 500,
            }
        except Exception as e:
            return {
                "message": f"Error: {e}",
                "success": False,
                "status_code": 500,
            }

    @classmethod
    def delete_file(cls, public_id):
        cls.initialize_cloudinary()
        try:
            result = destroy(public_id)
            if result["result"] == "ok":
                return {
                    "message": "File deleted successfully",
                    "success": True,
                    "status_code": 200,
                }
            elif result["result"] == "not found":
                return {
                    "message": "File does not exist",
                    "success": True,
                    "status_code": 200,
                }
            else:
                return {
                    "message": f"Error deleting file: {result['result']}",
                    "success": False,
                    "status_code": 400,
                }
        except CloudinaryError as e:
            return {
                "message": f"Cloudinary Error: {str(e)}",
                "success": False,
                "status_code": 400,
            }
        except Exception as e:
            return {
                "message": f"Error: {str(e)}",
                "success": False,
                "status_code": 400,
            }
