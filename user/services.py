from random import choices
import string

import requests

from .models import *
from decimal import *



from asgiref.sync import async_to_sync
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string

import logging
from uuid import uuid4
from django.core.files import File
import os


logger = logging.getLogger(__name__)





def send_to_all_users_websocket_notify(event, event_id, text=''):
    async_to_sync(channel_layer.group_send)('users',
                                            {"type": "user.notify",
                                             'event': event,
                                             'event_id': event_id,
                                             'message': text})


def send_to_user_websocket_notify(user, event, event_id, text):
    if user.is_online:
        async_to_sync(channel_layer.send)(user.channel,
                                          {
                                              "type": "user.notify",
                                              'message': text,
                                              'event': event,
                                              'event_id': event_id
                                          })


def create_user_notification(user, text, send_emal=False, event_id=None):
    Notification.objects.create(user=user,
                                text=text,
                                event_id=event_id
                                )
    if send_emal:
        send_email.delay('Оповещение на сайте ролф.рф',user.email,'notify.html',{'text':text})


def create_random_string(digits=False, num=4):
    if not digits:
        random_string = ''.join(choices(string.ascii_uppercase + string.digits, k=num))
    else:
        random_string = ''.join(choices(string.digits, k=num))
    return random_string


def create_transaction_history(
        user,
        token_id,
        from_user,
        to_user,
        amount,
        description,
        color,
        commission,
        is_to_trade_platform=False,
        is_income=False,
        is_outcome=False,
        is_stacking=False,
        is_ref_bonus=False,
        is_to_services=False,
        is_commission=False,
):
    TransactionHistory.objects.create(
        user=user,
        token_id=token_id,
        from_user=from_user,
        to_user=to_user,
        amount=amount,
        color=color,
        description=description,
        commission=commission,
        is_to_trade_platform=is_to_trade_platform,
        is_income=is_income,
        is_outcome=is_outcome,
        is_stacking=is_stacking,
        is_ref_bonus=is_ref_bonus,
        is_to_services=is_to_services,
        is_commission=is_commission,
    )


def get_user_today_transaction_amont(user,token_id):
    dt = timezone.now()
    start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    user_transaction_history = TransactionHistory.objects.filter(user=user,
                                                                 token_id=token_id,
                                                                 created_at__gte=start,
                                                                 )
    today_total_transfer_amount = 0
    for item in user_transaction_history:
        today_total_transfer_amount += item.amount

    return today_total_transfer_amount


def send_user_to_user_service_amount(data,from_user):
    to_user_id = data.get('to_id')
    service = data.get('service')
    amount = int(data.get('amount'))
    to_user = User.objects.get(id=to_user_id)
    logger.info(f"from_user {from_user.email} send {data}")
    if service == 'yandex':
        if amount > from_user.yandex_services_rub_balance:
            return {'success': False, 'message': 'Недостаточно средств'}
        logger.info(f"from_user {from_user.email} before yandex amount {from_user.yandex_services_rub_balance}")
        logger.info(f"to_user {from_user.email} before yandex amount {to_user.yandex_services_rub_balance}")
        from_user.yandex_services_rub_balance -= amount
        to_user.yandex_services_rub_balance += amount
        from_user.save(update_fields=['yandex_services_rub_balance'])
        to_user.save(update_fields=['yandex_services_rub_balance'])
        logger.info(f"from_user {from_user.email} after yandex amount {from_user.yandex_services_rub_balance}")
        logger.info(f"to_user {from_user.email} after yandex amount {to_user.yandex_services_rub_balance}")
        return {'success': True, 'message': 'Успешно переведено'}

    if service == 'payback':
        if amount > from_user.payback_rub_balance:
            return {'success': False, 'message': 'Недостаточно средств'}
        logger.info(f"from_user {from_user.email} before yandex amount {from_user.payback_rub_balance}")
        logger.info(f"to_user {from_user.email} before yandex amount {to_user.payback_rub_balance}")
        from_user.payback_rub_balance -= amount
        to_user.payback_rub_balance += amount
        from_user.save(update_fields=['payback_rub_balance'])
        to_user.save(update_fields=['payback_rub_balance'])
        logger.info(f"from_user {from_user.email} after yandex amount {from_user.payback_rub_balance}")
        logger.info(f"to_user {from_user.email} after yandex amount {to_user.payback_rub_balance}")
        return {'success': True, 'message': 'Успешно переведено'}


