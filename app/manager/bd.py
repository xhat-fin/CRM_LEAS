from datetime import datetime, date, timedelta
from sqlalchemy import (
    create_engine
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker, joinedload

from dotenv import load_dotenv

from typing import Optional, Dict, Any
from CRM_LEAS.app.admin.bd import Client, Deal

load_dotenv()


DB_URL = "postgresql+psycopg2://postgres:Totem123@localhost/leasing"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

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