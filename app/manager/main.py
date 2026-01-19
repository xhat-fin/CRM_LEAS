from functools import wraps

from flask import jsonify, render_template, request, flash, redirect, url_for, Blueprint
from flask import session as user_session
from dotenv import load_dotenv
from CRM_LEAS.app.manager import bd
from CRM_LEAS.app.admin.bd import User, Role
from CRM_LEAS.app.admin.bd import (read_status_deals, read_type_deals, read_currency,
                          read_body_decisions, read_type_documents,
                          read_creditworthiness, read_stage_deals,
                          read_type_clients)


from datetime import datetime
from decimal import Decimal, InvalidOperation

manager_bp = Blueprint('manager', __name__, template_folder='templates')

load_dotenv()


@manager_bp.before_request
def before_request():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'user_id' not in user_session:
        return redirect(url_for('auth.login'))


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in user_session or user_session['role'] != 'manager':
            return jsonify({
                "error": f"access denied {user_session['role']}"
            }), 403
        return f(*args, **kwargs)
    return decorated_function



@manager_bp.route('/', methods=['GET'])
def index():
    return render_template('manager/index.html')


# список всех сделок (фильтрация и пагинация)
@manager_bp.route('/deals/', methods=['GET'])
@manager_required
def get_deals():
    try:
        # Получаем параметры из запроса
        args = request.args.to_dict()
        page = args.pop('page', 1)
        per_page = args.pop('per_page', 20)

        # Получаем данные из БД
        deals_data = bd.read_deals(
            page=int(page),
            per_page=int(per_page),
            **args
        )

        if deals_data is None:
            flash('Ошибка при загрузке списка сделок', 'danger')
            return redirect(url_for('manager.index'))

        # Получаем данные для фильтров
        with bd.Session() as session:
            experts = session.query(User).join(User.role).filter(
                User.deleted_at.is_(None),
                Role.name == 'expert'  # Фильтр по названию роли
            ).all()
            managers = session.query(User).join(User.role).filter(
                User.deleted_at.is_(None),
                Role.name == 'manager'  # Фильтр по названию роли
            ).all()


            statuses = read_status_deals()
            type_deals = read_type_deals()

        # Подготовка контекста для шаблона
        context = {
            'deals': deals_data['data'],
            'meta': deals_data['meta'],
            'managers': managers,
            'statuses': statuses,
            'experts': experts,
            'type_deals': type_deals,
            'current_filters': request.args.to_dict()
        }

        return render_template('manager/deals/list.html', **context)

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        print(f"Error in get_deals: {str(e)}")
        return redirect(url_for('manager.index'))


# конкретная сделка по айди
@manager_bp.route('/deals/<int:deal_id>/', methods=['GET'])
@manager_required
def get_deal(deal_id):
    try:
        deals_data = bd.read_deal(deal_id=deal_id)
        print(deals_data)
        if not deals_data:
            flash('Сделка не найдена', 'warning')
            return redirect(url_for('manager.get_deals'))

        return render_template(
            'manager/deals/detail.html',
            deal=deals_data
        )

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        return redirect(url_for('manager.get_deals'))