def send_user_to_user(data,from_user):
    """Перевод от пользователя пользователю
     from_user отправитель
     """
    #print(data)

    commission = 0
    to_user_id = data.get('to_id')
    is_gift = data.get('is_gift')
    token_id = data.get('token_id')

    to_user = User.objects.filter(id=to_user_id).first()
    if not to_user:
        result = {'success': False, 'message': 'Получатель не найден'}
        return result

    # сумма перевода
    amount = Decimal(data.get('amount'))
    wallet = from_user.wallets.get(token_id=token_id)
    user_balance = wallet.divident_balance
    #print(user_balance)




    # узнаем сумму переводов за день

    if from_user.is_superuser:
        today_total_transfer_amount = 0
    else:
        today_total_transfer_amount = get_user_today_transaction_amont(from_user,token_id)

    # устанавливаем флан нужна ли комисия, если сумма переводов больше значения указанного в настройках
    if from_user.is_superuser:
        is_need_commission = False
    else:
        if amount > settings.USERTOUSERDAYLYAMONT:
            is_need_commission = True
        else:
            is_need_commission = today_total_transfer_amount > settings.USERTOUSERDAYLYAMONT



    # если сумма перевода меньше или равна торговому балансу отправителя, то отправляем

    if amount <= user_balance:

        to_user_wallet = to_user.wallets.get(token_id=token_id)
        logger.info(f'ID {from_user.id} {from_user.email} try send to ID {to_user.id} {to_user.email} {amount} TOKEN_ID {token_id}')
        # снимаем сумму перевода сбаланса отправителя

        logger.info(f"from_user {from_user.email} before divident_balance {str(wallet.divident_balance)}")
        wallet.divident_balance -= amount
        wallet.save(update_fields=["divident_balance"])
        logger.info(f"from_user {from_user.email} after divident_balance {str(wallet.divident_balance)}")



        if is_need_commission:
            # если нужна коммисия
            # расчет коммисии
            commission = amount * Decimal((settings.USERTOUSERCOMMISSION / 100))
            #print('commission',commission)

            # сумма перевода без учета коммиссии
            amount = amount - commission

            # перевод суммы коммисии на накопительный аккаунт
            commission_account = User.objects.get(id=settings.COMMISSION_ACCOUNT_ID)
            commission_account_wallet = commission_account.wallets.get(token_id=token_id)

            commission_account_wallet.divident_balance += commission
            commission_account_wallet.save(update_fields=['divident_balance'])

            create_transaction_history(user=commission_account,
                                       token_id=token_id,
                                       from_user=to_user,
                                       to_user=commission_account,
                                       amount=commission,
                                       commission=0,
                                       color='positive',
                                       is_commission=True,
                                       is_income=True,
                                       description='Комиссия за перевод'
                                       )
            logger.info(f'Added commission {str(commission)} on account {commission_account.email}')

        if is_gift:
            to_user_wallet.divident_gift_balance += amount
            to_user_wallet.save(update_fields=["divident_gift_balance"])
        else:
            logger.info(f"to_user {to_user.email} before divident_balance {str(to_user_wallet.divident_balance)}")
            to_user_wallet.divident_balance += amount
            to_user_wallet.save(update_fields=["divident_balance"])
            logger.info(f"to_user {to_user.email} after divident_balance {str(to_user_wallet.divident_balance)}")


        create_transaction_history(user=to_user,
                                   token_id=token_id,
                                   to_user=to_user,
                                   commission=commission,
                                   from_user=from_user,
                                   amount=amount,
                                   color='positive',
                                   is_income=True,
                                   description=f"Пользователь ROLF-{from_user.id},"
                                               f"{'подарил' if is_gift else 'перевел'} Вам {data.get('amount')}"
                                               )
        create_transaction_history(user=from_user,
                                   token_id=token_id,
                                   commission=commission,
                                   to_user=to_user,
                                   from_user=from_user,
                                   color='negative',
                                   is_outcome=True,
                                   amount=amount,
                                   description=f"Вы {'подарили' if is_gift else 'перевели'} пользователю ROLF-{to_user.id} {data.get('amount')}"

                                   )

        email_text = f"Пользователь ROLF-{from_user.id}, " \
                     f"{'подарил' if is_gift else 'перевел'} Вам {data.get('amount')} "

        create_user_notification(to_user, email_text, True)
        logger.info(f'ID {from_user.id} {from_user.email} {"GIFT" if is_gift else "MONEY"} to ID {to_user.id} {to_user.email} {amount} with commission {commission}')
        result = {'success': True}
    else:
        logger.warning(f'ID {from_user.id} {from_user.email} try send to ID {to_user_id}  {amount}  - NOT HAVE MONEY')
        result = {'success': False, 'message': 'Не хватает средств'}
    return result


