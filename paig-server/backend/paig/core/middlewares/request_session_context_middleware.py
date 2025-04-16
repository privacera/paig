from starlette.middleware.base import BaseHTTPMiddleware

from contextvars import ContextVar, Token

session_context: ContextVar[dict] = ContextVar("login_user", default={})


def get_context_value(key: str):
    """
    Get a specific value from the context.
    """
    return session_context.get().get(key)


def set_context_value(key: str, value: any):
    """
    Set a specific value in the context.
    """
    context = session_context.get().copy()  # Avoid modifying the default dict
    context[key] = value
    return session_context.set(context)


def reset_context(token: Token):
    """
    Reset the session context to a previous state.
    """
    session_context.reset(token)


def get_user():
    return get_context_value("user")


def set_user(user: dict):
    if user:
        return set_context_value("user", user)


def get_tenant_id():
    return get_context_value("tenant_id") or '1'


def set_tenant_id(tenant_id: str):
    return set_context_value("tenant_id", tenant_id)


def get_user_role():
    return get_context_value("user_role")


def set_user_role(user_role: str):
    if user_role:
        return set_context_value("user_role", user_role)


def get_email():
    return get_context_value("email")


def set_email(email: str):
    if email:
        return set_context_value("email", email)


class RequestSessionContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Skip the middleware if the request is not for guardrail-service
        if not request.url.path.startswith("/guardrail-service"):
            return await call_next(request)

        from core.security.authentication import get_auth_token_user_info
        token_user_info = await get_auth_token_user_info(request)
        context = set_user(token_user_info)

        tenant_id = request.headers.get('x-tenant-id')
        if tenant_id:
            set_tenant_id(tenant_id)

        try:
            response = await call_next(request)
            return response
        except Exception as exception:
            raise exception
        finally:
            reset_context(context)