@manager_bp.route('/clients/<int:id>/new-deal/', methods=['GET', 'POST'])
@manager_required
def create_deal(id):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            deal_data = {
                'manager_id': user_session.get('user_id'),
                'client_id': id,
                'car_brand': request.form.get('car_brand'),
                'car_seller': request.form.get('car_seller'),
                'type_deal': request.form.get('type_deal'),
                'stage_deal': request.form.get('stage_deal'),
                'prepayment': request.form.get('prepayment'),
                'first_payment': request.form.get('first_payment'),
                'term': request.form.get('term'),
                'dfl_currency': request.form.get('dfl_currency'),
                'interest_rate': request.form.get('interest_rate'),
                'effective_rate': request.form.get('effective_rate'),
                'applied_certificate': request.form.get('applied_certificate'),
                'issued_certificate': request.form.get('issued_certificate'),
                'is_express': request.form.get('is_express') == 'on',
                'is_electric_car': request.form.get('is_electric_car') == 'on',
                'financing_amount_usd_with_vat': request.form.get('financing_amount_usd_with_vat'),
                'deal_comment': request.form.get('deal_comment'),
                'agent_name': request.form.get('agent_name'),
                'pv_in_sap': request.form.get('pv_in_sap') == 'on',
                'originals_or_scans': request.form.get('originals_or_scans'),
                'status_deal': request.form.get('status_deal'),
                'deal_amount_at_conclusion': request.form.get('deal_amount_at_conclusion'),
                'deal_currency': request.form.get('deal_currency'),
                'client_refusal_reason': request.form.get('client_refusal_reason'),
                'description_manager': request.form.get('description_manager'),
            }


            date_format = {
                'first_contact_date': '%Y-%m-%d',
                'planned_shipment_date': '%Y-%m-%d',
                'application_datetime': '%Y-%m-%d %H:%M',
                'car_shipment_date': '%Y-%m-%d'
            }

            # Обработка дат
            date_fields = [
                'first_contact_date', 'planned_shipment_date', 'application_datetime',
                'car_shipment_date'
            ]

            for field in date_fields:
                if request.form.get(field):
                    deal_data[field] = datetime.strptime(request.form.get(field), date_format[field]).date()
                else:
                    deal_data[field] = None

            # Обработка временного интервала
            deal_data['stop_list_duration'] = request.form.get('stop_list_duration') or None
            deal_data['delay_comments'] = request.form.get('delay_comments') or None

            # Создаем сделку
            bd.create_deal(**deal_data)
            flash('Сделка успешно создана!', 'success')
            return redirect(url_for('manager.get_clients_by_id', id=id))

        except ValueError as e:
            flash(f'Ошибка при создании сделки: {str(e)}', 'danger')
        except Exception as e:
            flash('Произошла ошибка при создании сделки', 'danger')
            print(f"Error creating deal: {str(e)}")

    # Для GET запроса - отображаем форму
    with bd.Session() as session:
        experts = session.query(User).join(User.role).filter(
            User.deleted_at.is_(None),
            Role.name == 'expert'  # Фильтр по названию роли
        ).all()
        managers = session.query(User).join(User.role).filter(
            User.deleted_at.is_(None),
            Role.name == 'manager'  # Фильтр по названию роли
        ).all()
        currencies = read_currency()
        statuses = read_status_deals()

        decision_bodies = read_body_decisions()
        originals_types = read_type_documents()
        creditworthiness_levels = read_creditworthiness()
        stages = read_stage_deals()
        type_deal = read_type_deals()

    return render_template(
        'manager/deals/create.html',
        managers=managers,
        experts=experts,
        clients_id=id,
        statuses=statuses,
        currencies=currencies,
        originals_types=originals_types,
        stages=stages,
        type_deal=type_deal
    )


