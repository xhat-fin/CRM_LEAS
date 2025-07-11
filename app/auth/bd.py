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



load_dotenv()



class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(back_populates="users")

    # Связи для сделок
    managed_deals: Mapped[List["Deal"]] = relationship(
        back_populates="manager",
        foreign_keys="Deal.manager_id"
    )
    expert_deals: Mapped[List["Deal"]] = relationship(
        back_populates="expert",
        foreign_keys="Deal.expert_id"
    )



    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Client(Base):
    __tablename__ = "clients"

    client_name: Mapped[Optional[str]] = mapped_column(String(500))
    unp: Mapped[Optional[str]] = mapped_column(String(20))
    type_client: Mapped[Optional[str]] = mapped_column(String(20))
    egr_phone: Mapped[Optional[str]] = mapped_column(String(500))
    registration_date: Mapped[Optional[date]] = mapped_column(Date)
    address: Mapped[Optional[str]] = mapped_column(Text)


    deals: Mapped[List["Deal"]] = relationship(back_populates="client")

    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.client_name}')>"


class Deal(Base):
    __tablename__ = "deals"

    # Основные поля
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    # Поля из реестра менеджеров
    first_contact_date: Mapped[Optional[date]] = mapped_column(Date)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"))
    car_brand: Mapped[Optional[str]] = mapped_column(String(100))
    car_seller: Mapped[Optional[str]] = mapped_column(String(500))
    skp_or_bl: Mapped[Optional[str]] = mapped_column(String(50))
    shipment_signing: Mapped[Optional[str]] = mapped_column(String(100))
    prepayment: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    first_payment: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    term: Mapped[Optional[str]] = mapped_column(String(50))
    dfl_currency: Mapped[Optional[str]] = mapped_column(String(10))
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    effective_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    applied_certificate: Mapped[Optional[str]] = mapped_column(String(200))
    issued_certificate: Mapped[Optional[str]] = mapped_column(String(200))
    is_express: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_electric_car: Mapped[Optional[bool]] = mapped_column(Boolean)
    financing_amount_usd_with_vat: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    planned_shipment_date: Mapped[Optional[date]] = mapped_column(Date)
    deal_comment: Mapped[Optional[str]] = mapped_column(Text)
    deal_transferred: Mapped[Optional[str]] = mapped_column(String(200))
    agent_name: Mapped[Optional[str]] = mapped_column(String(200))
    pv_in_sap: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Поля из реестра кредитных экспертов
    application_datetime: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    originals_or_scans: Mapped[Optional[str]] = mapped_column(String(50))
    decision_making_body: Mapped[Optional[str]] = mapped_column(String(100))
    transfer_to_ke_datetime: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    application_status: Mapped[Optional[str]] = mapped_column(String(100))
    expert_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    deal_amount_at_conclusion: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    deal_currency: Mapped[Optional[str]] = mapped_column(String(10))
    kk_datetime: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    protocol_date: Mapped[Optional[date]] = mapped_column(Date)
    dfl_signing_date: Mapped[Optional[date]] = mapped_column(Date)
    car_shipment_date: Mapped[Optional[date]] = mapped_column(Date)
    stop_list_duration: Mapped[Optional[timedelta]] = mapped_column(Interval)
    delay_comments: Mapped[Optional[str]] = mapped_column(Text)
    client_refusal_reason: Mapped[Optional[str]] = mapped_column(Text)
    creditworthiness: Mapped[Optional[str]] = mapped_column(String(50))
    description_manager: Mapped[Optional[str]] = mapped_column(Text)
    description_ke: Mapped[Optional[str]] = mapped_column(Text)

    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True)
    )


    # Связи
    manager: Mapped["User"] = relationship(foreign_keys=[manager_id])
    expert: Mapped["User"] = relationship(foreign_keys=[expert_id])
    client: Mapped["Client"] = relationship(back_populates="deals")

    def __repr__(self):
        return f"<Deal(id={self.id}, client_id={self.client_id}, status='{self.application_status}')>"


DB_URL = "postgresql+psycopg2://postgres:Totem123@localhost/leasing"

engine = create_engine((DB_URL), echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)



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
def create_users(username, full_name, password, role_id):
    with Session() as session:
        try:
            password_hash = generate_password_hash(password)
            user = User(username=username, full_name=full_name, password_hash=password_hash, role_id=role_id)
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

