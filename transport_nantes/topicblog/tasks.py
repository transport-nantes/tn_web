import logging
import json
from django.core.serializers import deserialize
from django.core import mail
from celery import shared_task

logger = logging.getLogger("django")


@shared_task
def send_email(serialized_email_object: dict, serialized_send_record: dict):

    deserialized_email_object = json.loads(serialized_email_object)
    for send_record_obj in deserialize("json", serialized_send_record):
        send_record_obj.save()
        deserialized_send_record = send_record_obj

    logger.info(f"send_record : {deserialized_send_record.object}")
    # For some reason, the deserialized email object replaced "headers" with
    # "extra-headers". So we need to replace it.
    deserialized_email_object["headers"] = \
        deserialized_email_object.pop("extra_headers")

    custom_email_object = mail.EmailMultiAlternatives(
        **deserialized_email_object)
    send_record = deserialized_send_record.object

    try:
        custom_email_object.send(fail_silently=False)
        logger.info(f"Successfully sent email to {custom_email_object.to}")
    except Exception as e:
        logger.error(f"Failed to send email to {custom_email_object.to} : {e}")
        send_record.status = "FAILED"
        send_record.save()
