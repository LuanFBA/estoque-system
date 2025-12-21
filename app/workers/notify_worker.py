import json
from app.core.rabbitmq import EXCHANGE_NAME, get_connection
from app.core.config import settings
from app.services.email_service import (
    send_order_processed_email,
    send_payment_failed_email,
)

QUEUE_NAME = "notify_queue"


def callback(ch, method, _properties, body):
    try:
        data = json.loads(body)
        order_id = data.get("order_id")
        email = data.get("email") or settings.notify_email
        print("[notify_worker] Recebido:", data)

        if method.routing_key == "order.processed":
            send_order_processed_email(order_id, email)

        if method.routing_key == "payment.failed":
            reason = data.get("reason") or data.get("error") or "Motivo não informado"
            send_payment_failed_email(order_id, email, reason)

    except Exception as exc:
        print(f"[notify_worker] Erro ao processar mensagem: {exc}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = get_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
    )
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="order.processed"
    )
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="payment.failed"
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("[notify_worker] aguardando mensagens...")
    channel.start_consuming()
