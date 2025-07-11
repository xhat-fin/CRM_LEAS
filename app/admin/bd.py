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


# DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
DB_URL = "postgresql+psycopg2://postgres:Totem123@localhost/leasing"
engine = create_engine(DB_URL)
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
            user = session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                return user
            return None
        except Exception as e:
            session.rollback()
            print('Ошибка при чтении пользователя: ', e)
        finally:
            session.close()



# создание клиента
def create_client(client_data):
    with Session() as session:
        try:
            new_client = Client(
                client_name=client_data.get('client_name'),
                unp=client_data['unp'],
                type_client=client_data.get('type_client'),
                egr_phone=client_data.get('egr_phone'),
                registration_date=client_data.get('registration_date'),  # NULL если None
                address=client_data.get('address'),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None
            )

            session.add(new_client)
            session.commit()
            return new_client.id
        except Exception as e:
            session.rollback()
            current_app.logger.error(f'Ошибка при создании клиента: {str(e)}')
            raise
        finally:
            session.close()


# создание сделки
def create_deal(**kwargs):
    with Session() as session:
        required_fields = ['manager_id', 'client_id']
        for item in required_fields:
            if item not in kwargs:
                raise ValueError(f"Обязательное поле '{item}' не указано!")

        try:
            # Преобразуем пустые строки в None для числовых полей
            numeric_fields = [
                'prepayment', 'first_payment', 'interest_rate',
                'effective_rate', 'financing_amount_usd_with_vat',
                'deal_amount_at_conclusion'
            ]

            for field in numeric_fields:
                if field in kwargs and kwargs[field] == '':
                    kwargs[field] = None
                elif field in kwargs and kwargs[field] is not None:
                    try:
                        kwargs[field] = float(kwargs[field])
                    except (ValueError, TypeError):
                        kwargs[field] = None

            # Обработка stop_list_duration
            if 'stop_list_duration' in kwargs and kwargs['stop_list_duration'] == '':
                kwargs['stop_list_duration'] = None
            elif 'stop_list_duration' in kwargs and kwargs['stop_list_duration'] is not None:
                try:
                    kwargs['stop_list_duration'] = timedelta(days=int(kwargs['stop_list_duration']))
                except (ValueError, TypeError):
                    kwargs['stop_list_duration'] = None

            deal = Deal(
                first_contact_date=kwargs.get('first_contact_date'),
                manager_id=kwargs.get('manager_id'),
                client_id=kwargs.get('client_id'),
                car_brand=kwargs.get('car_brand'),
                car_seller=kwargs.get('car_seller'),
                skp_or_bl=kwargs.get('skp_or_bl'),
                shipment_signing=kwargs.get('shipment_signing'),
                prepayment=kwargs.get('prepayment'),
                first_payment=kwargs.get('first_payment'),
                term=kwargs.get('term'),
                dfl_currency=kwargs.get('dfl_currency'),
                interest_rate=kwargs.get('interest_rate'),
                effective_rate=kwargs.get('effective_rate'),
                applied_certificate=kwargs.get('applied_certificate'),
                issued_certificate=kwargs.get('issued_certificate'),
                is_express=kwargs.get('is_express', False),
                is_electric_car=kwargs.get('is_electric_car', False),
                financing_amount_usd_with_vat=kwargs.get('financing_amount_usd_with_vat'),
                planned_shipment_date=kwargs.get('planned_shipment_date'),
                deal_comment=kwargs.get('deal_comment'),
                agent_name=kwargs.get('agent_name'),
                pv_in_sap=kwargs.get('pv_in_sap', False),
                application_datetime=kwargs.get('application_datetime'),
                originals_or_scans=kwargs.get('originals_or_scans'),
                decision_making_body=kwargs.get('decision_making_body'),
                transfer_to_ke_datetime=kwargs.get('transfer_to_ke_datetime'),
                application_status=kwargs.get('application_status'),
                expert_id=kwargs.get('expert_id'),
                deal_amount_at_conclusion=kwargs.get('deal_amount_at_conclusion'),
                deal_currency=kwargs.get('deal_currency'),
                kk_datetime=kwargs.get('kk_datetime'),
                protocol_date=kwargs.get('protocol_date'),
                dfl_signing_date=kwargs.get('dfl_signing_date'),
                car_shipment_date=kwargs.get('car_shipment_date'),
                stop_list_duration=kwargs.get('stop_list_duration'),
                delay_comments=kwargs.get('delay_comments'),
                client_refusal_reason=kwargs.get('client_refusal_reason'),
                creditworthiness=kwargs.get('creditworthiness'),
                description_manager=kwargs.get('description_manager'),
                description_ke=kwargs.get('description_ke'),
            )
            session.add(deal)
            session.commit()
            return deal
        except Exception as e:
            session.rollback()
            print('Ошибка при создании сделки: ', e)
            raise
        finally:
            session.close()