@manager_bp.route('/deals/update/<int:id>', methods=['GET', 'POST'])
@manager_required
def update_deal(id):
    if request.method == 'POST':
        try:
            # Для отладки: выведем все полученные данные формы
            print("Полученные данные формы:", request.form)

            # Собираем данные формы с явным указанием имен полей модели
            form_data = {
                'car_brand': request.form.get('car_brand') or None,
                'car_seller': request.form.get('car_seller') or None,
                'type_deal': request.form.get('type_deal') or None,
                'stage_deal': request.form.get('stage_deal') or None,
                'dfl_currency': request.form.get('dfl_currency') or None,
                'deal_comment': request.form.get('deal_comment') or None,
                'deal_amount_at_conclusion': request.form.get('deal_amount_at_conclusion') or None,
                'delay_comments': request.form.get('delay_comments') or None,
                'description_manager': request.form.get('description_manager') or None,
                'prepayment': request.form.get('prepayment') or None,
                'first_payment': request.form.get('first_payment') or None,
                'interest_rate': request.form.get('interest_rate') or None,
                'effective_rate': request.form.get('effective_rate') or None,
                'term': request.form.get('term') or None,
                'first_contact_date': request.form.get('first_contact_date') or None,
                'is_express': request.form.get('is_express') == 'on',
                'is_electric_car': request.form.get('is_electric_car') == 'on',
                'financing_amount_usd_with_vat': request.form.get('financing_amount_usd_with_vat') or None,
                'planned_shipment_date': request.form.get('planned_shipment_date') or None,
                'pv_in_sap': request.form.get('pv_in_sap') == 'on',
                'type_document': request.form.get('type_document') or None,
                'status_deal': request.form.get('status_deal') or None,
                'deal_currency': request.form.get('deal_currency') or None,
                'car_shipment_date': request.form.get('car_shipment_date') or None,
                'client_refusal_reason': request.form.get('client_refusal_reason') or None,
                'agent_name': request.form.get('agent_name') or None,
                'applied_certificate': request.form.get('applied_certificate') or None,
                'issued_certificate': request.form.get('issued_certificate') or None
            }

            # Обработка числовых полей
            decimal_fields = [
                'prepayment', 'first_payment', 'interest_rate', 'effective_rate',
                'financing_amount_usd_with_vat', 'deal_amount_at_conclusion'
            ]

            # Обработка Decimal полей
            for field in decimal_fields:
                if field in form_data:
                    value = form_data.get(field)
                    if value in [None, '']:
                        form_data[field] = None
                    else:
                        try:
                            # Заменяем запятую на точку для корректного парсинга
                            value_str = str(value).replace(',', '.').strip()
                            form_data[field] = Decimal(value_str)
                        except (ValueError, InvalidOperation, TypeError) as e:
                            print(f"Ошибка преобразования {field} в Decimal: {value}. Ошибка: {str(e)}")
                            form_data[field] = None

            # Обработка поля term (как строка)
            if 'term' in form_data:
                form_data['term'] = str(form_data['term']) if form_data['term'] not in [None, ''] else None

            # Обработка дат
            date_fields = {
                'first_contact_date': '%Y-%m-%d',
                'planned_shipment_date': '%Y-%m-%d',
                'car_shipment_date': '%Y-%m-%d'
            }


            for field, fmt in date_fields.items():
                if field in form_data and form_data[field]:
                    try:
                        form_data[field] = datetime.strptime(form_data[field], fmt)
                    except (ValueError, TypeError):
                        form_data[field] = None
                else:
                    form_data[field] = None

            update_data = {k: v for k, v in form_data.items()}

            # Для отладки: выведем данные перед обновлением
            print("Данные для обновления:", update_data)

            updated_deal = bd.update_deal(deal_id=id, **update_data)

            if updated_deal:
                flash('Сделка успешно обновлена!', 'success')
            else:
                flash('Не удалось обновить сделку', 'danger')

            return redirect(url_for('manager.get_deals'))

        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')
            return redirect(url_for('manager.update_deal', id=id))

    # GET запрос остается без изменений
    with bd.Session() as session:
        deal = session.query(bd.Deal).filter_by(id=id).first()
        if not deal:
            flash('Сделка не найдена', 'danger')
            return redirect(url_for('manager.get_deals'))

        statuses = read_status_deals()
        currencies = read_currency()
        decision_bodies = read_body_decisions()
        originals_types = read_type_documents()
        type_deals = read_type_deals()
        stages = read_stage_deals()

    return render_template(
        'manager/deals/update.html',
        deal=deal,
        statuses=statuses,
        currencies=currencies,
        decision_bodies=decision_bodies,
        originals_types=originals_types,
        type_deals=type_deals,
        stages=stages
    )

@manager_bp.route('/deals/delete/<int:id>', methods=['GET', 'POST'])
@manager_required
def delete_deal(id):
    if request.method == 'POST':
        try:
            bd.soft_delete_deal(id)
            return redirect(request.referrer)
        except Exception as e:
            return jsonify({"message": f"произошла ошибка {e}"})
    else:
        return jsonify({"message": "Неправильный метод"})


                        ###########
                        # Клиенты #
                        ###########



