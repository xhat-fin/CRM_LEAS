from functools import wraps

from flask import jsonify, render_template, request, flash, redirect, url_for, session, Blueprint
from dotenv import load_dotenv
from CRM_LEAS.app.expert import bd

from CRM_LEAS.app.admin.bd import User, Role
from CRM_LEAS.app.admin.bd import (read_status_deals, read_type_deals, read_currency,
                          read_body_decisions, read_type_documents,
                          read_creditworthiness, read_stage_deals,
                          read_type_clients)

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

expert_bp = Blueprint('expert', __name__, template_folder='templates')

load_dotenv()


@expert_bp.before_request
def before_request():
    allowed_routes = ['login', 'register', 'static', 'api_index']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('auth.login'))



# Декоратор для проверки прав
def expert_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'expert':
            return jsonify({
                "error": f"access denied {session['role']}"
            }), 403
        return f(*args, **kwargs)
    return decorated_function



@expert_bp.route('/', methods=['GET'])
@expert_required
def index():
    return render_template('expert/index.html')


                        ##########
                        # Сделки #
                        ##########



# список всех сделок (фильтрация и пагинация)
@expert_bp.route('/deals/', methods=['GET'])
@expert_required
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
            return redirect(url_for('expert.index'))

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

        return render_template('expert/deals/list.html', **context)

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        print(f"Error in get_deals: {str(e)}")
        return redirect(url_for('expert.index'))


# конкретная сделка по айди
@expert_bp.route('/deals/<int:deal_id>/', methods=['GET'])
@expert_required
def get_deal(deal_id):
    try:
        deals_data = bd.read_deal(deal_id=deal_id)
        print(deals_data)
        if not deals_data:
            flash('Сделка не найдена', 'warning')
            return redirect(url_for('expert.get_deals'))

        return render_template(
            'expert/deals/detail.html',
            deal=deals_data
        )

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        return redirect(url_for('expert.get_deals'))


@expert_bp.route('/deals/update/<int:id>', methods=['GET', 'POST'])
@expert_required
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
                'stop_list_duration': request.form.get('stop_list_duration') or None,
                'delay_comments': request.form.get('delay_comments') or None,
                'description_manager': request.form.get('description_manager') or None,
                'description_ke': request.form.get('description_ke') or None,
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
                'application_datetime': request.form.get('application_datetime') or None,
                'type_document': request.form.get('originals_or_scans') or None,
                'body_decision': request.form.get('decision_making_body') or None,
                'status_deal': request.form.get('application_status') or None,
                'creditworthiness': request.form.get('creditworthiness') or None,
                'deal_currency': request.form.get('deal_currency') or None,
                'kk_datetime': request.form.get('kk_datetime') or None,
                'protocol_date': request.form.get('protocol_date') or None,
                'dfl_signing_date': request.form.get('dfl_signing_date') or None,
                'car_shipment_date': request.form.get('car_shipment_date') or None,
                'client_refusal_reason': request.form.get('client_refusal_reason') or None,
                'agent_name': request.form.get('agent_name') or None,
                'applied_certificate': request.form.get('applied_certificate') or None,
                'issued_certificate': request.form.get('issued_certificate') or None
            }

            # Обработка числовых полей
            int_fields = ['manager_id', 'expert_id', 'accounter_id']
            decimal_fields = [
                'prepayment', 'first_payment', 'interest_rate', 'effective_rate',
                'financing_amount_usd_with_vat', 'deal_amount_at_conclusion'
            ]

            # Обработка целочисленных полей
            for field in int_fields:
                if field in form_data:
                    value = form_data[field]
                    if value in [None, '']:
                        form_data[field] = None
                    else:
                        try:
                            form_data[field] = int(value)
                        except (ValueError, TypeError) as e:
                            print(f"Ошибка преобразования {field} в int: {value}. Ошибка: {str(e)}")
                            form_data[field] = None

            # Обработка Decimal полей
            for field in decimal_fields:
                if field in form_data:
                    value = form_data[field]
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
                'application_datetime': '%Y-%m-%dT%H:%M',
                'transfer_to_ke_datetime': '%Y-%m-%dT%H:%M',
                'kk_datetime': '%Y-%m-%dT%H:%M',
                'protocol_date': '%Y-%m-%d',
                'dfl_signing_date': '%Y-%m-%d',
                'car_shipment_date': '%Y-%m-%d'
            }

            if 'stop_list_duration' in form_data and form_data['stop_list_duration']:
                try:
                    days = int(form_data['stop_list_duration'])
                    form_data['stop_list_duration'] = timedelta(days=days)
                except (ValueError, TypeError):
                    form_data['stop_list_duration'] = None
            else:
                form_data['stop_list_duration'] = None

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

            return redirect(url_for('expert.get_deals'))

        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')
            print(f"Error updating deal: {str(e)}", exc_info=True)
            return redirect(url_for('expert.update_deal', id=id))

    # GET запрос остается без изменений
    with bd.Session() as session:
        deal = session.query(bd.Deal).filter_by(id=id).first()
        if not deal:
            flash('Сделка не найдена', 'danger')
            return redirect(url_for('expert.get_deals'))

        # managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 1).all()
        # experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 2).all()

        experts = session.query(User).join(User.role).filter(
            User.deleted_at.is_(None),
            Role.name == 'expert'  # Фильтр по названию роли
        ).all()
        managers = session.query(User).join(User.role).filter(
            User.deleted_at.is_(None),
            Role.name == 'manager'  # Фильтр по названию роли
        ).all()

        statuses = read_status_deals()
        currencies = read_currency()
        decision_bodies = read_body_decisions()
        originals_types = read_type_documents()
        creditworthiness_levels = read_creditworthiness()
        type_deals = read_type_deals()
        stages = read_stage_deals()

    return render_template(
        'expert/deals/update.html',
        deal=deal,
        managers=managers,
        experts=experts,
        statuses=statuses,
        currencies=currencies,
        decision_bodies=decision_bodies,
        originals_types=originals_types,
        creditworthiness_levels=creditworthiness_levels,
        type_deals=type_deals,
        stages=stages
    )

