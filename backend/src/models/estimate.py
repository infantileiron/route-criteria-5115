from sqlalchemy import String,JSON,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class EstimateProfile(Base):
 __tablename__="estimate_profiles"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("alternative_datasets.id"))
 ranges:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
