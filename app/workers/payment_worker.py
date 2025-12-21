import json
from app.core.rabbitmq import EXCHANGE_NAME, get_connection, publish_event
from app.services.payment_service import process_payment

QUEUE_NAME = "payment_queue"


def callback(ch, method, _properties, body):
    data = json.loads(body)
    print("[payment_worker] Recebido:", data)
    try:
        process_payment(data)
        publish_event("payment.completed", data)
    except Exception as exc:
        print("[payment_worker] error:", exc)
        publish_event("payment.failed", data)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = get_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
    )

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key="payment.processing",
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("[payment_worker] Esperando mensagens...")
    channel.start_consuming()
