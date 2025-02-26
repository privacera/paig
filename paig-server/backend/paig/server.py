import traceback

from api.shield.utils.config_utils import load_shield_configs
from core.logging_init import set_logging

set_logging()

from core.middlewares.usage import register_usage_events
from typing import List
from fastapi import FastAPI, Request, responses, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from core.middlewares.sqlalchemy_middleware import SQLAlchemyMiddleware
from core.middlewares.request_count_middleware import RequestCounterMiddleware
from core.exceptions import CustomException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from core import config, constants
import os
import webbrowser
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def init_ui_render(app_: FastAPI) -> None:
    from core.security.authentication import get_auth_token_user_info
    templates_dir = "templates"
    if os.getenv('PAIG_ROOT_DIR'):
        templates_dir = os.path.join(os.getenv('PAIG_ROOT_DIR') + "/templates")
    app_.mount("/static", StaticFiles(directory=os.path.join(templates_dir, "static")))
    templates = Jinja2Templates(directory=templates_dir)

    @app_.get("/styles/fonts/{filename}", response_class=FileResponse)
    async def get_fonts(request: Request, filename: str):
        file_path = f"{templates_dir}/static/styles/fonts/{filename}"
        return FileResponse(file_path)

    @app_.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        try:
            if await get_auth_token_user_info(request) is not None:
                return templates.TemplateResponse("index.html", {"request": request})
            else:
                return responses.RedirectResponse(url="/login", status_code=303)
        except:
            return responses.RedirectResponse(url="/login", status_code=303)

    @app_.get("/login", response_class=HTMLResponse)
    async def login(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app_.get("/logout")
    async def user_logout(
            request: Request,
    ):
        response = responses.RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("PRIVACERAPAIGSESSION")
        return response


def init_routers(app_: FastAPI) -> None:
    from routers import router
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        content = {"error_code": exc.error_code, "success": False, "message": exc.message}
        if exc.details:
            content["details"] = exc.details
        return JSONResponse(
            status_code=exc.code,
            content=content
        )

    @app_.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        message = "Request validation failed"
        try:
            err = exc.errors()[0]
            message = f"{err['loc'][-1]}: {err['msg']}"
        except:
            pass
        return JSONResponse(content=jsonable_encoder({
            "error_code": 400,
            "success": False,
            "message": message
        }), status_code=status.HTTP_400_BAD_REQUEST)

    @app_.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb_str = traceback.format_exc()
        # Log the exception with the traceback
        logging.error(f"Unhandled exception occurred: {exc}\n{tb_str}")
        return JSONResponse(
            status_code=500,
            content={"error_code": 500, "success": False,
                     "message": "An unexpected error occurred. Please try again later."}
        )

    @app_.exception_handler(StarletteHTTPException)
    async def path_not_found_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(content=jsonable_encoder({
                    "error_code": 404,
                    "success": False,
                    "message": "Path Not Found",
                    "path": request.url.path
                }), status_code=status.HTTP_404_NOT_FOUND)


def init_cache() -> None:
    pass


def init_settings() -> None:
    cnf = config.load_config_file()
    config.Config = cnf


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SQLAlchemyMiddleware),
        Middleware(RequestCounterMiddleware)
    ]
    return middleware


def create_app() -> FastAPI:
    init_settings()
    load_shield_configs()
    app_ = FastAPI(
        title="Paig",
        description="Paig Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        middleware=make_middleware(),
        lifespan=register_usage_events
    )

    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    print(f"Paig is running on http://{constants.HOST}:{constants.PORT}")
    if constants.MODE == "standalone":
        init_ui_render(app_=app_)
        try:
            webbrowser.open(f"http://{constants.HOST}:{constants.PORT}")
        except Exception as e:
            logger.error(f"Unable to open browser: {e}")
            logger.info(f"Please open browser and navigate to: http://{constants.HOST}:{constants.PORT}")

    # Add startup events
    return app_


app = create_app()
