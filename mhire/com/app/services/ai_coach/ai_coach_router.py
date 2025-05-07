from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from openai import OpenAIError

from mhire.com.config.config import Config
from mhire.com.app.services.ai_coach.ai_coach import AICoach
from mhire.com.app.responses.network_responses import NetworkResponse

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])
config = Config()
ai_coach = AICoach(config)
network_response = NetworkResponse()

@router.post("/chat", response_model=Dict[str, Any])
async def chat(message: str = Body(..., embed=True)) -> Dict[str, Any]:
    """
    Process a chat message with NetworkResponse handling
    """
    try:
        response = await ai_coach.chat(message)
        return network_response.success_response(
            http_code=NetworkResponse.HttpStatus.SUCCESS,
            message="Chat response generated successfully",
            data=response
        )

    except HTTPException as http_error:
        if http_error.status_code == 400:
            return network_response.error_response(
                http_code=NetworkResponse.HttpStatus.BAD_REQUEST,
                error_code=NetworkResponse.ErrorCodes.BadRequest.INVALID_INPUT,
                error_type="validation_error",
                message=http_error.detail
            )
        return network_response.error_response(
            http_code=NetworkResponse.HttpStatus.NOT_FOUND,
            error_code=NetworkResponse.ErrorCodes.NotFound.API_KEY_NOT_FOUND,
            error_type="configuration_error",
            message=http_error.detail
        )

    except OpenAIError as openai_error:
        return network_response.error_response(
            http_code=NetworkResponse.HttpStatus.INTERNAL_SERVER_ERROR,
            error_code=NetworkResponse.ErrorCodes.InternalServerError.OPENAI_API_ERROR,
            error_type="openai_error",
            message=str(openai_error)
        )

    except ConnectionError as conn_error:
        return network_response.error_response(
            http_code=NetworkResponse.HttpStatus.INTERNAL_SERVER_ERROR,
            error_code=NetworkResponse.ErrorCodes.InternalServerError.EXTERNAL_API_ERROR,
            error_type="connection_error",
            message=str(conn_error)
        )

    except Exception as e:
        return network_response.error_response(
            http_code=NetworkResponse.HttpStatus.INTERNAL_SERVER_ERROR,
            error_code=NetworkResponse.ErrorCodes.InternalServerError.UNKNOWN_ERROR,
            error_type="internal_error",
            message=str(e)
        )
