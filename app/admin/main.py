from functools import wraps

from flask import jsonify, render_template, request, flash, redirect, url_for, session, Blueprint
from dotenv import load_dotenv
from app.admin import bd

from datetime import datetime

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
def get_deals():
    try:
        # Получаем параметры из запроса
        manager_id = request.args.get('manager_id', type=int)
        client_id = request.args.get('client_id', type=int)
        expert_id = request.args.get('expert_id', type=int)
        status = request.args.get('status')

        # Булевы параметры
        is_express = request.args.get('is_express')
        is_electric = request.args.get('is_electric')
        show_deleted = request.args.get('show_deleted')

        # Преобразуем строковые булевы значения
        if is_express is not None:
            is_express = is_express.lower() == 'true'
        if is_electric is not None:
            is_electric = is_electric.lower() == 'true'
        if show_deleted is not None:
            show_deleted = show_deleted.lower() == 'true'

        # Даты и пагинация
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)


        # Получаем данные из БД
        deals_data = bd.read_deals(
            manager_id=manager_id,
            client_id=client_id,
            expert_id=expert_id,
            status=status,
            is_express=is_express,
            is_electric=is_electric,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
            show_deleted=show_deleted
        )

        if deals_data is None:
            flash('Ошибка при загрузке списка сделок', 'danger')
            return redirect(url_for('admin.index'))

        # Получаем данные для фильтров
        with bd.Session() as session:
            managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None)).filter(bd.User.role_id == 1).all()
            experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None)).filter(bd.User.role_id == 2).all()

            clients = session.query(bd.Client).filter(bd.Client.deleted_at.is_(None)).all()
            statuses = session.query(bd.Deal.application_status).distinct().all()
            statuses = [s[0] for s in statuses if s[0]]

        return render_template(
            'admin/deals/list.html',
            deals=deals_data['data'],
            meta=deals_data['meta'],
            managers=managers,
            clients=clients,
            statuses=statuses,
            request=request,
            experts=experts
        )

    except Exception as e:
        flash(f'Ошибка сервера: {str(e)}', 'danger')
        print("Ошибка", e)
        return redirect(url_for('admin.index'))


# конкретная сделка по айди
@admin_bp.route('/deals/<int:deal_id>/', methods=['GET'])
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




@admin_bp.route('/deals/create/', methods=['GET', 'POST'])
def create_deal():
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            deal_data = {
                'manager_id': request.form.get('manager_id'),
                'client_id': request.form.get('client_id'),
                'car_brand': request.form.get('car_brand'),
                'car_seller': request.form.get('car_seller'),
                'skp_or_bl': request.form.get('skp_or_bl'),
                'shipment_signing': request.form.get('shipment_signing'),
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
                'application_status': request.form.get('application_status'),
                'expert_id': request.form.get('expert_id') or None,  # Пустые значения преобразуем в None
                'deal_amount_at_conclusion': request.form.get('deal_amount_at_conclusion'),
                'deal_currency': request.form.get('deal_currency'),
                'client_refusal_reason': request.form.get('client_refusal_reason'),
                'creditworthiness': request.form.get('creditworthiness'),
                'description_manager': request.form.get('description_manager'),
                'description_ke': request.form.get('description_ke'),
            }

            # Обработка дат
            date_fields = [
                'first_contact_date', 'planned_shipment_date', 'application_datetime',
                'transfer_to_ke_datetime', 'kk_datetime', 'protocol_date',
                'dfl_signing_date', 'car_shipment_date'
            ]

            for field in date_fields:
                if request.form.get(field):
                    deal_data[field] = datetime.strptime(request.form.get(field), '%Y-%m-%d').date()
                else:
                    deal_data[field] = None

            # Обработка временного интервала
            deal_data['stop_list_duration'] = request.form.get('stop_list_duration') or None
            deal_data['delay_comments'] = request.form.get('delay_comments') or None

            # Создаем сделку
            bd.create_deal(**deal_data)
            flash('Сделка успешно создана!', 'success')
            return redirect(url_for('admin.get_deals'))

        except ValueError as e:
            flash(f'Ошибка при создании сделки: {str(e)}', 'danger')
        except Exception as e:
            flash('Произошла ошибка при создании сделки', 'danger')
            print(f"Error creating deal: {str(e)}")

    # Для GET запроса - отображаем форму
    with bd.Session() as session:
        managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 1).all()
        experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 2).all()
        clients = session.query(bd.Client).filter(bd.Client.deleted_at.is_(None)).all()

    statuses = ['Согласование условий', 'Отказ банка', 'Отказ клиента', 'На рассмотрении', 'Сбор документов']
    currencies = ['USD', 'EUR', 'RUB', 'BYN']
    decision_bodies = ['Кредитный комитет', 'Руководитель', 'Автоматически']
    originals_types = ['Оригиналы', 'Сканы', 'Электронные']
    creditworthiness_levels = ['Высокий', 'Средний', 'Низкий', 'Не проверен']

    return render_template(
        'admin/deals/create.html',
        managers=managers,
        experts=experts,
        clients=clients,
        statuses=statuses,
        currencies=currencies,
        decision_bodies=decision_bodies,
        originals_types=originals_types,
        creditworthiness_levels=creditworthiness_levels
    )


