"""
User creation before the first start of the application
"""
#
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from auth.models import User
# from passlib.context import CryptContext
#
# from settings.config import DATABASE_URL
# from services.logger import Logger
#
# logger = Logger(__name__).get_logger()
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # Настройка подключения к базе данных
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# def create_superuser():
#     db = SessionLocal()
#     username = os.getenv("SUPERUSER_USERNAME", "admin")
#     email = os.getenv("SUPERUSER_EMAIL", "admin@admin.com")
#     password = os.getenv("SUPERUSER_PASSWORD", "admin")
#
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         hashed_password = pwd_context.hash(password)
#         new_user = User(username=username, email=email, password=hashed_password, is_superuser=True)
#         db.add(new_user)
#         db.commit()
#         print("Superuser created")
#     else:
#         print("Superuser already exists")
#     db.close()
#
#
# if __name__ == "__main__":
#     create_superuser()
