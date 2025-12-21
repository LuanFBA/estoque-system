import json
from app.core.rabbitmq import EXCHANGE_NAME, get_connection, publish_event


QUEUE_NAME = "order_queue"


def callback(ch, method, _properties, body):
    data = json.loads(body)
    print("[order_worker] Recebido:", data)

    publish_event("payment.processing", data)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = get_connection()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
    )

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="order.created"
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("[order_worker] Esperando mensagens...")
    channel.start_consuming()
