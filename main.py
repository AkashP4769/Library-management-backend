from fastapi import FastAPI
import uvicorn
import logging

from middleware import configure_middleware
from auth.router import router as auth_router
from config import setting
from exceptions.handler import register_exception_handlers
from book.router import router as book_router
from shelf.router import router as shelf_router
from book_copy.router import router as book_copy_router
from review.router import router as review_router
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = FastAPI(
    title="Library Management App",
    description="A simple library management application",
    version="1.0.0",
)

configure_middleware(app)
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(shelf_router)
app.include_router(book_copy_router)
app.include_router(review_router)

@app.get("/health", tags=["health"], status_code=200)
def health():
    return {
        "message": f"App is healthy. Environment: {setting.app_env}",
        "status": "healthy",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=True)