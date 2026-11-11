from fastapi import APIRouter

from apps.api.app.domains.courses.router import router as courses_router
from apps.api.app.domains.documents.router import router as documents_router
from apps.api.app.domains.identity.router import router as identity_router

api_router = APIRouter()
api_router.include_router(identity_router)
api_router.include_router(courses_router)
api_router.include_router(documents_router)
