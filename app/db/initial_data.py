import logging

from app.crud.user import user as crud_user
from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    # Tables should be created with Alembic
    db = SessionLocal()

    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin",
            is_admin=True,
        )
        user = crud_user.create(db, obj_in=user_in)
        logger.info("First superuser created")
    else:
        logger.info("First superuser already exists in database")

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")
