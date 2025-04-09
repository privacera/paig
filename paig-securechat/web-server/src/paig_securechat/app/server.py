import traceback
from core.logging_init import set_logging
set_logging()

from typing import List
from fastapi import FastAPI, Request, Depends , status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core import llm_constants
from core import config
from services.AI_applications import AIApplications
from routers import router
from core.middlewares.sqlalchemy_middleware import SQLAlchemyMiddleware
from core.exceptions import CustomException
from vectordb import vector_store_factory
from services.paig_shield import PAIGShield
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from core import constants
from core.utils import set_paig_app_api_key
import webbrowser
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


def init_ui_render(app_: FastAPI) -> None:
    templates_dir = "templates"
    if os.getenv('SECURECHAT_ROOT_DIR'):
        templates_dir = os.path.join(os.getenv('SECURECHAT_ROOT_DIR') + "/templates")
    app_.mount("/static", StaticFiles(directory=os.path.join(templates_dir, "static")))
    app_.mount("/site/", StaticFiles(directory=templates_dir))
    templates = Jinja2Templates(directory=templates_dir)

    @app_.get("/", response_class=HTMLResponse)
    @app_.get("/login", response_class=HTMLResponse)
    @app_.get("/chat", response_class=HTMLResponse)
    @app_.get("/chat/c/{id}", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "success": False, "message": exc.message},
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


def init_llm_factory() -> None:
    llm_constants.AI_application = AIApplications(config.Config)


def init_paig_shield() -> None:
    llm_constants.paig_shield = PAIGShield()
    llm_constants.paig_shield.setup_shield_client()


def init_vector_db() -> None:
    llm_constants.vector_store = vector_store_factory.VectorStoreFactory(config.Config)
    llm_constants.vector_store.create_vectordb_indices()


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
        Middleware(SQLAlchemyMiddleware)
    ]
    return middleware


def create_app() -> FastAPI:
    init_settings()
    set_paig_app_api_key()
    init_paig_shield()
    init_vector_db()
    app_ = FastAPI(
        title="Secure Chat",
        description="Secure Chat Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        middleware=make_middleware(),
    )
    init_llm_factory()
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    if constants.MODE == "standalone":
        init_ui_render(app_=app_)
        try:
            webbrowser.open(f"http://{constants.HOST}:{constants.PORT}")
        except Exception as e:
            logger.error(f"Unable to open browser: {e}")
            logger.info(f"Please open browser and navigate to: http://{constants.HOST}:{constants.PORT}")
    return app_


app = create_app()