@manager_bp.route('/clients/', methods=['GET'])
@manager_required
def get_clients():
    try:
        # Получаем параметры из запроса
        unp = request.args.get('unp')
        client_name = request.args.get('client_name')
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)


        # Валидация параметров
        if page < 1 or per_page < 1 or per_page > 100:
            flash('Некорректные параметры пагинации', 'error')
            return redirect(url_for('manager.index'))

        # Получаем данные из БД
        clients_data = bd.read_clients(
            unp=unp,
            client_name=client_name,
            page=page,
            per_page=per_page
        )

        if not clients_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('manager.index'))

        # Подготовка параметров для шаблона
        template_params = {
            'clients': clients_data['data'],
            'meta': clients_data['meta'],
            'filters': {
                'unp': unp or '',
                'client_name': client_name or '',
                'per_page': per_page
            },
            'client_types': ['ФЛ', 'ЮЛ']
        }

        return render_template('manager/clients/list.html', **template_params)

    except Exception as e:
        print(f'Error in get_clients: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('manager.index'))



@manager_bp.route('/clients/<int:id>/', methods=['GET'])
@manager_required
def get_clients_by_id(id):
    try:
        data = bd.read_client_by_id(id)
        client_data = data.get('data_client')
        deals_data = data.get('client_deals')
        if not client_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('manager.index'))

        print(data.get('client_deals'))
        return render_template('manager/clients/detail.html', client=client_data, deals=deals_data)

    except Exception as e:
        print(f'Error in get_clients_by_id: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('manager.index'))


@manager_bp.route('/clients/create', methods=['GET', 'POST'])
@manager_required
def create_client():
    if request.method == 'POST':
        try:
            client_data = {
                'client_name': request.form.get('client_name') or None,
                'unp': request.form.get('unp'),
                'type_client': request.form.get('type_client') or None,
                'egr_phone': request.form.get('egr_phone') or None,
                'registration_date': request.form.get('registration_date') or None,
                'address': request.form.get('address') or None
            }

            if not client_data['unp']:
                flash('УНП является обязательным полем', 'error')
                return redirect(url_for('manager.create_client'))

            # Преобразование даты только если она есть
            if client_data['registration_date']:
                try:
                    client_data['registration_date'] = datetime.strptime(
                        client_data['registration_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    flash('Некорректный формат даты', 'error')
                    return redirect(url_for('manager.create_client'))


            client_id = bd.create_client(client_data)

            flash('Клиент успешно создан', 'success')
            return redirect(url_for('manager.get_clients_by_id', id=client_id))

        except Exception as e:
            flash(f'Произошла ошибка при создании клиента: {str(e)}', 'error')
            return redirect(url_for('manager.create_client'))

    client_types = read_type_clients()

    return render_template('manager/clients/create.html', client_types=client_types)


@manager_bp.route('/clients/update/<int:id>', methods=['GET', 'POST'])
@manager_required
def update_client(id):
    if request.method == 'POST':
        try:
            # Подготовка данных для обновления
            update_data = {
                'client_name': request.form.get('client_name') or None,
                'unp': request.form.get('unp'),
                'type_client': request.form.get('type_client') or None,
                'egr_phone': request.form.get('egr_phone') or None,
                'address': request.form.get('address') or None
            }

            # Обработка даты регистрации
            reg_date = request.form.get('registration_date')
            if reg_date:
                try:
                    update_data['registration_date'] = datetime.strptime(reg_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Некорректный формат даты регистрации', 'error')
                    return redirect(url_for('manager.update_client', id=id))
            else:
                update_data['registration_date'] = None

            # Валидация обязательного поля УНП
            if not update_data['unp']:
                flash('УНП является обязательным полем', 'error')
                return redirect(url_for('manager.update_client', id=id))

            # Обновление клиента в БД
            updated_client = bd.update_client(
                client_id=id,
                **update_data
            )

            if updated_client:
                flash('Данные клиента успешно обновлены', 'success')
                return redirect(url_for('manager.get_clients_by_id', id=id))
            else:
                flash('Клиент не найден', 'error')
                return redirect(url_for('manager.get_clients'))

        except Exception as e:
            flash(f'Произошла ошибка при обновлении: {str(e)}', 'error')
            return redirect(url_for('manager.update_client', id=id))

    # GET запрос - отображаем форму редактирования
    with bd.Session() as session:
        client = session.query(bd.Client).filter_by(id=id).first()
        if not client:
            flash('Клиент не найден', 'error')
            return redirect(url_for('manager.get_clients'))

        # Подготовка списка типов клиентов для формы
        client_types = read_type_clients()

        return render_template(
            'manager/clients/update.html',
            client=client,
            client_types=client_types
        )


@manager_bp.route('/clients/delete/<int:id>', methods=['GET', 'POST'])
@manager_required
def delete_client(id):
    if request.method == 'POST':
        try:
            bd.soft_delete_client(id)
            return redirect(url_for('manager.get_clients'))
        except Exception as e:
            return jsonify({"message": f"произошла ошибка {e}"})
    else:
        return jsonify({"message": "Неправильный метод"})
