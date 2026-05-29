from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import auth, posts, comments,users

app = FastAPI(
    title="SocialNet API",
    description="RESTful API for a full-stack social networking platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Creates all database tables on startup if they don't already exist."""
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router,     prefix="/auth",  tags=["Auth"])
app.include_router(posts.router,    prefix="/posts", tags=["Posts"])
app.include_router(comments.router, prefix="",       tags=["Comments"])
app.include_router(users.router,    prefix="/users", tags=["Users"])

@app.get("/", tags=["Health"])
def root():
    """Returns 200 when the server is running."""
    return {"status": "ok", "app": "SocialNet API"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SocialNet API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi