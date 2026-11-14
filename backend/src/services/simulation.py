import hashlib,json,time,random
from src.services.topsis import topsis

VERSION="triangular-monte-carlo-v1"
DISTRIBUTION="每条航段每项指标按（下限,最可能值,上限）独立三角分布抽样"
STREAM_KEY="每个（随机种子,航段编号,指标代码）一条SHA-256派生独立抽样流；样本序号即流内次序"
WEIGHTS_RULE="权重取本次AHP主特征向量并固定；每个样本只重算全体航段的列范数归一与理想点"
DEGENERATE_RULE="零范数、常量或近常量指标、理想点距离和为0的退化样本不丢弃，整条计入不可排名"
COUNT_RULE="独占首名/并列首名/未获首名/不可排名互斥，每条航段合计须等于实际完成样本数"
NOTE="首名次数与占比是本次随机抽样的频率，不是确定性保证，也不是航段必然获胜的概率；不可作为航行安全或调度判定。"

def _stream(seed,alternative_id,code):
 key=f"{seed}|{alternative_id}|{code}".encode("utf-8")
 return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8],"big"))

def basis_checksum(ranges,weights,directions,seed,samples):
 payload={"ranges":sorted(ranges,key=lambda r:r["alternative_id"]),"weights":weights,"directions":directions,"seed":seed,"samples":samples,"version":VERSION}
 return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()

def simulate(weights,codes,directions,alt_ids,alt_names,samples,seed,timeout_seconds=None,estimate_id="",estimate_name="",ranges=None,clock=None):
 ranges=sorted(ranges,key=lambda r:r["alternative_id"]);by_id={row["alternative_id"]:row["values"] for row in ranges}
 codes=list(codes);directions=list(directions);ids=list(alt_ids)
 if set(by_id)!=set(ids):raise ValueError("抽样依据的航段须与方案集完全一致")
 for aid in ids:
  if set(by_id[aid])!=set(codes):raise ValueError("抽样依据须覆盖全部指标："+aid)
 counts={aid:{"exclusive_first":0,"tied_first":0,"not_first":0,"unrankable":0} for aid in ids}
 unavailable=0;reason_counts={};timed_out=False;completed=0
 clock=clock or time.monotonic
 started=clock();deadline=started+timeout_seconds if timeout_seconds is not None else None
 streams={(aid,code):_stream(seed,aid,code) for aid in ids for code in codes}
 for sample_index in range(samples):
  if deadline is not None and clock()>deadline:timed_out=True;break
  values=[[streams[(aid,code)].triangular(by_id[aid][code]["min"],by_id[aid][code]["max"],by_id[aid][code]["mode"]) for code in codes] for aid in ids]
  try:
   result=topsis(values,directions,weights);available=result["available"];ranks=result["ranks"];reason=result["reason"]
  except (ValueError,ZeroDivisionError) as error:
   available=False;ranks=None;reason=str(error)
  completed=sample_index+1
  if not available:
   unavailable+=1;reason_counts[reason]=reason_counts.get(reason,0)+1
   for aid in ids:counts[aid]["unrankable"]+=1
   continue
  tied=sum(1 for r in ranks if r==1)>1
  for i,aid in enumerate(ids):
   if ranks[i] is None:counts[aid]["unrankable"]+=1
   elif ranks[i]==1:counts[aid]["tied_first" if tied else "exclusive_first"]+=1
   else:counts[aid]["not_first"]+=1
 rows_out=[]
 for aid in ids:
  c=counts[aid];total=sum(c.values())
  if total!=completed:raise ValueError("抽样计数合计与实际完成样本数不一致")
  denominator=completed if completed else None
  rows_out.append({"alternative_id":aid,"name":alt_names[aid],**c,"counted_samples":total,
   "exclusive_first_share":c["exclusive_first"]/denominator if denominator else None,
   "tied_first_share":c["tied_first"]/denominator if denominator else None,
   "not_first_share":c["not_first"]/denominator if denominator else None,
   "unrankable_share":c["unrankable"]/denominator if denominator else None})
 weights=list(weights)
 basis={"estimate_id":estimate_id,"estimate_name":estimate_name,"ranges":ranges,"weights":weights,"directions":directions,"seed":seed,
  "requested_samples":samples,"completed_samples":completed,"distribution":DISTRIBUTION,"stream_key":STREAM_KEY,"weights_rule":WEIGHTS_RULE,
  "degenerate_rule":DEGENERATE_RULE,"count_rule":COUNT_RULE,"version":VERSION,"checksum":""}
 basis["checksum"]=basis_checksum(ranges,weights,directions,seed,samples)
 return {"version":VERSION,"estimate_id":estimate_id,"estimate_name":estimate_name,"distribution":DISTRIBUTION,"stream_key":STREAM_KEY,
  "degenerate_rule":DEGENERATE_RULE,"count_rule":COUNT_RULE,"weights":weights,"weights_rule":WEIGHTS_RULE,
  "requested_samples":samples,"completed_samples":completed,"seed":seed,"status":"completed" if completed==samples else "partial",
  "timed_out":timed_out,"timeout_seconds":timeout_seconds,"elapsed_seconds":round(clock()-started,3),
  "unavailable_samples":unavailable,"unavailable_reasons":reason_counts,"alternatives":rows_out,"basis":basis,
  "basis_checksum":basis["checksum"],"note":NOTE}