# обновление клиента
def update_client(client_id: int,
                  client_name: Optional[str] = None,
                  unp: Optional[str] = None,
                  egr_phone: Optional[str] = None,
                  registration_date: Optional[date] = None,
                  address: Optional[str] = None,
                  type_client: Optional[str] = None):
    with Session() as session:
        try:
            client = session.query(Client).filter_by(id=client_id).first()

            if not client:
                print(f'Клиент с ID {client_id} не найден')
                return None

            if client_name is not None:
                client.client_name = client_name
            if unp is not None:
                client.unp = unp
            if egr_phone is not None:
                client.egr_phone = egr_phone
            if registration_date is not None:
                client.registration_date = registration_date
            if address is not None:
                client.address = address
            if type_client is not None:
                client.type_client = type_client

            session.commit()
            return client

        except Exception as e:
            session.rollback()
            print(f'Ошибка при обновлении клиента {client_id}: ', e)
            return None

        finally:
            session.close()



# обновление пользователя
def update_users(user_id: int, username: Optional[str] = None, full_name: Optional[str] = None, password: Optional[str] = None, role_id: Optional[int] = None):
    with Session() as session:
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                print(f'Пользователь с ID {user_id} не найден')
                return None

            if username is not None:
                user.username = username

            if full_name is not None:
                user.full_name = full_name

            if password is not None:
                user.password_hash = generate_password_hash(password)

            if role_id is not None:
                user.role_id = role_id

            session.commit()
            return user

        except Exception as e:
            session.rollback()
            print('Ошибка при обновлении пользователя: ', e)
            return None
        finally:
            session.close()



# обновление роли
def update_role(id_role: int, name_role: str):
    with Session() as session:
        try:
            role = session.query(Role).filter_by(id=id_role).first()

            if not role:
                print(f'Роли с ID {id_role} не найдено')
                return None

            role.name = name_role
            session.commit()
            return role

        except Exception as e:
            session.rollback()
            print("Ошибка при обновлении роли: ", e)
            return None
        finally:
            session.close()


