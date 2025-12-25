from app.core.database import engine, Base
from app.models import task, user

Base.metadata.create_all(engine)
