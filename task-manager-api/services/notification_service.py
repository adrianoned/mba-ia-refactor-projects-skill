"""Servico de Notificacao — side effects isolados (TR-17).
Credenciais externalizadas via config (TR-01)."""
import smtplib
import logging
from datetime import datetime, timezone
from config.settings import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = settings.SMTP_HOST
        self.email_port = settings.SMTP_PORT
        self.email_user = settings.SMTP_USER
        self.email_password = settings.SMTP_PASS

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as e:
            logger.error("Erro ao enviar email: %s", e)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuida: {task.title}"
        body = (
            f"Ola {user.name},\n\n"
            f"A task '{task.title}' foi atribuida a voce.\n\n"
            f"Prioridade: {task.priority}\n"
            f"Status: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            "type": "task_assigned",
            "user_id": user.id,
            "task_id": task.id,
            "timestamp": datetime.now(timezone.utc),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Ola {user.name},\n\n"
            f"A task '{task.title}' esta atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
