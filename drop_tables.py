from app.core.database import engine, Base
from app.models import task, user

Base.metadata.drop_all(engine)