@admin_bp.route('/deals/update/<int:id>', methods=['GET', 'POST'])
def update_deal(id):
    if request.method == 'POST':
        try:
            # Автоматическая обработка всех полей формы
            update_data = {}
            for field in request.form:
                value = request.form[field]

                # Boolean-поля
                if field in ['is_express', 'is_electric_car', 'pv_in_sap']:
                    update_data[field] = value == 'on'
                # Пустые значения
                elif value == "":
                    update_data[field] = None
                # Числовые поля
                elif field in ['prepayment', 'first_payment', 'interest_rate',
                               'effective_rate', 'term', 'financing_amount_usd_with_vat']:
                    update_data[field] = float(value) if value else None
                # Остальные поля
                else:
                    update_data[field] = value

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

            for field, fmt in date_fields.items():
                if field in request.form and request.form[field]:
                    update_data[field] = datetime.strptime(request.form[field], fmt)

            # Обновление
            updated_deal = bd.update_deal(deal_id=id, **update_data)
            flash('Сделка обновлена!' if updated_deal else 'Сделка не найдена',
                  'success' if updated_deal else 'danger')
            return redirect(url_for('admin.get_deals'))

        except ValueError as e:
            flash(f'Ошибка в данных: {str(e)}', 'danger')
        except Exception as e:
            flash('Ошибка при обновлении', 'danger')
            print(f"Error updating deal: {str(e)}")


    # Для GET запроса - отображаем форму с текущими данными
    with bd.Session() as session:
        deal = session.query(bd.Deal).filter_by(id=id).first()
        if not deal:
            flash('Сделка не найдена', 'danger')
            return redirect(url_for('admin.get_deals'))

        managers = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 1).all()
        experts = session.query(bd.User).filter(bd.User.deleted_at.is_(None), bd.User.role_id == 2).all()
        clients = session.query(bd.Client).filter(bd.Client.deleted_at.is_(None)).all()

    # Подготовка списков для формы
    statuses = ['Согласование условий', 'Отказ банка', 'Отказ клиента', 'На рассмотрении', 'Сбор документов']
    currencies = ['USD', 'EUR', 'RUB', 'BYN']
    decision_bodies = ['Кредитный комитет', 'Руководитель', 'Автоматически']
    originals_types = ['Оригиналы', 'Сканы', 'Электронные']
    creditworthiness_levels = ['Высокий', 'Средний', 'Низкий', 'Не проверен']

    return render_template(
        'admin/deals/update.html',
        deal=deal,
        managers=managers,
        experts=experts,
        clients=clients,
        statuses=statuses,
        currencies=currencies,
        decision_bodies=decision_bodies,
        originals_types=originals_types,
        creditworthiness_levels=creditworthiness_levels
    )

@admin_bp.route('/deals/delete/<int:id>', methods=['GET', 'POST'])
def delete_deal(id):
    if request.method == 'POST':
        try:
            bd.soft_delete_deal(id)
            return redirect(url_for('admin.get_deals'))
        except Exception as e:
            return jsonify({"message": f"произошла ошибка {e}"})
    else:
        return jsonify({"message": "Неправильный метод"})


                        ###########
                        # Клиенты #
                        ###########



@admin_bp.route('/clients/', methods=['GET'])
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



@admin_bp.route('/clients/<int:id>', methods=['GET'])
def get_clients_by_id(id):
    try:
        client_data = bd.read_client_by_id(id)
        if not client_data:
            flash('Ошибка загрузки данных', 'error')
            return redirect(url_for('admin.index'))


        return render_template('admin/clients/detail.html', client=client_data)

    except Exception as e:
        print(f'Error in get_clients_by_id: {str(e)}')
        flash('Произошла ошибка', 'error')
        return redirect(url_for('admin.index'))


@admin_bp.route('/clients/create', methods=['GET', 'POST'])
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
                    ).date()  # Используем .date() для типа date (без времени)
                except ValueError:
                    flash('Некорректный формат даты', 'error')
                    return redirect(url_for('admin.create_client'))

            client_id = bd.create_client(client_data)

            flash('Клиент успешно создан', 'success')
            return redirect(url_for('admin.get_clients_by_id', id=client_id))

        except Exception as e:
            flash(f'Произошла ошибка при создании клиента: {str(e)}', 'error')
            return redirect(url_for('admin.create_client'))

    return render_template('admin/clients/create.html')