# обновление сделки
def update_deal(deal_id: int, **kwargs):
    with Session() as session:
        try:
            # Находим сделку по ID
            deal = session.query(Deal).filter_by(id=deal_id).first()

            if not deal:
                print(f'Сделка с ID {deal_id} не найдена')
                return None

            if 'first_contact_date' in kwargs:
                deal.first_contact_date = kwargs.get('first_contact_date')
            if 'manager_id' in kwargs:
                deal.manager_id = kwargs.get('manager_id')
            if 'client_id' in kwargs:
                deal.client_id = kwargs.get('client_id')
            if 'car_brand' in kwargs:
                deal.car_brand = kwargs.get('car_brand')
            if 'car_seller' in kwargs:
                deal.car_seller = kwargs.get('car_seller')
            if 'skp_or_bl' in kwargs:
                deal.skp_or_bl = kwargs.get('skp_or_bl')
            if 'shipment_signing' in kwargs:
                deal.shipment_signing = kwargs.get('shipment_signing')
            if 'prepayment' in kwargs:
                deal.prepayment = kwargs.get('prepayment')
            if 'first_payment' in kwargs:
                deal.first_payment = kwargs.get('first_payment')
            if 'term' in kwargs:
                deal.term = kwargs.get('term')
            if 'dfl_currency' in kwargs:
                deal.dfl_currency = kwargs.get('dfl_currency')
            if 'interest_rate' in kwargs:
                deal.interest_rate = kwargs.get('interest_rate')
            if 'effective_rate' in kwargs:
                deal.effective_rate = kwargs.get('effective_rate')
            if 'applied_certificate' in kwargs:
                deal.applied_certificate = kwargs.get('applied_certificate')
            if 'issued_certificate' in kwargs:
                deal.issued_certificate = kwargs.get('issued_certificate')
            if 'is_express' in kwargs:
                deal.is_express = kwargs.get('is_express')
            if 'is_electric_car' in kwargs:
                deal.is_electric_car = kwargs.get('is_electric_car')
            if 'financing_amount_usd_with_vat' in kwargs:
                deal.financing_amount_usd_with_vat = kwargs.get('financing_amount_usd_with_vat')
            if 'planned_shipment_date' in kwargs:
                deal.planned_shipment_date = kwargs.get('planned_shipment_date')
            if 'deal_comment' in kwargs:
                deal.deal_comment = kwargs.get('deal_comment')
            if 'agent_name' in kwargs:
                deal.agent_name = kwargs.get('agent_name')
            if 'pv_in_sap' in kwargs:
                deal.pv_in_sap = kwargs.get('pv_in_sap')
            if 'application_datetime' in kwargs:
                deal.application_datetime = kwargs.get('application_datetime')
            if 'originals_or_scans' in kwargs:
                deal.originals_or_scans = kwargs.get('originals_or_scans')
            if 'decision_making_body' in kwargs:
                deal.decision_making_body = kwargs.get('decision_making_body')
            if 'transfer_to_ke_datetime' in kwargs:
                deal.transfer_to_ke_datetime = kwargs.get('transfer_to_ke_datetime')
            if 'application_status' in kwargs:
                deal.application_status = kwargs.get('application_status')
            if 'expert_id' in kwargs:
                deal.expert_id = kwargs.get('expert_id')
            if 'deal_amount_at_conclusion' in kwargs:
                deal.deal_amount_at_conclusion = kwargs.get('deal_amount_at_conclusion')
            if 'deal_currency' in kwargs:
                deal.deal_currency = kwargs.get('deal_currency')
            if 'kk_datetime' in kwargs:
                deal.kk_datetime = kwargs.get('kk_datetime')
            if 'protocol_date' in kwargs:
                deal.protocol_date = kwargs.get('protocol_date')
            if 'dfl_signing_date' in kwargs:
                deal.dfl_signing_date = kwargs.get('dfl_signing_date')
            if 'car_shipment_date' in kwargs:
                deal.car_shipment_date = kwargs.get('car_shipment_date')
            if 'stop_list_duration' in kwargs:
                deal.stop_list_duration = kwargs.get('stop_list_duration')
            if 'delay_comments' in kwargs:
                deal.delay_comments = kwargs.get('delay_comments')
            if 'client_refusal_reason' in kwargs:
                deal.client_refusal_reason = kwargs.get('client_refusal_reason')
            if 'creditworthiness' in kwargs:
                deal.creditworthiness = kwargs.get('creditworthiness')
            if 'description_manager' in kwargs:
                deal.description_manager = kwargs.get('description_manager')
            if 'description_ke' in kwargs:
                deal.description_ke = kwargs.get('description_ke')

            session.commit()
            return deal

        except Exception as e:
            session.rollback()
            print('Ошибка при обновлении сделки: ', e)
            return None
        finally:
            session.close()


# софт удаление роли
def soft_delete_role(role_id: int):
    with Session() as session:
        try:
            role = session.query(Role).filter_by(id=role_id).first()
            if not role:
                print(f'Роль с ID {role_id} не найдена')
                return False

            role.deleted_at = datetime.utcnow()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при soft delete роли {role_id}: ', e)
            return False
        finally:
            session.close()


# софт удаление пользователя
def soft_delete_user(user_id: int):
    with Session() as session:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f'Пользователь с ID {user_id} не найден')
                return False

            user.deleted_at = datetime.utcnow()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при soft delete пользователя {user_id}: ', e)
            return False
        finally:
            session.close()


