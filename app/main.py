from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import get_logger, setup_logging


from app import models  # noqa: F401

from app.routers import auth, categories, comments, likes, logs, posts, users

setup_logging()
logger = get_logger(__name__)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы БД проверены / созданы.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "REST API для блог-платформы. Поддерживает аутентификацию через JWT, "
            "ролевую модель (Reader / Author / Moderator), CRUD для статей, "
            "комментариев, категорий и лайков."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.warning("Validation error on %s: %s", request.url, exc.errors())
        # Pydantic v2 кладёт в поле 'ctx' исходный объект исключения (например,
        # ValueError из кастомного field_validator), который не сериализуется
        # в JSON напрямую. Оставляем только безопасные для сериализации поля.
        safe_errors = [
            {
                "type": err.get("type"),
                "loc": err.get("loc"),
                "msg": err.get("msg"),
                "input": err.get("input"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": safe_errors},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Необработанная ошибка на %s: %s", request.url, exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Внутренняя ошибка сервера"},
        )

    # ---------------------------------------------------------------------------
    # Роутеры
    # ---------------------------------------------------------------------------
    api_prefix = "/api"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(categories.router, prefix=api_prefix)
    app.include_router(posts.router, prefix=api_prefix)
    app.include_router(comments.router, prefix=api_prefix)
    app.include_router(likes.router, prefix=api_prefix)
    app.include_router(logs.router, prefix=api_prefix)

    # ---------------------------------------------------------------------------
    # Старт приложения: создание таблиц БД
    # ---------------------------------------------------------------------------
    @app.on_event("startup")
    def on_startup():
        create_tables()
        logger.info("Приложение '%s' запущено.", settings.APP_NAME)

    @app.get("/", tags=["Состояние сервиса"], summary="Проверка работоспособности")
    def health():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
