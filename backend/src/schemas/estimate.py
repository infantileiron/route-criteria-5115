from pydantic import BaseModel,Field,model_validator
import math
class Triple(BaseModel):
 min:float=Field(allow_inf_nan=False)
 mode:float=Field(allow_inf_nan=False)
 max:float=Field(allow_inf_nan=False)
 @model_validator(mode="after")
 def ordered(self):
  if not (self.min<=self.mode<=self.max):raise ValueError("估计区间须满足下限≤最可能值≤上限")
  if any(abs(v)>1e12 for v in (self.min,self.mode,self.max)):raise ValueError("估计值绝对值不得超过10的12次方")
  return self
class RangeRow(BaseModel):
 alternative_id:str=Field(min_length=1,max_length=60)
 values:dict[str,Triple]
class EstimateInput(BaseModel):
 name:str=Field(min_length=2,max_length=160)
 dataset_id:str
 ranges:list[RangeRow]=Field(min_length=1,max_length=1000)
 @model_validator(mode="after")
 def unique(self):
  if len({r.alternative_id for r in self.ranges})!=len(self.ranges):raise ValueError("同一航段只能填写一组估计区间")
  if any(not r.values for r in self.ranges):raise ValueError("每条航段须至少填写一项指标区间")
  return self