# софт удаление клиента
def soft_delete_client(client_id: int):
    with Session() as session:
        try:
            client = session.query(Client).filter_by(id=client_id).first()
            if not client:
                print(f'Клиент с ID {client_id} не найден')
                return False

            client.deleted_at = datetime.utcnow()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при soft delete клиента {client_id}: ', e)
            return False
        finally:
            session.close()


# софт удаление сделки
def soft_delete_deal(deal_id: int):
    with Session() as session:
        try:
            deal = session.query(Deal).filter_by(id=deal_id).first()
            if not deal:
                print(f'Сделка с ID {deal_id} не найдена')
                return False

            deal.deleted_at = datetime.utcnow()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при soft delete сделки {deal_id}: ', e)
            return False
        finally:
            session.close()


# хард удаление роли
def hard_delete_role(role_id: int):
    with Session() as session:
        try:
            role = session.query(Role).filter_by(id=role_id).first()
            if not role:
                print(f'Роль с ID {role_id} не найдена')
                return False

            session.delete(role)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при hard delete роли {role_id}: ', e)
            return False
        finally:
            session.close()


# хард удаление пользователя
def hard_delete_user(user_id: int):
    with Session() as session:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f'Пользователь с ID {user_id} не найден')
                return False

            session.delete(user)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при hard delete пользователя {user_id}: ', e)
            return False
        finally:
            session.close()


# хард удаление клиента
def hard_delete_client(client_id: int):
    with Session() as session:
        try:
            client = session.query(Client).filter_by(id=client_id).first()
            if not client:
                print(f'Клиент с ID {client_id} не найден')
                return False

            session.delete(client)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при hard delete клиента {client_id}: ', e)
            return False
        finally:
            session.close()


# хард удаление сделки
def hard_delete_deal(deal_id: int):
    with Session() as session:
        try:
            deal = session.query(Deal).filter_by(id=deal_id).first()
            if not deal:
                print(f'Сделка с ID {deal_id} не найдена')
                return False

            session.delete(deal)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при hard delete сделки {deal_id}: ', e)
            return False
        finally:
            session.close()


# восстановление роли
def restore_role(role_id: int):
    with Session() as session:
        try:
            role = session.query(Role).filter_by(id=role_id).first()
            if not role:
                print(f'Роль с ID {role_id} не найдена')
                return False

            role.deleted_at = None
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при восстановлении роли {role_id}: ', e)
            return False
        finally:
            session.close()


# восстановление сделки
def restore_deal(deal_id: int):
    with Session() as session:
        try:
            deal = session.query(Deal).filter_by(id=deal_id).first()
            if not deal:
                print(f'Сделка с ID {deal_id} не найдена')
                return False

            deal.deleted_at = None
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при восстановлении сделки {deal_id}: ', e)
            return False
        finally:
            session.close()


# восстановление клиента
def restore_client(client_id: int):
    with Session() as session:
        try:
            client = session.query(Client).filter_by(id=client_id).first()
            if not client:
                print(f'Клиент с ID {client_id} не найден')
                return False

            client.deleted_at = None
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при восстановлении клиента {client_id}: ', e)
            return False
        finally:
            session.close()


# восстановление пользователя
def restore_user(user_id: int):
    with Session() as session:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f'Пользователь с ID {user_id} не найден')
                return False

            user.deleted_at = None
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f'Ошибка при восстановлении пользователя {user_id}: ', e)
            return False
        finally:
            session.close()


# список всех пользователей (сотрудников)
def read_users():
    with Session() as session:
        try:
            # Получаем пользователей с отношениями через ORM
            users = session.query(User).options(
                joinedload(User.role),
                selectinload(User.managed_deals),
                selectinload(User.expert_deals)
            ).filter(User.deleted_at.is_(None)).all()


            result = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'created_at': user.created_at.date().isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.date().isoformat() if user.updated_at else None,
                    'role': {
                        'id': user.role.id,
                        'name': user.role.name
                    } if user.role else None
                }
                result.append(user_data)

            return result

        except Exception as e:
            session.rollback()
            print('Ошибка при чтении пользователей: ', e)
            return False
        finally:
            session.close()


