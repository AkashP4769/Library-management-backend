from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


def configure_middleware(app: FastAPI) -> None:
    """
    Register ASGI middleware. Last added is outermost (runs first on the request path).

    Stack (request): CORS -> request logging -> routes.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )
