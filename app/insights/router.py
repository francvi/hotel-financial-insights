from fastapi import APIRouter
from fastapi.responses import JSONResponse

from insights.db import clear_rows
from insights.service import load as load_insights
from suggestions.db import clear as clear_suggestions

router = APIRouter()


@router.get("/api/insights")
async def get_insights() -> JSONResponse:
    return JSONResponse(load_insights())


@router.post("/api/insights/refresh")
async def refresh_insights() -> JSONResponse:
    clear_rows()
    clear_suggestions()
    return JSONResponse(load_insights())
