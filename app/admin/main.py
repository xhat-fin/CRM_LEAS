from functools import wraps

from flask import jsonify, render_template, request, flash, redirect, url_for, session, Blueprint
from dotenv import load_dotenv
from app.admin import bd

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

admin_bp = Blueprint('admin', __name__, template_folder='templates')

load_dotenv()


@admin_bp.before_request
def before_request():
    allowed_routes = ['login', 'register', 'static', 'api_index']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('auth.login'))



# Декоратор для проверки прав
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return jsonify({
                "error": f"access denied {session['role']}"
            }), 403
        return f(*args, **kwargs)
    return decorated_function


                    #########
                    # РОУТЫ #
                    #########


@admin_bp.route('/', methods=['GET'])
@admin_required
def index():
    return render_template('admin/index.html')


                    ################
                    # Пользователи #
                    ################


@admin_bp.route('/users/', methods=["GET"])
@admin_required
def get_users():
    try:
        users = bd.read_users()
        if not users:
            return jsonify({"message": "No users found"}), 404

        return render_template('admin/users/view_users.html', data=users)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@admin_bp.route('/users/<int:id>/', methods=['GET'])
@admin_required
def get_user(id):
    try:
        user = bd.read_user_by_id(id)
        if not user:
            return jsonify({"message": "No user found"}), 404

        return render_template('admin/users/user_id.html', user=user)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



                        ##########
                        # Сделки #
                        ##########



# список всех сделок (фильтрация и пагинация)
@admin_bp.route('/deals/', methods=['GET'])
@admin_required
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
            return redirect(url_for('admin.index'))

        # Получаем данные для фильтров
        with bd.Session() as session:
            experts = session.query(bd.User).join(bd.User.role).filter(
                bd.User.deleted_at.is_(None),
                bd.Role.name == 'expert'  # Фильтр по названию роли
            ).all()
            managers = session.query(bd.User).join(bd.User.role).filter(
                bd.User.deleted_at.is_(None),
                bd.Role.name == 'manager'  # Фильтр по названию роли
            ).all()


            statuses = bd.read_status_deals()
            type_deals = bd.read_type_deals()

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

        return render_template('admin/deals/list.html', **context)

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        print(f"Error in get_deals: {str(e)}")
        return redirect(url_for('admin.index'))


# конкретная сделка по айди
@admin_bp.route('/deals/<int:deal_id>/', methods=['GET'])
@admin_required
def get_deal(deal_id):
    try:
        deals_data = bd.read_deal(deal_id=deal_id)
        print(deals_data)
        if not deals_data:
            flash('Сделка не найдена', 'warning')
            return redirect(url_for('admin.get_deals'))

        return render_template(
            'admin/deals/detail.html',
            deal=deals_data
        )

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        return redirect(url_for('admin.get_deals'))




