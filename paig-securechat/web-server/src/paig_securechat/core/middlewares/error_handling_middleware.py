import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.exceptions import UnauthorizedException, CustomException
from paig_client.exception import AccessControlException

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except UnauthorizedException as e:
            logger.warning(f"[Unauthorized Access] Path: {request.url.path}, Error: {str(e)}", exc_info=False)
            return JSONResponse(
                content={"error": "Unauthorized access."},
                status_code=401
            )

        except AccessControlException as e:
            logger.error(f"[Access Control Error] Path: {request.url.path}, Error: {str(e)}", exc_info=False)
            return JSONResponse(
                content={"error": "Access control violation."},
                status_code=403
            )

        except CustomException as e:
            logger.error(f"[Custom Exception] Path: {request.url.path}, Error: {str(e)}", exc_info=False)
            return JSONResponse(
                content={"error": "An unexpected error occurred. Please try again later."},
                status_code=e.code
            )

        except Exception as e:
            # Log exception without stack trace
            logger.error(f"[Unhandled Exception] Path: {request.url.path}, Error: {type(e).__name__}: {str(e)}", exc_info=False)
            
            return JSONResponse(
                content={"error": "An unexpected error occurred. Please try again later."},
                status_code=500
            )
