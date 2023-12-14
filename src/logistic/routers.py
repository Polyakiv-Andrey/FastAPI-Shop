from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db
from src.logistic.models import NovaPosta
from src.utils import pagination_dependency, get_list_objects

logistic_router = APIRouter(prefix="/logistic", tags=["Logistic"])


@logistic_router.get("/list_novaposhta/")
async def get_list_novaposhta(
        q: str = None,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        pagination: dict = Depends(pagination_dependency)
):
    query = {"description": q, "is_active": True} if q else {"is_active": True}
    list_warehouses = await get_list_objects(session, pagination, NovaPosta, query)
    return list_warehouses

