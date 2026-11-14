import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,ChoiceReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell
SIM_FIELDS=["exclusive_first","tied_first","not_first","unrankable","exclusive_first_share","tied_first_share","not_first_share","unrankable_share"]
def create(db,payload,user):
 run=require_completed(db,payload.run_id)
 review=db.scalar(select(ChoiceReview).where(ChoiceReview.run_id==payload.run_id).order_by(ChoiceReview.created_at.desc()))
 if not review or review.decision!="accepted":raise HTTPException(409,"最新复核须为接受后才能归档")
 if db.scalar(select(Report).where(Report.run_id==payload.run_id)):raise HTTPException(409,"本次运行已归档")
 basis=run.result.get("simulation",{}).get("basis",{})
 item=Report(id=str(uuid.uuid4()),published_by=user["email"],created_at=now(),basis=basis,**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 result=require_completed(db,report.run_id).result;simulation=result.get("simulation")
 buf=io.StringIO();fields=["alternative_id","name","rank","score","d_plus","d_minus","min_rank","max_rank","cr","ranking_available","reason"]
 if simulation:fields+=SIM_FIELDS+["seed","requested_samples","completed_samples","timed_out","simulation_status","basis_checksum","estimate_name"]
 writer=csv.DictWriter(buf,fields);writer.writeheader()
 by_id={row["alternative_id"]:row for row in simulation["alternatives"]} if simulation else {}
 basis=(report.basis or simulation.get("basis",{})) if simulation else {}
 for a in result["alternatives"]:
  row={k:safe_cell(a[k]) for k in fields[:8]}
  row.update({"cr":result["ahp"]["cr"],"ranking_available":result["topsis"]["available"],"reason":result["topsis"]["reason"]})
  if simulation:
   sampled=by_id[a["alternative_id"]]
   row.update({k:safe_cell(sampled[k]) for k in SIM_FIELDS})
   row.update({"seed":simulation["seed"],"requested_samples":simulation["requested_samples"],"completed_samples":simulation["completed_samples"],"timed_out":simulation["timed_out"],"simulation_status":simulation["status"],"basis_checksum":basis.get("checksum",simulation["basis_checksum"]),"estimate_name":simulation["estimate_name"]})
  writer.writerow(row)
 return "﻿"+buf.getvalue()
