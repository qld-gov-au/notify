import uuid

from datetime import datetime
from flask import current_app

from app import statsd_client
from app.clients import ClientException
from app.dao import notifications_dao
from app.clients.sms.sap import get_sap_responses
from app.clients.sms.telstra import get_telstra_responses
from app.clients.sms.twilio import get_twilio_responses
from app.dao.notifications_dao import dao_update_notification
from app.notifications.callbacks import check_for_callback_and_send_delivery_status_to_service


sms_response_mapper = {
    'sap': get_sap_responses,
    'sap_covid': get_sap_responses,
    'telstra': get_telstra_responses,
    'twilio': get_twilio_responses,
}


def validate_callback_data(data, fields, client_name):
    errors = []
    for f in fields:
        if not str(data.get(f, '')):
            error = "{} callback failed: {} missing".format(client_name, f)
            errors.append(error)
    return errors if len(errors) > 0 else None


def process_sms_client_response(status, provider_reference, client_name):
    success = None
    errors = None

    # validate reference
    try:
        uuid.UUID(provider_reference, version=4)
    except ValueError:
        errors = "{} callback with invalid reference {}".format(client_name, provider_reference)
        return success, errors

    try:
        response_parser = sms_response_mapper[client_name]
    except KeyError:
        return success, 'unknown sms client: {}'.format(client_name)

    # validate  status
    try:
        notification_status = response_parser(status)
        current_app.logger.info('{} callback return status of {} for reference: {}'.format(
            client_name, status, provider_reference)
        )
    except KeyError:
        _process_for_status(
            notification_status='technical-failure',
            client_name=client_name,
            provider_reference=provider_reference
        )
        raise ClientException("{} callback failed: status {} not found.".format(client_name, status))

    success = _process_for_status(
        notification_status=notification_status,
        client_name=client_name,
        provider_reference=provider_reference
    )
    return success, errors


def _process_for_status(notification_status, client_name, provider_reference):
    notification = notifications_dao.update_notification_status_by_id(provider_reference, notification_status)
    if not notification:
        current_app.logger.warning("{} callback failed: notification {} either not found or already updated "
                                   "from sending. Status {}".format(client_name,
                                                                    provider_reference,
                                                                    notification_status))
        return

    statsd_client.incr('callback.{}.{}'.format(client_name, notification_status))

    if not notification.sent_by:
        set_notification_sent_by(notification, client_name)

    if notification.sent_at:
        statsd_client.timing_with_dates(
            'callback.{}.elapsed-time'.format(client_name),
            datetime.utcnow(),
            notification.sent_at
        )

    check_for_callback_and_send_delivery_status_to_service(notification)

    success = "{} callback succeeded. reference {} updated".format(client_name, provider_reference)
    return success


def set_notification_sent_by(notification, client_name):
    notification.sent_by = client_name
    dao_update_notification(notification)