# пользователь по id
def read_user_by_id(user_id):
    with Session() as session:
        try:
            user = session.query(User).options(
                joinedload(User.role),
                selectinload(User.managed_deals),
                selectinload(User.expert_deals)
            ).filter(User.deleted_at.is_(None)).filter(User.id == user_id).one_or_none()

            if not user:
                return None

            user_data = {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'created_at': user.created_at.date().isoformat() if user.created_at else None,
                'updated_at': user.updated_at.date().isoformat() if user.updated_at else None,
                'role': {
                    'id': user.role.id,
                    'name': user.role.name
                } if user.role else None
            }

            return user_data

        except Exception as e:
            session.rollback()
            print('Ошибка при чтении пользователя: ', e)
            return False
        finally:
            session.close()


def read_deals(
        manager_id: Optional[int] = None,
        client_id: Optional[int] = None,
        expert_id: Optional[int] = None,
        status: Optional[str] = None,
        is_express: Optional[bool] = None,
        is_electric: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        show_deleted: bool = False
):

    with Session() as session:
        try:
            # Базовый запрос
            query = session.query(Deal)

            # Фильтр по удаленным записям
            if not show_deleted:
                query = query.filter(Deal.deleted_at.is_(None))

            # Применяем фильтры
            if manager_id is not None:
                query = query.filter(Deal.manager_id == manager_id)

            if client_id is not None:
                query = query.filter(Deal.client_id == client_id)

            if expert_id is not None:
                query = query.filter(Deal.expert_id == expert_id)

            if status is not None:
                query = query.filter(Deal.application_status == status)

            if is_express is not None:
                query = query.filter(Deal.is_express == is_express)

            if is_electric is not None:
                query = query.filter(Deal.is_electric_car == is_electric)

            if start_date and end_date:
                # Преобразуем строки в даты
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

                # Добавляем 1 день к конечной дате
                end_date_next_day = end_date_obj + timedelta(days=1)

                # Фильтруем с учетом всего диапазона
                query = query.filter(
                    Deal.created_at >= start_date_obj,
                    Deal.created_at < end_date_next_day
                )
            elif start_date:
                query = query.filter(Deal.created_at >= start_date)
            elif end_date:
                query = query.filter(Deal.created_at <= end_date)


            # Получаем общее количество записей
            total = query.count()

            # Применяем пагинацию
            query = query.limit(per_page).offset((page - 1) * per_page)

            # Загружаем связанные данные
            deals = query.options(
                joinedload(Deal.manager),
                joinedload(Deal.expert),
                joinedload(Deal.client)
            ).all()

            # Форматируем результат
            result = []
            for deal in deals:
                deal_data = {
                    'id': deal.id,
                    'manager': {
                        'id': deal.manager.id if deal.manager else None,
                        'name': deal.manager.full_name if deal.manager else None
                    },
                    'client': {
                        'id': deal.client.id if deal.client else None,
                        'name': deal.client.client_name if deal.client else None
                    },
                    'expert': {
                        'id': deal.expert.id if deal.expert else None,
                        'name': deal.expert.full_name if deal.expert else None
                    },
                    'car_brand': deal.car_brand,
                    'car_seller': deal.car_seller,
                    'skp_or_bl': deal.skp_or_bl,
                    'shipment_signing': deal.shipment_signing,
                    'prepayment': float(deal.prepayment) if deal.prepayment else None,
                    'first_payment': float(deal.first_payment) if deal.first_payment else None,
                    'term': deal.term,
                    'dfl_currency': deal.dfl_currency,
                    'interest_rate': float(deal.interest_rate) if deal.interest_rate else None,
                    'effective_rate': float(deal.effective_rate) if deal.effective_rate else None,
                    'applied_certificate': deal.applied_certificate,
                    'issued_certificate': deal.issued_certificate,
                    'is_express': deal.is_express,
                    'is_electric_car': deal.is_electric_car,
                    'financing_amount': float(
                        deal.financing_amount_usd_with_vat) if deal.financing_amount_usd_with_vat else None,
                    'planned_shipment_date': deal.planned_shipment_date.isoformat() if deal.planned_shipment_date else None,
                    'deal_comment': deal.deal_comment,
                    'deal_transferred': deal.deal_transferred,
                    'agent_name': deal.agent_name,
                    'pv_in_sap': deal.pv_in_sap,
                    'application_datetime': deal.application_datetime.isoformat() if deal.application_datetime else None,
                    'originals_or_scans': deal.originals_or_scans,
                    'decision_making_body': deal.decision_making_body,
                    'transfer_to_ke_datetime': deal.transfer_to_ke_datetime.isoformat() if deal.transfer_to_ke_datetime else None,
                    'status': deal.application_status,
                    'deal_amount_at_conclusion': float(
                        deal.deal_amount_at_conclusion) if deal.deal_amount_at_conclusion else None,
                    'deal_currency': deal.deal_currency,
                    'kk_datetime': deal.kk_datetime.isoformat() if deal.kk_datetime else None,
                    'protocol_date': deal.protocol_date.isoformat() if deal.protocol_date else None,
                    'dfl_signing_date': deal.dfl_signing_date.isoformat() if deal.dfl_signing_date else None,
                    'car_shipment_date': deal.car_shipment_date.isoformat() if deal.car_shipment_date else None,
                    'stop_list_duration': str(deal.stop_list_duration) if deal.stop_list_duration else None,
                    'delay_comments': deal.delay_comments,
                    'client_refusal_reason': deal.client_refusal_reason,
                    'creditworthiness': deal.creditworthiness,
                    'description_manager': deal.description_manager,
                    'description_ke': deal.description_ke,
                    'first_contact_date': deal.first_contact_date.isoformat() if deal.first_contact_date else None,
                    'created_at': deal.created_at.isoformat() if deal.created_at else None,
                    'updated_at': deal.updated_at.isoformat() if deal.updated_at else None,
                    'deleted_at': deal.deleted_at.isoformat() if deal.deleted_at else None
                }
                result.append(deal_data)

            return {
                'data': result,
                'meta': {
                    'total': total,
                    'page': page,
                    'per_page': per_page
                }
            }

        except Exception as e:
            session.rollback()
            print(f'Ошибка при получении списка сделок: {str(e)}')
            return None
        finally:
            session.close()