@expert_bp.route('/deals/delete/<int:id>', methods=['GET', 'POST'])
@expert_required
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



@expert_bp.route('/clients/', methods=['GET'])
@expert_required
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
            return redirect(url_for('expert.index'))

        # Получаем данные из БД
        clients_data = bd.read_clients(
            unp=unp,
            client_name=client_name,
            page=page,
            per_page=per_page
        )

        if not clients_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('expert.index'))

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

        return render_template('expert/clients/list.html', **template_params)

    except Exception as e:
        print(f'Error in get_clients: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('expert.index'))



@expert_bp.route('/clients/<int:id>/', methods=['GET'])
@expert_required
def get_clients_by_id(id):
    try:
        data = bd.read_client_by_id(id)
        client_data = data.get('data_client')
        deals_data = data.get('client_deals')
        if not client_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('expert.index'))

        print(data.get('client_deals'))
        return render_template('expert/clients/detail.html', client=client_data, deals=deals_data)

    except Exception as e:
        print(f'Error in get_clients_by_id: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('expert.index'))


@expert_bp.route('/clients/create', methods=['GET', 'POST'])
@expert_required
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
                return redirect(url_for('expert.create_client'))

            # Преобразование даты только если она есть
            if client_data['registration_date']:
                try:
                    client_data['registration_date'] = datetime.strptime(
                        client_data['registration_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    flash('Некорректный формат даты', 'error')
                    return redirect(url_for('expert.create_client'))


            client_id = bd.create_client(client_data)

            flash('Клиент успешно создан', 'success')
            return redirect(url_for('expert.get_clients_by_id', id=client_id))

        except Exception as e:
            flash(f'Произошла ошибка при создании клиента: {str(e)}', 'error')
            return redirect(url_for('expert.create_client'))

    client_types = read_type_clients()

    return render_template('expert/clients/create.html', client_types=client_types)


@expert_bp.route('/clients/update/<int:id>', methods=['GET', 'POST'])
@expert_required
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
                    return redirect(url_for('expert.update_client', id=id))
            else:
                update_data['registration_date'] = None

            # Валидация обязательного поля УНП
            if not update_data['unp']:
                flash('УНП является обязательным полем', 'error')
                return redirect(url_for('expert.update_client', id=id))

            # Обновление клиента в БД
            updated_client = bd.update_client(
                client_id=id,
                **update_data
            )

            if updated_client:
                flash('Данные клиента успешно обновлены', 'success')
                return redirect(url_for('expert.get_clients_by_id', id=id))
            else:
                flash('Клиент не найден', 'error')
                return redirect(url_for('expert.get_clients'))

        except Exception as e:
            flash(f'Произошла ошибка при обновлении: {str(e)}', 'error')
            return redirect(url_for('expert.update_client', id=id))

    # GET запрос - отображаем форму редактирования
    with bd.Session() as session:
        client = session.query(bd.Client).filter_by(id=id).first()
        if not client:
            flash('Клиент не найден', 'error')
            return redirect(url_for('expert.get_clients'))

        # Подготовка списка типов клиентов для формы
        client_types = read_type_clients()

        return render_template(
            'expert/clients/update.html',
            client=client,
            client_types=client_types
        )

@expert_bp.route('/clients/delete/<int:id>', methods=['GET', 'POST'])
@expert_required
def delete_client(id):
    if request.method == 'POST':
        try:
            bd.soft_delete_client(id)
            return redirect(url_for('expert.get_clients'))
        except Exception as e:
            return jsonify({"message": f"произошла ошибка {e}"})
    else:
        return jsonify({"message": "Неправильный метод"})

