from pydantic import BaseModel,Field
class RunInput(BaseModel):
 judgment_id:str
 estimate_id:str|None=None
 samples:int=Field(default=500,ge=1,le=10000)
 seed:int=Field(default=20261114,ge=0,le=2147483647)