def read_deal(deal_id):
    with Session() as session:
        try:
            deal = session.query(Deal).options(
                joinedload(Deal.manager),
                joinedload(Deal.expert),
                joinedload(Deal.client)
            ).filter(Deal.id == deal_id).first()
            deal_data = {
                'id': deal.id,
                'manager': {
                    'id': deal.manager.id if deal.manager else None,
                    'name': deal.manager.full_name if deal.manager else None
                },
                'client': {
                    'id': deal.client.id if deal.client else None,
                    'name': deal.client.client_name if deal.client else None
                },
                'expert': {
                    'id': deal.expert.id if deal.expert else None,
                    'name': deal.expert.full_name if deal.expert else None
                },
                'car_brand': deal.car_brand,
                'car_seller': deal.car_seller,
                'skp_or_bl': deal.skp_or_bl,
                'shipment_signing': deal.shipment_signing,
                'prepayment': float(deal.prepayment) if deal.prepayment else None,
                'first_payment': float(deal.first_payment) if deal.first_payment else None,
                'term': deal.term,
                'dfl_currency': deal.dfl_currency,
                'interest_rate': float(deal.interest_rate) if deal.interest_rate else None,
                'effective_rate': float(deal.effective_rate) if deal.effective_rate else None,
                'applied_certificate': deal.applied_certificate,
                'issued_certificate': deal.issued_certificate,
                'is_express': deal.is_express,
                'is_electric_car': deal.is_electric_car,
                'financing_amount': float(
                    deal.financing_amount_usd_with_vat) if deal.financing_amount_usd_with_vat else None,
                'planned_shipment_date': deal.planned_shipment_date.isoformat() if deal.planned_shipment_date else None,
                'deal_comment': deal.deal_comment,
                'deal_transferred': deal.deal_transferred,
                'agent_name': deal.agent_name,
                'pv_in_sap': deal.pv_in_sap,
                'application_datetime': deal.application_datetime.isoformat() if deal.application_datetime else None,
                'originals_or_scans': deal.originals_or_scans,
                'decision_making_body': deal.decision_making_body,
                'transfer_to_ke_datetime': deal.transfer_to_ke_datetime.isoformat() if deal.transfer_to_ke_datetime else None,
                'status': deal.application_status,
                'deal_amount_at_conclusion': float(
                    deal.deal_amount_at_conclusion) if deal.deal_amount_at_conclusion else None,
                'deal_currency': deal.deal_currency,
                'kk_datetime': deal.kk_datetime.isoformat() if deal.kk_datetime else None,
                'protocol_date': deal.protocol_date.isoformat() if deal.protocol_date else None,
                'dfl_signing_date': deal.dfl_signing_date.isoformat() if deal.dfl_signing_date else None,
                'car_shipment_date': deal.car_shipment_date.isoformat() if deal.car_shipment_date else None,
                'stop_list_duration': str(deal.stop_list_duration) if deal.stop_list_duration else None,
                'delay_comments': deal.delay_comments,
                'client_refusal_reason': deal.client_refusal_reason,
                'creditworthiness': deal.creditworthiness,
                'description_manager': deal.description_manager,
                'description_ke': deal.description_ke,
                'first_contact_date': deal.first_contact_date.isoformat() if deal.first_contact_date else None,
                'created_at': deal.created_at.isoformat() if deal.created_at else None,
                'updated_at': deal.updated_at.isoformat() if deal.updated_at else None,
                'deleted_at': deal.deleted_at.isoformat() if deal.deleted_at else None
            }
            return deal_data
        except Exception as e:
            session.rollback()
            print(f'Ошибка при получении сделки: {str(e)}')
            return None
        finally:
            session.close()



