from fastapi import APIRouter,Depends
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.models import EstimateProfile
from src.schemas.estimate import EstimateInput
from src.services import estimates as service
from src.utils.serialization import rows
router=APIRouter(prefix="/estimates")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(EstimateProfile).order_by(EstimateProfile.created_at.desc())))
@router.post("")
def create(payload:EstimateInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
