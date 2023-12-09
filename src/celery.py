import sendgrid
from celery import Celery
from sendgrid import Mail, Email, Personalization

from src.config import settings

celery = Celery(
    "shop",
    broker=f"redis://{settings.db.REDIS_HOST}:{settings.db.REDIS_PORT}",
    backend=f"redis://{settings.db.REDIS_HOST}:{settings.db.REDIS_PORT}"
)


@celery.task
def send_mail(template, data, to):
    sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
    mail = Mail()
    mail.template_id = template
    mail.from_email = Email(settings.DEFAULT_FROM_EMAIL)
    personalization = Personalization()
    personalization.add_to(Email(to))
    personalization.dynamic_template_data = data
    mail.add_personalization(personalization)
    sg.client.mail.send.post(request_body=mail.get())
