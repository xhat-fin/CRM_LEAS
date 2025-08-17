import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import (
    create_engine, String, ForeignKey, Date, Numeric,
    Boolean, Text, Interval, or_
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, joinedload, selectinload
from sqlalchemy.types import TIMESTAMP

from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from typing import Optional, Dict, Any, List
from app.admin.bd import Role, User


load_dotenv()



DB_URL = "postgresql+psycopg2://postgres:Totem123@localhost/leasing"

engine = create_engine((DB_URL), echo=True)
Session = sessionmaker(bind=engine)



# создание роли
def create_role(name_role):
    with Session() as session:
        try:
            role = Role(name=name_role)
            session.add(role)
            session.commit()
        except Exception as e:
            session.rollback()
            print("Ошибка при создании роли: ", e)
        finally:
            session.close()



# создание пользователя
def create_users(username, full_name, password):
    with Session() as session:
        try:
            password_hash = generate_password_hash(password)
            user = User(username=username, full_name=full_name, password_hash=password_hash)
            session.add(user)
            session.commit()
        except Exception as e:
            session.rollback()
            print('Ошибка при создании пользователя: ', e)
        finally:
            session.close()


def user_exists(username):
    with Session() as session:
        return session.query(User).filter_by(username=username).first() is not None


def login_user(username, password):
    with Session() as session:
        try:
            user = session.query(User).options(joinedload(User.role)
            ).filter(User.deleted_at.is_(None)).filter(User.username == username).one_or_none()
            if user and check_password_hash(user.password_hash, password):
                return user
            return None
        except Exception as e:
            session.rollback()
            print('Ошибка при чтении пользователя: ', e)
        finally:
            session.close()

