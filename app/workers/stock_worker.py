import json
from app.core.rabbitmq import EXCHANGE_NAME, get_connection, publish_event
from app.services.stock_service import reserve_stock


QUEUE_NAME = "stock_queue"


def callback(ch, method, _properties, body):
    data = json.loads(body)
    print("[stock_worker] Recebido:", data)

    try:
        reserve_stock(data["items"])
        publish_event(
            "order.processed",
            {
                "order_id": data.get("order_id"),
                "email": data.get("email"),
                "items": data.get("items", []),
            },
        )
    except Exception as exc:
        print("[stock_worker] error:", exc)

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
        routing_key="payment.completed",
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("[stock_worker] Esperando mensagens...")
    channel.start_consuming()
