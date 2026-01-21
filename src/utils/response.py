from rest_framework.response import Response as DRFResponse


class Response:
    def __new__(
        cls,
        status_code,
        success=None,
        data=None,
        message=None,
        errors=None,
        meta=None,
        **kwargs
    ):
        return DRFResponse(
            {
                "success": success if errors is None else False,
                "message": message or ("Validation error" if errors else None),
                "data": data,
                "errors": errors,
                "meta": meta,
                **kwargs,
            },
            status=status_code,
        )
