import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import EstimateProfile
from src.services.datasets import require
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 dataset=require(db,payload.dataset_id)
 codes={c["code"] for c in dataset.columns};ids={a["alternative_id"] for a in dataset.alternatives}
 if len(payload.ranges)!=len(ids) or {r.alternative_id for r in payload.ranges}!=ids:raise HTTPException(422,"估计区间须覆盖方案集中的全部航段且航段不重复")
 for row in payload.ranges:
  if set(row.values)!=codes:raise HTTPException(422,"每条航段的估计区间须覆盖方案集中的全部指标")
 if db.scalar(select(EstimateProfile).where(EstimateProfile.name==payload.name)):raise HTTPException(409,"估计区间名称已存在")
 item=EstimateProfile(id=str(uuid.uuid4()),name=payload.name,dataset_id=payload.dataset_id,ranges=[r.model_dump() for r in payload.ranges],created_at=now());db.add(item);db.commit();return serialize(item)
