from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.code import router as code_router
from app.api.v1.endpoints.docs import router as docs_router
from app.api.v1.endpoints.experiments import router as experiments_router
from app.api.v1.endpoints.student import router as student_router
from app.api.v1.endpoints.submissions import router as submissions_router
from app.api.v1.endpoints.teacher import router as teacher_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(code_router)
api_v1_router.include_router(docs_router)
api_v1_router.include_router(experiments_router)
api_v1_router.include_router(submissions_router)
api_v1_router.include_router(teacher_router)
api_v1_router.include_router(student_router)
api_v1_router.include_router(admin_router)
