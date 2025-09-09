from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import (
    create_engine, String, ForeignKey, Date, Numeric,
    Boolean, Text, Interval
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, joinedload, selectinload
from sqlalchemy.types import TIMESTAMP

from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from typing import Optional, Dict, Any, List
import os


load_dotenv()


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"



class Currency(Base):
    __tablename__ = "currency"

    currency_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class TypeClients(Base):
    __tablename__ = "type_clients"

    type_clients: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class StatusDeal(Base):
    __tablename__ = "status_deal"

    status_deal: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Creditworthiness(Base):
    __tablename__ = "creditworthiness"

    creditworthiness: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class TypeDocument(Base):
    __tablename__ = "type_document"

    type_document: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class BodyDecision(Base):
    __tablename__ = "body_decision"

    body_decision: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class TypeDeal(Base):
    __tablename__ = "type_deal"

    type_deal: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class StageDeal(Base):
    __tablename__ = "stage_deal"

    stage_deal: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Team(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    users: Mapped[List["User"]] = relationship(back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"))
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    role: Mapped["Role"] = relationship(back_populates="users")
    team: Mapped[Optional["Team"]] = relationship(back_populates="users")

    # Связи для сделок
    managed_deals: Mapped[List["Deal"]] = relationship(
        back_populates="manager",
        foreign_keys="Deal.manager_id"
    )
    expert_deals: Mapped[List["Deal"]] = relationship(
        back_populates="expert",
        foreign_keys="Deal.expert_id"
    )
    accounter_deals: Mapped[List["Deal"]] = relationship(
        back_populates="accounter",
        foreign_keys="Deal.accounter_id"
    )


    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        onupdate=datetime.now
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
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        onupdate=datetime.now
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.client_name}')>"


class Deal(Base):
    __tablename__ = "deals"

    # Поля из реестра менеджеров
    first_contact_date: Mapped[Optional[date]] = mapped_column(Date)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"))
    car_brand: Mapped[Optional[str]] = mapped_column(String(100))
    car_seller: Mapped[Optional[str]] = mapped_column(String(500))
    type_deal: Mapped[Optional[str]] = mapped_column(String(50)) # вид сделки
    stage_deal: Mapped[Optional[str]] = mapped_column(String(100))
    prepayment: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    first_payment: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    term: Mapped[Optional[str]] = mapped_column(String(50))
    dfl_currency: Mapped[Optional[str]] = mapped_column(String(10)) # вставка из справочника валюты
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
    type_document: Mapped[Optional[str]] = mapped_column(String(50))
    body_decision: Mapped[Optional[str]] = mapped_column(String(100)) # орган принявший решение
    transfer_to_ke_datetime: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    status_deal: Mapped[Optional[str]] = mapped_column(String(100))
    expert_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    deal_amount_at_conclusion: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    deal_currency: Mapped[Optional[str]] = mapped_column(String(10)) # вставка из справочника валюты
    kk_datetime: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    protocol_date: Mapped[Optional[date]] = mapped_column(Date)
    dfl_signing_date: Mapped[Optional[date]] = mapped_column(Date)
    car_shipment_date: Mapped[Optional[date]] = mapped_column(Date)
    stop_list_duration: Mapped[Optional[timedelta]] = mapped_column(Interval)
    stop_list_start: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    delay_comments: Mapped[Optional[str]] = mapped_column(Text) # коммент стоп-листа
    client_refusal_reason: Mapped[Optional[str]] = mapped_column(Text) # почему отказ клиента
    creditworthiness: Mapped[Optional[str]] = mapped_column(String(50)) # кредитоспособность из справочника
    description_manager: Mapped[Optional[str]] = mapped_column(Text)
    description_ke: Mapped[Optional[str]] = mapped_column(Text)
    accounter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        onupdate=datetime.now
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True)
    )


    # Связи
    manager: Mapped["User"] = relationship(foreign_keys=[manager_id], back_populates="managed_deals")
    expert: Mapped["User"] = relationship(foreign_keys=[expert_id], back_populates="expert_deals")
    client: Mapped["Client"] = relationship(back_populates="deals")
    accounter: Mapped["User"] = relationship(foreign_keys=[accounter_id], back_populates="accounter_deals")

    def __repr__(self):
        return f"<Deal(id={self.id}, client_id={self.client_id}, status='{self.status_deal}')>"


DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

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
                type_deal=kwargs.get('type_deal'),
                stage_deal=kwargs.get('stage_deal'),
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
                type_document=kwargs.get('type_document'),
                body_decision=kwargs.get('body_decision'),
                transfer_to_ke_datetime=kwargs.get('transfer_to_ke_datetime'),
                status_deal=kwargs.get('status_deal'),
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
def update_users(user_id: int, username: Optional[str] = None,
                full_name: Optional[str] = None,
                password: Optional[str] = None,
                role_id: Optional[int] = None):
    with Session() as session:
        try:
            user = session.query(User).options(
                joinedload(User.role)
            ).filter_by(id=user_id).first()

            if not user:
                print(f'Пользователь с ID {user_id} не найден')
                return None

            if username is not None:
                # Проверка уникальности username
                existing = session.query(User).filter(
                    User.username == username,
                    User.id != user_id
                ).first()
                if existing:
                    raise ValueError("Пользователь с таким логином уже существует")
                user.username = username

            if full_name is not None:
                user.full_name = full_name

            if password is not None:
                user.password_hash = generate_password_hash(password)

            if role_id is not None:
                # Проверка существования роли
                role = session.query(Role).filter_by(id=role_id).first()
                if not role:
                    raise ValueError("Указанная роль не существует")
                user.role_id = role_id

            session.commit()
            return user

        except Exception as e:
            session.rollback()
            print('Ошибка при обновлении пользователя: ', e)
            raise  # Пробрасываем исключение дальше для обработки в роуте
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
            deal = session.query(Deal).filter_by(id=deal_id).first()
            if not deal:
                print(f'Сделка с ID {deal_id} не найдена')
                return None

            # Обновляем все переданные поля, включая None
            for field, value in kwargs.items():
                if hasattr(deal, field):
                    setattr(deal, field, value)

            session.commit()
            return deal

        except Exception as e:
            session.rollback()
            print(f'Ошибка при обновлении сделки: {str(e)}')
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

            role.deleted_at = datetime.now()
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

            user.deleted_at = datetime.now()
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

            client.deleted_at = datetime.now()
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

            deal.deleted_at = datetime.now()
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
def read_users(show_deleted: bool = False):
    with Session() as session:
        try:
            # Получаем пользователей с отношениями через ORM
            users = session.query(User).options(
                joinedload(User.role),
                selectinload(User.managed_deals),
                selectinload(User.expert_deals)
            ).order_by(User.id.asc())

            if show_deleted:
                users = users.filter(User.deleted_at.isnot(None))  # Только удаленные
            else:
                users = users.filter(User.deleted_at.is_(None))  # Только неудаленные

            users = users.all()

            result = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'created_at': user.created_at.date().isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.date().isoformat() if user.updated_at else None,
                    'deleted_at': user.deleted_at.date().isoformat() if user.deleted_at else None,
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
        client_name: Optional[str] = None,
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
            query = session.query(Deal).order_by(Deal.id.desc())

            # Фильтр по удаленным записям
            if show_deleted:
                query = query.filter(Deal.deleted_at.isnot(None))  # Только удаленные
            else:
                query = query.filter(Deal.deleted_at.is_(None))  # Только неудаленные

            # Применяем фильтры
            if manager_id is not None:
                query = query.filter(Deal.manager_id == manager_id)

            if client_name:
                query = query.join(Deal.client).filter(
                    Client.client_name.ilike(f"%{client_name}%")
                )

            if expert_id is not None:
                query = query.filter(Deal.expert_id == expert_id)

            if status is not None:
                query = query.filter(Deal.status_deal == status)

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
                    'type_deal': deal.type_deal,
                    'stage_deal': deal.stage_deal,
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
                    'type_document': deal.type_document,
                    'body_decision': deal.body_decision,
                    'transfer_to_ke_datetime': deal.transfer_to_ke_datetime.isoformat() if deal.transfer_to_ke_datetime else None,
                    'status_deal': deal.status_deal,
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
                'type_deal': deal.type_deal,
                'stage_deal': deal.stage_deal,
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
                'type_document': deal.type_document,
                'body_decision': deal.body_decision,
                'transfer_to_ke_datetime': deal.transfer_to_ke_datetime.isoformat() if deal.transfer_to_ke_datetime else None,
                'status': deal.status_deal,
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
        show_deleted: bool = False
) -> Optional[Dict[str, Any]]:

    with Session() as session:
        try:

            query = session.query(Client).order_by(Client.created_at.desc())

            if show_deleted:
                query = query.filter(Client.deleted_at.isnot(None))  # Только удаленные
            else:
                query = query.filter(Client.deleted_at.is_(None))  # Только неудаленные

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
            query = session.query(Client).filter(Client.id == id)
            client = query.first()
            if not client:
                return None
            data_client = {
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

            query_deals_client = session.query(Deal).options(
                joinedload(Deal.manager),
                joinedload(Deal.expert),
                joinedload(Deal.client)
            ).filter(
                Deal.deleted_at.is_(None),
                Deal.client_id == id
            ).order_by(Deal.created_at.desc())

            client_deals = query_deals_client.all()
            data_deals = []
            for deal in client_deals:
                data_deals.append({
                    "id": deal.id,
                    "status": deal.status_deal,
                    "created_at": deal.created_at.strftime('%d-%m-%Y %H:%M'),
                    "type_deal": deal.type_deal
                })

            data = {"data_client": data_client, "client_deals": data_deals}

            return data
        except Exception as e:
            session.rollback()
            print(f'Ошибка при получении клиентов: {str(e)}')
            return None
        finally:
            session.close()


def read_deals_assign():
    with Session() as session:
        try:
            deals = session.query(Deal).options(
                joinedload(Deal.manager),
                joinedload(Deal.client)
            ).filter(
                Deal.status_deal == 'На распределении',
                Deal.deleted_at.is_(None)
            ).all()

            deals_assign = []
            for deal in deals:
                deals_assign.append({
                    'id': deal.id,
                    'manager': {
                        'id': deal.manager.id if deal.manager else None,
                        'name': deal.manager.full_name if deal.manager else None
                    },
                    'client': {
                        'id': deal.client.id if deal.client else None,
                        'name': deal.client.client_name if deal.client else None
                    },
                    'car_brand': deal.car_brand,
                    'financing_amount': float(
                        deal.financing_amount_usd_with_vat) if deal.financing_amount_usd_with_vat else None,
                    'created_at': deal.created_at.strftime('%d.%m.%Y %H:%M') if deal.created_at else None
                })

            experts = session.query(User).join(User.role).filter(
                User.deleted_at.is_(None),
                Role.name == 'expert' # Фильтр по названию роли
            ).all()

            return {
                "deals": deals_assign,
                "experts": experts
            }
        except Exception as e:
            print(f"Error in read_deals_assign: {str(e)}")
            return None


def assign_expert_to_deal(deal_id, expert_id):
    with Session() as session:
        try:
            deal = session.query(Deal).get(deal_id)
            if not deal:
                return False

            deal.expert_id = expert_id
            deal.status_deal = 'В работе'  # Обновляем статус
            deal.transfer_to_ke_datetime = datetime.now()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error assigning expert to deal: {str(e)}")
            return False


def get_config():
    with Session() as session:
        try:
            currency = session.query(Currency).all()
            type_clients = session.query(TypeClients).all()
            status_deal = session.query(StatusDeal).all()
            creditworthiness = session.query(Creditworthiness).all()
            type_doc = session.query(TypeDocument).all()
            body_decision = session.query(BodyDecision).all()
            type_deal = session.query(TypeDeal).all()
            stage_deal = session.query(StageDeal).all()
            team = session.query(Team).all()

            data = {
                'currency': currency,
                'type_clients': type_clients,
                'status_deal': status_deal,
                'creditworthiness': creditworthiness,
                'type_doc': type_doc,
                'body_decision': body_decision,
                'type_deal': type_deal,
                'stage_deal': stage_deal,
                'team': team
            }


            return data
        except Exception as e:
            session.rollback()
            print(f"Error get config data: {str(e)}")
            return False

def read_currency():
    with Session() as session:
        try:
            data_currency = session.query(Currency).all()

            currency = []
            for curr in data_currency:
                currency.append(
                    {'id': curr.id,
                     'currency_name': curr.currency_name}
                )

            return currency
        except Exception as e:
            session.rollback()
            print(f"Error get config data: {str(e)}")
            return False


def create_currency(currency_name):
    with Session() as session:
        try:
            new_currency = Currency(currency_name=currency_name)
            session.add(new_currency)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating currency: {str(e)}")
            return False

def update_currency(currency_id, new_currency_name):
    with Session() as session:
        try:
            currency = session.query(Currency).filter_by(id=currency_id).first()
            if currency:
                currency.currency_name = new_currency_name
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating currency: {str(e)}")
            return False

def delete_currency(currency_id):
    with Session() as session:
        try:
            currency = session.query(Currency).filter_by(id=currency_id).first()
            if currency:
                session.delete(currency)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting currency: {str(e)}")
            return False


def read_type_clients():
    with Session() as session:
        try:
            data = session.query(TypeClients).all()
            return [{'id': item.id, 'type_clients': item.type_clients} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading type clients: {str(e)}")
            return False

def create_type_client(type_client):
    with Session() as session:
        try:
            new_item = TypeClients(type_clients=type_client)
            session.add(new_item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating type client: {str(e)}")
            return False

def update_type_client(client_id, new_type):
    with Session() as session:
        try:
            item = session.query(TypeClients).filter_by(id=client_id).first()
            if item:
                item.type_clients = new_type
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating type client: {str(e)}")
            return False

def delete_type_client(client_id):
    with Session() as session:
        try:
            item = session.query(TypeClients).filter_by(id=client_id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting type client: {str(e)}")
            return False

# Чтение всех статусов сделок
def read_status_deals():
    with Session() as session:
        try:
            data = session.query(StatusDeal).all()
            return [{'id': item.id, 'status_deal': item.status_deal} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading status deals: {str(e)}")
            return False

# Создание нового статуса сделки
def create_status_deal(status_name):
    with Session() as session:
        try:
            new_status = StatusDeal(status_deal=status_name)
            session.add(new_status)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating status deal: {str(e)}")
            return False

# Обновление статуса сделки
def update_status_deal(status_id, new_status_name):
    with Session() as session:
        try:
            status = session.query(StatusDeal).filter_by(id=status_id).first()
            if status:
                status.status_deal = new_status_name
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating status deal: {str(e)}")
            return False

# Удаление статуса сделки
def delete_status_deal(status_id):
    with Session() as session:
        try:
            status = session.query(StatusDeal).filter_by(id=status_id).first()
            if status:
                session.delete(status)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting status deal: {str(e)}")
            return False


# Чтение всех записей кредитоспособности
def read_creditworthiness():
    with Session() as session:
        try:
            data = session.query(Creditworthiness).all()
            return [{'id': item.id, 'creditworthiness': item.creditworthiness} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading creditworthiness: {str(e)}")
            return False


# Создание новой записи
def create_creditworthiness(value):
    with Session() as session:
        try:
            if len(value) > 50:
                return False

            new_record = Creditworthiness(creditworthiness=value)
            session.add(new_record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating creditworthiness: {str(e)}")
            return False


# Обновление записи
def update_creditworthiness(record_id, new_value):
    with Session() as session:
        try:
            if len(new_value) > 50:
                return False

            record = session.query(Creditworthiness).filter_by(id=record_id).first()
            if record:
                record.creditworthiness = new_value
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating creditworthiness: {str(e)}")
            return False


# Удаление записи
def delete_creditworthiness(record_id):
    with Session() as session:
        try:
            record = session.query(Creditworthiness).filter_by(id=record_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting creditworthiness: {str(e)}")
            return False


# Чтение всех типов документов
def read_type_documents():
    with Session() as session:
        try:
            data = session.query(TypeDocument).all()
            return [{'id': item.id, 'type_document': item.type_document} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading document types: {str(e)}")
            return False


# Создание нового типа документа
def create_type_document(doc_type):
    with Session() as session:
        try:
            if len(doc_type) > 50:
                return False

            new_doc_type = TypeDocument(type_document=doc_type)
            session.add(new_doc_type)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating document type: {str(e)}")
            return False


# Обновление типа документа
def update_type_document(doc_id, new_type):
    with Session() as session:
        try:
            if len(new_type) > 50:
                return False

            doc_type = session.query(TypeDocument).filter_by(id=doc_id).first()
            if doc_type:
                doc_type.type_document = new_type
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating document type: {str(e)}")
            return False


# Удаление типа документа
def delete_type_document(doc_id):
    with Session() as session:
        try:
            doc_type = session.query(TypeDocument).filter_by(id=doc_id).first()
            if doc_type:
                session.delete(doc_type)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting document type: {str(e)}")
            return False


# Чтение всех органов решений
def read_body_decisions():
    with Session() as session:
        try:
            data = session.query(BodyDecision).all()
            return [{'id': item.id, 'body_decision': item.body_decision} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading body decisions: {str(e)}")
            return False


# Создание нового органа решения
def create_body_decision(body_name):
    with Session() as session:
        try:
            if len(body_name) > 50:
                return False

            new_body = BodyDecision(body_decision=body_name)
            session.add(new_body)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating body decision: {str(e)}")
            return False


# Обновление органа решения
def update_body_decision(body_id, new_name):
    with Session() as session:
        try:
            if len(new_name) > 50:
                return False

            body = session.query(BodyDecision).filter_by(id=body_id).first()
            if body:
                body.body_decision = new_name
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating body decision: {str(e)}")
            return False


# Удаление органа решения
def delete_body_decision(body_id):
    with Session() as session:
        try:
            body = session.query(BodyDecision).filter_by(id=body_id).first()
            if body:
                session.delete(body)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting body decision: {str(e)}")
            return False


# Чтение всех типов сделок
def read_type_deals():
    with Session() as session:
        try:
            data = session.query(TypeDeal).all()
            return [{'id': item.id, 'type_deal': item.type_deal} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading deal types: {str(e)}")
            return False


# Создание нового типа сделки
def create_type_deal(deal_type):
    with Session() as session:
        try:
            if len(deal_type) > 50:
                return False

            new_deal_type = TypeDeal(type_deal=deal_type)
            session.add(new_deal_type)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating deal type: {str(e)}")
            return False


# Обновление типа сделки
def update_type_deal(deal_id, new_type):
    with Session() as session:
        try:
            if len(new_type) > 50:
                return False

            deal_type = session.query(TypeDeal).filter_by(id=deal_id).first()
            if deal_type:
                deal_type.type_deal = new_type
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating deal type: {str(e)}")
            return False


# Удаление типа сделки
def delete_type_deal(deal_id):
    with Session() as session:
        try:
            deal_type = session.query(TypeDeal).filter_by(id=deal_id).first()
            if deal_type:
                session.delete(deal_type)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting deal type: {str(e)}")
            return False


# Чтение всех стадий сделок
def read_stage_deals():
    with Session() as session:
        try:
            data = session.query(StageDeal).all()
            return [{'id': item.id, 'stage_deal': item.stage_deal} for item in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading deal stages: {str(e)}")
            return False


# Создание новой стадии сделки
def create_stage_deal(stage_name):
    with Session() as session:
        try:
            if len(stage_name) > 50:
                return False

            new_stage = StageDeal(stage_deal=stage_name)
            session.add(new_stage)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating deal stage: {str(e)}")
            return False


# Обновление стадии сделки
def update_stage_deal(stage_id, new_name):
    with Session() as session:
        try:
            if len(new_name) > 50:
                return False

            stage = session.query(StageDeal).filter_by(id=stage_id).first()
            if stage:
                stage.stage_deal = new_name
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating deal stage: {str(e)}")
            return False


# Удаление стадии сделки
def delete_stage_deal(stage_id):
    with Session() as session:
        try:
            stage = session.query(StageDeal).filter_by(id=stage_id).first()
            if stage:
                session.delete(stage)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting deal stage: {str(e)}")
            return False


# Чтение всех команд
def read_teams():
    with Session() as session:
        try:
            data = session.query(Team).options(joinedload(Team.users)).all()
            return [{
                'id': team.id,
                'name': team.name,
                'users_count': len(team.users)
            } for team in data]
        except Exception as e:
            session.rollback()
            print(f"Error reading teams: {str(e)}")
            return False


# Создание новой команды
def create_team(team_name):
    with Session() as session:
        try:
            if len(team_name) > 50:
                return False

            new_team = Team(name=team_name)
            session.add(new_team)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating team: {str(e)}")
            return False


# Обновление команды
def update_team(team_id, new_name):
    with Session() as session:
        try:
            if len(new_name) > 50:
                return False

            team = session.query(Team).filter_by(id=team_id).first()
            if team:
                team.name = new_name
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating team: {str(e)}")
            return False


# Удаление команды (с проверкой связанных пользователей)
def delete_team(team_id):
    with Session() as session:
        try:
            team = session.query(Team).options(joinedload(Team.users)).filter_by(id=team_id).first()
            if team:
                if len(team.users) > 0:
                    return None  # Особый статус - есть зависимости
                session.delete(team)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting team: {str(e)}")
            return False