@admin_bp.route('/clients/<int:id>/new-deal/', methods=['GET', 'POST'])
@admin_required
def create_deal(id):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            deal_data = {
                'manager_id': request.form.get('manager_id'),
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
                'decision_making_body': request.form.get('decision_making_body'),
                'status_deal': request.form.get('status_deal'),
                'expert_id': request.form.get('expert_id') or None,
                'deal_amount_at_conclusion': request.form.get('deal_amount_at_conclusion'),
                'deal_currency': request.form.get('deal_currency'),
                'client_refusal_reason': request.form.get('client_refusal_reason'),
                'creditworthiness': request.form.get('creditworthiness'),
                'description_manager': request.form.get('description_manager'),
                'description_ke': request.form.get('description_ke'),
            }

            print(deal_data.get('pv_in_sap'))
            print(deal_data.get('is_electric_car'))
            print(deal_data.get('is_express'))

            date_format = {
                'first_contact_date': '%Y-%m-%d',
                'planned_shipment_date': '%Y-%m-%d',
                'application_datetime': '%Y-%m-%d %H:%M',
                'transfer_to_ke_datetime': '%Y-%m-%d %H:%M',
                'kk_datetime': '%Y-%m-%d %H:%M',
                'protocol_date': '%Y-%m-%d',
                'dfl_signing_date': '%Y-%m-%d',
                'car_shipment_date': '%Y-%m-%d'
            }

            # Обработка дат
            date_fields = [
                'first_contact_date', 'planned_shipment_date', 'application_datetime',
                'transfer_to_ke_datetime', 'kk_datetime', 'protocol_date',
                'dfl_signing_date', 'car_shipment_date'
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
            return redirect(url_for('admin.get_clients_by_id', id=id))

        except ValueError as e:
            flash(f'Ошибка при создании сделки: {str(e)}', 'danger')
        except Exception as e:
            flash('Произошла ошибка при создании сделки', 'danger')
            print(f"Error creating deal: {str(e)}")

    # Для GET запроса - отображаем форму
    with bd.Session() as session:
        # managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 1).all()
        # experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 2).all()
        experts = session.query(bd.User).join(bd.User.role).filter(
            bd.User.deleted_at.is_(None),
            bd.Role.name == 'expert'  # Фильтр по названию роли
        ).all()
        managers = session.query(bd.User).join(bd.User.role).filter(
            bd.User.deleted_at.is_(None),
            bd.Role.name == 'manager'  # Фильтр по названию роли
        ).all()
        currencies = bd.read_currency()
        statuses = bd.read_status_deals()

        decision_bodies = bd.read_body_decisions()
        originals_types = bd.read_type_documents()
        creditworthiness_levels = bd.read_creditworthiness()
        stages = bd.read_stage_deals()
        type_deal = bd.read_type_deals()

    return render_template(
        'admin/deals/create.html',
        managers=managers,
        experts=experts,
        clients_id=id,
        statuses=statuses,
        currencies=currencies,
        decision_bodies=decision_bodies,
        originals_types=originals_types,
        creditworthiness_levels=creditworthiness_levels,
        stages=stages,
        type_deal=type_deal
    )


@admin_bp.route('/deals/update/<int:id>', methods=['GET', 'POST'])
@admin_required
def update_deal(id):
    if request.method == 'POST':
        try:
            # Для отладки: выведем все полученные данные формы
            print("Полученные данные формы:", request.form)

            # Собираем данные формы с явным указанием имен полей модели
            form_data = {
                'manager_id': request.form.get('manager_id') or None,
                'car_brand': request.form.get('car_brand') or None,
                'car_seller': request.form.get('car_seller') or None,
                'type_deal': request.form.get('type_deal') or None,
                'stage_deal': request.form.get('stage_deal') or None,
                'dfl_currency': request.form.get('dfl_currency') or None,
                'deal_comment': request.form.get('deal_comment') or None,
                'expert_id': request.form.get('expert_id') or None,
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
                'transfer_to_ke_datetime': request.form.get('transfer_to_ke_datetime') or None,
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

            return redirect(url_for('admin.get_deals'))

        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')
            print(f"Error updating deal: {str(e)}", exc_info=True)
            return redirect(url_for('admin.update_deal', id=id))

    # GET запрос остается без изменений
    with bd.Session() as session:
        deal = session.query(bd.Deal).filter_by(id=id).first()
        if not deal:
            flash('Сделка не найдена', 'danger')
            return redirect(url_for('admin.get_deals'))

        # managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 1).all()
        # experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 2).all()

        experts = session.query(bd.User).join(bd.User.role).filter(
            bd.User.deleted_at.is_(None),
            bd.Role.name == 'expert'  # Фильтр по названию роли
        ).all()
        managers = session.query(bd.User).join(bd.User.role).filter(
            bd.User.deleted_at.is_(None),
            bd.Role.name == 'manager'  # Фильтр по названию роли
        ).all()

        statuses = bd.read_status_deals()
        currencies = bd.read_currency()
        decision_bodies = bd.read_body_decisions()
        originals_types = bd.read_type_documents()
        creditworthiness_levels = bd.read_creditworthiness()
        type_deals = bd.read_type_deals()
        stages = bd.read_stage_deals()

    return render_template(
        'admin/deals/update.html',
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

@admin_bp.route('/deals/delete/<int:id>', methods=['GET', 'POST'])
@admin_required
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



@admin_bp.route('/clients/', methods=['GET'])
@admin_required
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
            return redirect(url_for('admin.index'))

        # Получаем данные из БД
        clients_data = bd.read_clients(
            unp=unp,
            client_name=client_name,
            page=page,
            per_page=per_page
        )

        if not clients_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('admin.index'))

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

        return render_template('admin/clients/list.html', **template_params)

    except Exception as e:
        print(f'Error in get_clients: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('admin.index'))



@admin_bp.route('/clients/<int:id>/', methods=['GET'])
@admin_required
def get_clients_by_id(id):
    try:
        data = bd.read_client_by_id(id)
        client_data = data.get('data_client')
        deals_data = data.get('client_deals')
        if not client_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('admin.index'))

        print(data.get('client_deals'))
        return render_template('admin/clients/detail.html', client=client_data, deals=deals_data)

    except Exception as e:
        print(f'Error in get_clients_by_id: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('admin.index'))


@admin_bp.route('/clients/create/', methods=['GET', 'POST'])
@admin_required
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
                return redirect(url_for('admin.create_client'))

            # Преобразование даты только если она есть
            if client_data['registration_date']:
                try:
                    client_data['registration_date'] = datetime.strptime(
                        client_data['registration_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    flash('Некорректный формат даты', 'error')
                    return redirect(url_for('admin.create_client'))


            client_id = bd.create_client(client_data)

            flash('Клиент успешно создан', 'success')
            return redirect(url_for('admin.get_clients_by_id', id=client_id))

        except Exception as e:
            flash(f'Произошла ошибка при создании клиента: {str(e)}', 'error')
            return redirect(url_for('admin.create_client'))

    client_types = bd.read_type_clients()

    return render_template('admin/clients/create.html', client_types=client_types)


@admin_bp.route('/clients/update/<int:id>', methods=['GET', 'POST'])
@admin_required
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
                    return redirect(url_for('admin.update_client', id=id))
            else:
                update_data['registration_date'] = None

            # Валидация обязательного поля УНП
            if not update_data['unp']:
                flash('УНП является обязательным полем', 'error')
                return redirect(url_for('admin.update_client', id=id))

            # Обновление клиента в БД
            updated_client = bd.update_client(
                client_id=id,
                **update_data
            )

            if updated_client:
                flash('Данные клиента успешно обновлены', 'success')
                return redirect(url_for('admin.get_clients_by_id', id=id))
            else:
                flash('Клиент не найден', 'error')
                return redirect(url_for('admin.get_clients'))

        except Exception as e:
            flash(f'Произошла ошибка при обновлении: {str(e)}', 'error')
            return redirect(url_for('admin.update_client', id=id))

    # GET запрос - отображаем форму редактирования
    with bd.Session() as session:
        client = session.query(bd.Client).filter_by(id=id).first()
        if not client:
            flash('Клиент не найден', 'error')
            return redirect(url_for('admin.get_clients'))

        # Подготовка списка типов клиентов для формы
        client_types = bd.read_type_clients()

        return render_template(
            'admin/clients/update.html',
            client=client,
            client_types=client_types
        )

@admin_bp.route('/clients/delete/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_client(id):
    if request.method == 'POST':
        try:
            bd.soft_delete_client(id)
            return redirect(url_for('admin.get_clients'))
        except Exception as e:
            return jsonify({"message": f"произошла ошибка {e}"})
    else:
        return jsonify({"message": "Неправильный метод"})



                ###########################
                # распределение сделок КЭ #
                ###########################


@admin_bp.route('/deals/assign/', methods=['GET', 'POST'])
@admin_required
def deal_assign():
    try:
        if request.method == 'POST':
            deal_id = request.form.get('deal_id')
            expert_id = request.form.get('expert_id')

            # Обновляем эксперта для сделки
            if bd.assign_expert_to_deal(deal_id, expert_id):
                flash('Эксперт успешно назначен на сделку', 'success')
            else:
                flash('Ошибка при назначении эксперта', 'danger')

            return redirect(url_for('admin.deal_assign'))

        # Получаем данные из БД
        deals_data = bd.read_deals_assign()

        if deals_data is None:
            flash('Ошибка при загрузке списка сделок', 'danger')
            return redirect(url_for('admin.index'))

        return render_template('admin/deals/assign_deals_expert.html',
                               deals=deals_data['deals'],
                               experts=deals_data['experts'])

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        print(f"Error in deal_assign: {str(e)}")
        return redirect(url_for('admin.index'))


########################
# Конфигурация системы #
########################

@admin_bp.route('/config/', methods=['GET'])
@admin_required
def get_config():
    # Получаем данные для всех таблиц
    context = {
        'currency': bd.read_currency(),
        'type_clients': bd.read_type_clients(),
        'status_deals': bd.read_status_deals(),
        'creditworthiness': bd.read_creditworthiness(),
        'type_documents': bd.read_type_documents(),
        'body_decisions': bd.read_body_decisions(),
        'type_deals': bd.read_type_deals(),
        'stage_deals': bd.read_stage_deals(),
        'teams': bd.read_teams()
    }
    return render_template('admin/config/config.html', **context)


@admin_bp.route('/config/currency/add', methods=['POST'])
@admin_required
def add_currency():
    currency_name = request.form.get('currency_name')
    if currency_name:
        if bd.create_currency(currency_name):
            flash('Валюта успешно добавлена', 'success')
        else:
            flash('Ошибка при добавлении валюты', 'danger')
    return redirect(url_for('admin.get_config'))


@admin_bp.route('/config/currency/update', methods=['POST'])
@admin_required
def update_currency():
    currency_id = request.form.get('id')
    new_name = request.form.get('currency_name')
    if currency_id and new_name:
        if bd.update_currency(currency_id, new_name):
            flash('Валюта успешно обновлена', 'success')
        else:
            flash('Ошибка при обновлении валюты', 'danger')
    return redirect(url_for('admin.get_config'))


@admin_bp.route('/config/currency/delete/<int:currency_id>', methods=['POST'])
@admin_required
def delete_currency(currency_id):
    if bd.delete_currency(currency_id):
        flash('Валюта успешно удалена', 'success')
    else:
        flash('Ошибка при удалении валюты', 'danger')
    return redirect(url_for('admin.get_config'))


# Роуты для TypeClients
@admin_bp.route('/config/type_clients/add', methods=['POST'])
@admin_required
def add_type_client():
    type_client = request.form.get('type_clients')
    if type_client and bd.create_type_client(type_client):
        flash('Тип клиента успешно добавлен', 'success')
    else:
        flash('Ошибка при добавлении типа клиента', 'danger')
    return redirect(url_for('admin.get_config'))

@admin_bp.route('/config/type_clients/update', methods=['POST'])
@admin_required
def update_type_client():
    client_id = request.form.get('id')
    new_type = request.form.get('type_clients')
    if client_id and new_type and bd.update_type_client(client_id, new_type):
        flash('Тип клиента успешно обновлен', 'success')
    else:
        flash('Ошибка при обновлении типа клиента', 'danger')
    return redirect(url_for('admin.get_config'))

@admin_bp.route('/config/type_clients/delete/<int:client_id>', methods=['POST'])
@admin_required
def delete_type_client(client_id):
    if bd.delete_type_client(client_id):
        flash('Тип клиента успешно удален', 'success')
    else:
        flash('Ошибка при удалении типа клиента', 'danger')
    return redirect(url_for('admin.get_config'))


# Роут для добавления статуса сделки
@admin_bp.route('/config/status_deal/add', methods=['POST'])
@admin_required
def add_status_deal():
    status_name = request.form.get('status_deal')
    if status_name:
        if bd.create_status_deal(status_name):
            flash('Статус сделки успешно добавлен', 'success')
        else:
            flash('Ошибка при добавлении статуса сделки', 'danger')
    else:
        flash('Название статуса не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Роут для обновления статуса сделки
@admin_bp.route('/config/status_deal/update', methods=['POST'])
@admin_required
def update_status_deal():
    status_id = request.form.get('id')
    new_status_name = request.form.get('status_deal')

    if status_id and new_status_name:
        if bd.update_status_deal(status_id, new_status_name):
            flash('Статус сделки успешно обновлен', 'success')
        else:
            flash('Ошибка при обновлении статуса сделки', 'danger')
    else:
        flash('Не указан ID или новое название статуса', 'warning')
    return redirect(url_for('admin.get_config'))


# Роут для удаления статуса сделки
@admin_bp.route('/config/status_deal/delete/<int:status_id>', methods=['POST'])
@admin_required
def delete_status_deal(status_id):
    if bd.delete_status_deal(status_id):
        flash('Статус сделки успешно удален', 'success')
    else:
        flash('Ошибка при удалении статуса сделки', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление новой записи
@admin_bp.route('/config/creditworthiness/add', methods=['POST'])
@admin_required
def add_creditworthiness():
    value = request.form.get('creditworthiness')
    if value:
        if bd.create_creditworthiness(value):
            flash('Запись кредитоспособности успешно добавлена', 'success')
        else:
            flash('Ошибка при добавлении записи или слишком длинное значение', 'danger')
    else:
        flash('Значение не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление записи
@admin_bp.route('/config/creditworthiness/update', methods=['POST'])
@admin_required
def update_creditworthiness():
    record_id = request.form.get('id')
    new_value = request.form.get('creditworthiness')

    if record_id and new_value:
        if bd.update_creditworthiness(record_id, new_value):
            flash('Запись кредитоспособности успешно обновлена', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное значение', 'danger')
    else:
        flash('Не указан ID или новое значение', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление записи
@admin_bp.route('/config/creditworthiness/delete/<int:record_id>', methods=['POST'])
@admin_required
def delete_creditworthiness(record_id):
    if bd.delete_creditworthiness(record_id):
        flash('Запись кредитоспособности успешно удалена', 'success')
    else:
        flash('Ошибка при удалении записи', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление типа документа
@admin_bp.route('/config/type_document/add', methods=['POST'])
@admin_required
def add_type_document():
    doc_type = request.form.get('type_document')
    if doc_type:
        if bd.create_type_document(doc_type):
            flash('Тип документа успешно добавлен', 'success')
        else:
            flash('Ошибка при добавлении или слишком длинное значение (макс. 50 символов)', 'danger')
    else:
        flash('Название типа документа не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление типа документа
@admin_bp.route('/config/type_document/update', methods=['POST'])
@admin_required
def update_type_document():
    doc_id = request.form.get('id')
    new_type = request.form.get('type_document')

    if doc_id and new_type:
        if bd.update_type_document(doc_id, new_type):
            flash('Тип документа успешно обновлен', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное значение', 'danger')
    else:
        flash('Не указан ID или новое значение типа', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление типа документа
@admin_bp.route('/config/type_document/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_type_document(doc_id):
    if bd.delete_type_document(doc_id):
        flash('Тип документа успешно удален', 'success')
    else:
        flash('Ошибка при удалении типа документа', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление органа решения
@admin_bp.route('/config/body_decision/add', methods=['POST'])
@admin_required
def add_body_decision():
    body_name = request.form.get('body_decision')
    if body_name:
        if bd.create_body_decision(body_name):
            flash('Орган решения успешно добавлен', 'success')
        else:
            flash('Ошибка при добавлении или слишком длинное название (макс. 50 символов)', 'danger')
    else:
        flash('Название органа решения не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление органа решения
@admin_bp.route('/config/body_decision/update', methods=['POST'])
@admin_required
def update_body_decision():
    body_id = request.form.get('id')
    new_name = request.form.get('body_decision')

    if body_id and new_name:
        if bd.update_body_decision(body_id, new_name):
            flash('Орган решения успешно обновлен', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное название', 'danger')
    else:
        flash('Не указан ID или новое название', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление органа решения
@admin_bp.route('/config/body_decision/delete/<int:body_id>', methods=['POST'])
@admin_required
def delete_body_decision(body_id):
    if bd.delete_body_decision(body_id):
        flash('Орган решения успешно удален', 'success')
    else:
        flash('Ошибка при удалении органа решения', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление типа сделки
@admin_bp.route('/config/type_deal/add', methods=['POST'])
@admin_required
def add_type_deal():
    deal_type = request.form.get('type_deal')
    if deal_type:
        if bd.create_type_deal(deal_type):
            flash('Тип сделки успешно добавлен', 'success')
        else:
            flash('Ошибка при добавлении или слишком длинное название (макс. 50 символов)', 'danger')
    else:
        flash('Название типа сделки не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление типа сделки
@admin_bp.route('/config/type_deal/update', methods=['POST'])
@admin_required
def update_type_deal():
    deal_id = request.form.get('id')
    new_type = request.form.get('type_deal')

    if deal_id and new_type:
        if bd.update_type_deal(deal_id, new_type):
            flash('Тип сделки успешно обновлен', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное название', 'danger')
    else:
        flash('Не указан ID или новое название типа', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление типа сделки
@admin_bp.route('/config/type_deal/delete/<int:deal_id>', methods=['POST'])
@admin_required
def delete_type_deal(deal_id):
    if bd.delete_type_deal(deal_id):
        flash('Тип сделки успешно удален', 'success')
    else:
        flash('Ошибка при удалении типа сделки', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление стадии сделки
@admin_bp.route('/config/stage_deal/add', methods=['POST'])
@admin_required
def add_stage_deal():
    stage_name = request.form.get('stage_deal')
    if stage_name:
        if bd.create_stage_deal(stage_name):
            flash('Стадия сделки успешно добавлена', 'success')
        else:
            flash('Ошибка при добавлении или слишком длинное название (макс. 50 символов)', 'danger')
    else:
        flash('Название стадии не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление стадии сделки
@admin_bp.route('/config/stage_deal/update', methods=['POST'])
@admin_required
def update_stage_deal():
    stage_id = request.form.get('id')
    new_name = request.form.get('stage_deal')

    if stage_id and new_name:
        if bd.update_stage_deal(stage_id, new_name):
            flash('Стадия сделки успешно обновлена', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное название', 'danger')
    else:
        flash('Не указан ID или новое название', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление стадии сделки
@admin_bp.route('/config/stage_deal/delete/<int:stage_id>', methods=['POST'])
@admin_required
def delete_stage_deal(stage_id):
    if bd.delete_stage_deal(stage_id):
        flash('Стадия сделки успешно удалена', 'success')
    else:
        flash('Ошибка при удалении стадии сделки', 'danger')
    return redirect(url_for('admin.get_config'))


# Добавление команды
@admin_bp.route('/config/team/add', methods=['POST'])
@admin_required
def add_team():
    team_name = request.form.get('name')
    if team_name:
        if bd.create_team(team_name):
            flash('Команда успешно добавлена', 'success')
        else:
            flash('Ошибка при добавлении или слишком длинное название (макс. 50 символов)', 'danger')
    else:
        flash('Название команды не может быть пустым', 'warning')
    return redirect(url_for('admin.get_config'))


# Обновление команды
@admin_bp.route('/config/team/update', methods=['POST'])
@admin_required
def update_team():
    team_id = request.form.get('id')
    new_name = request.form.get('name')

    if team_id and new_name:
        if bd.update_team(team_id, new_name):
            flash('Команда успешно обновлена', 'success')
        else:
            flash('Ошибка при обновлении или слишком длинное название', 'danger')
    else:
        flash('Не указан ID или новое название', 'warning')
    return redirect(url_for('admin.get_config'))


# Удаление команды
@admin_bp.route('/config/team/delete/<int:team_id>', methods=['POST'])
@admin_required
def delete_team(team_id):
    result = bd.delete_team(team_id)
    if result is None:
        flash('Невозможно удалить команду - есть привязанные пользователи', 'warning')
    elif result:
        flash('Команда успешно удалена', 'success')
    else:
        flash('Ошибка при удалении команды', 'danger')
    return redirect(url_for('admin.get_config'))


@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            full_name = request.form.get('full_name')
            role_id = request.form.get('role_id')

            updated_user = bd.update_users(
                user_id=id,
                username=username,
                full_name=full_name,
                role_id=int(role_id) if role_id else None
            )

            if updated_user:
                flash('Пользователь успешно обновлен', 'success')
            else:
                flash('Не удалось обновить пользователя', 'danger')

            return redirect(url_for('admin.get_user', id=id))

        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_user', id=id))

    # GET запрос
    with bd.Session() as session:
        user = session.query(bd.User).options(bd.joinedload(bd.User.role)
        ).filter_by(id=id).first()

        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('admin.get_users'))

        roles = session.query(bd.Role).all()

    return render_template(
        'admin/users/edit.html',
        user=user,
        roles=roles
    )


@admin_bp.route('/trash/', methods=['GET'])
@admin_required
def trash_management():
    """Главная страница управления удаленными сущностями"""
    active_tab = request.args.get('tab', 'clients')

    # Получаем количество удаленных записей каждого типа
    clients_count = bd.read_clients(show_deleted=True)['meta']['total'] if bd.read_clients(show_deleted=True) else 0
    deals_count = bd.read_deals(show_deleted=True)['meta']['total'] if bd.read_deals(show_deleted=True) else 0
    users_count = len(bd.read_users(show_deleted=True)) if bd.read_users(show_deleted=True) else 0

    return render_template('admin/trash.html',
                           active_tab=active_tab,
                           clients_count=clients_count,
                           deals_count=deals_count,
                           users_count=users_count)


@admin_bp.route('/trash/clients/', methods=['GET'])
@admin_required
def get_deleted_clients():
    """Получение списка удаленных клиентов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Получаем данные одним запросом
        result = bd.read_clients(
            page=page,
            per_page=per_page,
            show_deleted=True
        )

        if not result:
            flash('Ошибка при загрузке удаленных клиентов', 'danger')
            return redirect(url_for('admin.trash_management'))

        # Получаем общее количество удаленных записей из meta
        counts = {
            'clients_count': result['meta']['total'],
            'deals_count': bd.read_deals(per_page=1, show_deleted=True)['meta']['total'],
            'users_count': len(bd.read_users(show_deleted=True)) if bd.read_users(show_deleted=True) else 0
        }

        return render_template('admin/trash.html',
                               active_tab='clients',
                               clients=result['data'],
                               meta=result['meta'],
                               **counts)
    except Exception as e:
        flash(f'Ошибка при загрузке удаленных клиентов: {str(e)}', 'danger')
        return redirect(url_for('admin.trash_management'))


@admin_bp.route('/trash/deals/', methods=['GET'])
@admin_required
def get_deleted_deals():
    """Получение списка удаленных сделок"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        result = bd.read_deals(
            page=page,
            per_page=per_page,
            show_deleted=True
        )


        counts = {
            'deals_count': result['meta']['total'],
            'clients_count': bd.read_clients(per_page=1, show_deleted=True)['meta']['total'],
            'users_count': len(bd.read_users(show_deleted=True)) if bd.read_users(show_deleted=True) else 0
        }

        return render_template('admin/trash.html',
                               active_tab='deals',
                               deals=result['data'],
                               meta=result['meta'],
                               **counts)
    except Exception as e:
        flash(f'Ошибка при загрузке удаленных сделок: {str(e)}', 'danger')
        return redirect(url_for('admin.trash_management'))


@admin_bp.route('/trash/users/', methods=['GET'])
@admin_required
def get_deleted_users():
    """Получение списка удаленных пользователей"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Добавляем пагинацию в запрос
        users = bd.read_users(show_deleted=True)


        # Вручную применяем пагинацию
        total = len(users)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = users[start:end]

        counts = {
            'users_count': total,
            'clients_count': bd.read_clients(per_page=1, show_deleted=True)['meta']['total'],
            'deals_count': bd.read_deals(per_page=1, show_deleted=True)['meta']['total']
        }

        return render_template('admin/trash.html',
                               active_tab='users',
                               users=paginated_users,
                               meta={
                                   'total': total,
                                   'page': page,
                                   'per_page': per_page,
                                   'has_next': end < total
                               },
                               **counts)
    except Exception as e:
        print(f"Error: {str(e)}")
        flash(f'Ошибка при загрузке удаленных пользователей: {str(e)}', 'danger')
        return redirect(url_for('admin.trash_management'))


@admin_bp.route('/trash/restore/<entity_type>/<int:id>', methods=['POST'])
@admin_required
def restore_entity(entity_type, id):
    """Восстановление удаленной сущности"""
    try:
        with bd.Session() as session:
            if entity_type == 'client':
                entity = session.query(bd.Client).get(id)
            elif entity_type == 'deal':
                entity = session.query(bd.Deal).get(id)
            elif entity_type == 'user':
                entity = session.query(bd.User).get(id)
            else:
                flash('Неверный тип сущности', 'danger')
                return redirect(url_for('admin.trash_management'))

            if not entity:
                flash('Сущность не найдена', 'danger')
                return redirect(url_for('admin.trash_management'))

            entity.deleted_at = None
            session.commit()

            flash(f'{entity_type.capitalize()} успешно восстановлен', 'success')
            return redirect(request.referrer or url_for('admin.trash_management'))
    except Exception as e:
        session.rollback()
        flash(f'Ошибка при восстановлении: {str(e)}', 'danger')
        return redirect(url_for('admin.trash_management'))


@admin_bp.route('/trash/delete/<entity_type>/<int:id>', methods=['POST'])
@admin_required
def hard_delete_entity(entity_type, id):
    """Полное удаление сущности из базы данных"""
    try:
        with bd.Session() as session:
            if entity_type == 'client':
                entity = session.query(bd.Client).get(id)
            elif entity_type == 'deal':
                entity = session.query(bd.Deal).get(id)
            elif entity_type == 'user':
                entity = session.query(bd.User).get(id)
            else:
                flash('Неверный тип сущности', 'danger')
                return redirect(url_for('admin.trash_management'))

            if not entity:
                flash('Сущность не найдена', 'danger')
                return redirect(url_for('admin.trash_management'))

            session.delete(entity)
            session.commit()

            flash(f'{entity_type.capitalize()} полностью удален', 'success')
            return redirect(request.referrer or url_for('admin.trash_management'))
    except Exception as e:
        session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin.trash_management'))