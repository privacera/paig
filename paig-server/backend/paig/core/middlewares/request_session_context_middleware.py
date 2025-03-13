from starlette.middleware.base import BaseHTTPMiddleware

from contextvars import ContextVar, Token

session_context_user: ContextVar[dict] = ContextVar("login_user")


def get_user() -> dict:
    """
    Get the user of the current request.

    Returns:
        dict: The user of the current request.
    """
    return session_context_user.get()


def set_user(user: dict):
    """
    Set the user of the current request.
    """
    return session_context_user.set(user)


def reset_user(context: Token):
    """
    Reset the user of the current request.
    """
    session_context_user.reset(context)


class RequestSessionContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Skip the middleware if the request is not for guardrail-service
        if not request.url.path.startswith("/guardrail-service"):
            return await call_next(request)

        from core.security.authentication import get_auth_token_user_info
        token_user_info = await get_auth_token_user_info(request)
        context = set_user(token_user_info)
        try:
            response = await call_next(request)
            return response
        except Exception as exception:
            raise exception
        finally:
            reset_user(context)
