from app.db.session import get_db
from app.models.product import Product
from app.models.stock_movement import StockMovement


def reserve_stock(items: list[dict]):
    print("[stock_service] reservando estoque para itens:", items)
    db_gen = get_db()
    db = next(db_gen)
    movements = []
    try:
        for item in items:
            product = (
                db.query(Product)
                .filter(Product.product_id == item["product_id"])
                .with_for_update()
                .one_or_none()
            )

            if not product:
                raise Exception(f"Produto {item['product_id']} não encontrado")

            if product.quantity_on_hand < item["quantity"]:
                raise Exception(
                    f"Estoque insuficiente para produto {product.product_id}"
                )

            product.quantity_on_hand -= item["quantity"]

            movement = StockMovement(
                product_id=product.product_id,
                quantity=item["quantity"],
                movement_type="saida",
            )
            db.add(movement)
            movements.append(movement)

        db.commit()
        return movements
    except Exception:
        db.rollback()
        raise
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