def read_clients(
        unp: Optional[str] = None,
        client_name: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        show_deleted: bool = False,
        show_active: bool = True  # Или сделать Optional[bool] = None
) -> Optional[Dict[str, Any]]:

    with Session() as session:
        try:
            query = session.query(Client).filter(Client.deleted_at.is_(None))


            # Применяем фильтры
            if unp:
                query = query.filter(Client.unp.ilike(f"%{unp}%"))
            if client_name:
                query = query.filter(Client.client_name.ilike(f"%{client_name}%"))

            # Получаем общее количество записей
            total = query.count()

            # Применяем пагинацию
            query = query.limit(per_page).offset((page - 1) * per_page)

            # Выполняем запрос
            clients = query.all()

            # Форматируем результат
            data = [{
                "id": client.id,
                "client_name": client.client_name,
                "unp": client.unp,
                "type_client": client.type_client,
                "egr_phone": client.egr_phone,
                "registration_date": client.registration_date.isoformat() if client.registration_date else None,
                "address": client.address,
                "created_at": client.created_at.isoformat() if client.created_at else None,
                "updated_at": client.updated_at.isoformat() if client.updated_at else None,
                "deleted_at": client.deleted_at.isoformat() if client.deleted_at else None,
                "is_deleted": client.deleted_at is not None
            } for client in clients]

            return {
                "data": data,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "has_next": (page * per_page) < total
                }
            }

        except Exception as e:
            session.rollback()
            print(f'Ошибка при получении клиентов: {str(e)}')
            return None
        finally:
            session.close()


def read_client_by_id(id):
    with Session() as session:
        try:
            query = session.query(Client).filter(Client.deleted_at.is_(None)).filter(Client.id == id)
            client = query.first()
            if not client:
                return None
            data = {
                "id": client.id,
                "client_name": client.client_name,
                "unp": client.unp,
                "type_client": client.type_client,
                "egr_phone": client.egr_phone,
                "registration_date": client.registration_date.isoformat() if client.registration_date else None,
                "address": client.address,
                "created_at": client.created_at.isoformat() if client.created_at else None,
                "updated_at": client.updated_at.isoformat() if client.updated_at else None,
                "deleted_at": client.deleted_at.isoformat() if client.deleted_at else None,
                "is_deleted": client.deleted_at is not None
            }
            return data
        except Exception as e:
            session.rollback()
            print(f'Ошибка при получении клиентов: {str(e)}')
            return None
        finally:
            session.close()

print(read_client_by_id(123))