from fastapi import FastAPI

from src.api import api_router, admin_api_router
from src.exceptions.handlers import exception_handlers


class App:
    """
    A factory class for creating and configuring the main application.

    This class uses a builder pattern to allow for a fluent and declarative
    way of setting up the main application instance.
    """

    def __init__(self):
        self._app_kwargs = {}
        self._routers_to_include = []
        self._handlers_to_register = []

    def title(self, title: str) -> 'App':
        self._app_kwargs['title'] = title
        return self

    def description(self, description: str) -> 'App':
        self._app_kwargs['description'] = description
        return self

    def version(self, version: str) -> 'App':
        self._app_kwargs['version'] = version
        return self

    def routers(self) -> 'App':
        """Includes all the feature routers into the application."""
        self._routers_to_include = [api_router, admin_api_router]
        return self

    def exception_handlers(self) -> 'App':
        """Registers custom exception handlers for the application."""
        self._handlers_to_register = exception_handlers
        return self

    def create(self) -> FastAPI:
        """Returns the configured FastAPI application instance."""
        app = FastAPI(**self._app_kwargs)

        for router in self._routers_to_include:
            app.include_router(router)

        for exc_class, handler in self._handlers_to_register:
            app.add_exception_handler(exc_class, handler)

        return app
