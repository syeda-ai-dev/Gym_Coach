from typing import Any, Dict, Optional, Union


class NetworkResponse:
    class HttpStatus:
        SUCCESS = 200
        BAD_REQUEST = 400
        FORBIDDEN = 403
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500

    class ErrorCodes:
        class BadRequest:
            MISSING_REQUIRED_FIELD = 400001
            INVALID_FORMAT = 400002
            VALIDATION_ERROR = 400003
            INVALID_INPUT = 400004
            MESSAGE_TOO_LONG = 400005

        class Forbidden:
            ACCESS_DENIED = 403001
            INSUFFICIENT_PERMISSIONS = 403002

        class NotFound:
            MODEL_NOT_FOUND = 404001
            API_KEY_NOT_FOUND = 404002
            ENDPOINT_NOT_FOUND = 404003

        class InternalServerError:
            SERVICE_UNAVAILABLE = 500001
            DATABASE_ERROR = 500002
            EXTERNAL_API_ERROR = 500003
            MEMORY_ERROR = 500004
            INITIALIZATION_ERROR = 500005
            PROCESSING_ERROR = 500006
            UNKNOWN_ERROR = 500007

    def success_response(
        self,
        http_code: int,
        message: str = "Success",
        data: Optional[Union[Dict[str, Any], Any]] = None,
        ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = {
            "status": "success",
            "code": http_code,
            "data": {"message": message},
        }

        if ref is not None:
            response["data"]["ref"] = ref

        if data is not None:
            if isinstance(data, dict):
                # Merge data without overwriting message
                for key, value in data.items():
                    if key != "message":
                        response["data"][key] = value
            else:
                response["data"]["value"] = data

        return response

    def error_response(
        self,
        http_code: int,
        error_code: int,
        error_type: str,
        message: str,
        ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = {
            "status": "error",
            "code": http_code,
            "error": {
                "code": error_code,
                "type": error_type,
                "message": message,
            },
        }

        if ref is not None:
            response["error"]["ref"] = ref

        return response
