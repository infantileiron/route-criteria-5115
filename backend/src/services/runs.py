import uuid,redis
from fastapi import HTTPException
from src.models import DecisionRun,JudgmentMatrix,EstimateProfile,CriteriaSet
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 if not db.get(JudgmentMatrix,payload.judgment_id):raise HTTPException(404,"判断矩阵不存在")
 estimate_id="";samples=0;seed=0
 if payload.estimate_id:
  judgment=db.get(JudgmentMatrix,payload.judgment_id);criteria=db.get(CriteriaSet,judgment.criteria_set_id)
  estimate=db.get(EstimateProfile,payload.estimate_id)
  if not estimate or estimate.dataset_id!=criteria.dataset_id:raise HTTPException(422,"估计区间须属于同一方案集")
  estimate_id=estimate.id;samples=payload.samples;seed=payload.seed
 item=DecisionRun(id=str(uuid.uuid4()),judgment_id=payload.judgment_id,status="queued",result={},error="",estimate_id=estimate_id,samples=samples,seed=seed,created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush("route-criteria:jobs",item.id)
 except redis.RedisError:
  item.status="failed";item.error="后台队列不可用，请重试";db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(DecisionRun,id)
 if not item:raise HTTPException(404,"运行不存在")
 if item.status!="completed":raise HTTPException(409,"计算尚未完成")
 return item