def send_to_trade_site(data,user):
    amount = Decimal(data.get('amount'))
    wallet = user.wallets.get(token_id=data.get('token_id'))
    if wallet.divident_balance >= amount:
        response = requests.post(f'{settings.TRADE_URL}/api/user/money_from_rolf',
                                 data={
                                     'amount': data.get('amount'),
                                     'uuid': user.uuid
                                 })
        logger.info(f"{user.email} before send to trade {str(wallet.divident_balance)}")
        wallet.divident_balance -= Decimal(data.get('amount'))
        wallet.save(update_fields=['divident_balance'])
        if response.status_code == 200:
            logger.info(f"{user.email} send to trade {str(amount)}")
            logger.info(f"{user.email} after send to trade {str(wallet.divident_balance)}")
            create_transaction_history(user=user,
                                       token_id=data.get('token_id'),
                                       commission=0,
                                       to_user=user,
                                       from_user=user,
                                       color='negative',
                                       amount=amount,
                                       is_to_trade_platform=True,
                                       is_outcome=True,
                                       description=f"Вы перевели на торговую площадку {amount}"
                                       )

        else:
            wallet.divident_balance += Decimal(data.get('amount'))
            wallet.save(update_fields=['divident_balance'])
            logger.info(f"{user.email} rollback send to trade {str(amount)}")
            logger.info(f"{user.email} after send to trade {str(wallet.divident_balance)}")
            return {'success': False, 'message': 'Запрос не может быть обработан. Попробуете повторить попытку через пару минут.'}

        return {'success': True}
    else:
        return {'success': False, 'message': 'Недостаточно средств'}


def generateUserBlank(user):

    user.blank_file.delete()
    html = render_to_string('user_blank.html',
                            {
                                'user': user
                            })
    pdf = pydf.generate_pdf(html)
    filename = f'media/{uuid4()}-blank.pdf'
    with open(filename, mode='wb') as f:
        f.write(pdf)

    with open(filename, 'rb') as file:
        user.blank_file.save(filename, File(file), save=True)
    os.remove(filename)
    user.save(update_fields=['blank_file'])
    return user.blank_file.url


def register_on_trade_site(user,data):
    #print(data)
    uuid = uuid4()
    data['uuid'] = uuid
    #print(data)
    response = requests.post(f'{settings.TRADE_URL}/auth/users/', data=data)
    #print(response.json())
    #print(response.status_code)
    if response.status_code == 201:
        user.uuid = uuid
        user.save(update_fields=['uuid'])
        return {'success': True, 'message': 'asd'}
    else:
        return {'success': False, 'message': response.json()}


def withdrawal_earnings(user, token_id):
    wallet = user.wallets.get(token_id=token_id)

    amount_stacking_balance = wallet.stacking_balance
    amount_referall_bonuses = wallet.referall_bonuses
    total_amount = amount_stacking_balance + amount_referall_bonuses
    logger.info(f'User {user.email} before divident_balance {str(wallet.divident_balance)}')
    logger.info(f'User {user.email} before stacking_balance {str(wallet.stacking_balance)}')
    logger.info(f'User {user.email} before referall_bonuses {str(wallet.referall_bonuses)}')
    wallet.divident_balance += total_amount
    wallet.stacking_balance = 0
    wallet.referall_bonuses = 0

    wallet.can_withdrawal = timezone.now() + timedelta(days=7)
    wallet.save(update_fields=['divident_balance','stacking_balance','referall_bonuses','can_withdrawal'])

    UserWithdrawal.objects.create(user=user,
                                  amount=total_amount,
                                  token_id=token_id)

    create_transaction_history(user=user,
                               token_id=token_id,
                               to_user=user,
                               commission=0,
                               from_user=user,
                               amount=total_amount,
                               color='positive',
                               is_income=True,
                               description=f'Еженедельное снятие начислений. '
                                           f'Дисконтное распределение {amount_stacking_balance}. '
                                           f'Партнерские начисления {amount_referall_bonuses}'
                               )


    logger.info(f'User {user.email} withdrawal stacking_balance {str (amount_stacking_balance)}')
    logger.info(f'User {user.email} withdrawal referall_bonuses {str (amount_referall_bonuses)}')
    logger.info(f'User {user.email} after stacking_balance {str(wallet.stacking_balance)}')
    logger.info(f'User {user.email} after referall_bonuses {str(wallet.referall_bonuses)}')
    logger.info(f'User {user.email} after divident_balance {str(wallet.divident_balance)}')

    result = {'success': True, 'message': 'Начисления переведены'}

    return result