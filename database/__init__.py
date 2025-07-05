from sqlalchemy import create_engine
from .models import Base

def init_db():
    engine = create_engine('sqlite:///murphylogistik.db')
    Base.metadata.create_all(bind=engine)
    return engine