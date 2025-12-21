def process_payment(payment_data):
    try:
        # Simulação de processamento
        print(payment_data, "DATAAAAAAAAAAAAAAA")
        print(
            f"[payment_service] Processando pagamento para o pedido {payment_data.get('order_id')}"
        )
        return True
    except Exception as exc:
        print(f"[payment_service] Erro ao processar pagamento: {exc}")
        return False
