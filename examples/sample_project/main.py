"""Main module for the sample project demonstrating PyArchViz capabilities."""

from pathlib import Path

from models import Order, Product, User
from services import OrderService, PaymentProcessor, UserService
from utils import ConfigManager, Logger


def main() -> None:
    """Main entry point for the application."""
    logger = Logger(__name__)
    config = ConfigManager.load_config("config.yaml")

    logger.info("Starting application...")

    # Initialize services
    user_service = UserService()
    order_service = OrderService()
    payment_processor = PaymentProcessor(config.payment_gateway)

    # Create sample user
    user = User(id=1, username="john_doe", email="john@example.com")
    user_service.create_user(user)

    # Create sample product
    product = Product(id=101, name="Python Book", price=29.99)

    # Create order
    order = Order(id=1001, user_id=user.id, products=[product], total=product.price)

    # Process order
    order_service.create_order(order)
    payment_result = payment_processor.process_payment(order)

    if payment_result.success:
        logger.info(f"Order {order.id} processed successfully!")
    else:
        logger.error(f"Order {order.id} failed: {payment_result.error}")


if __name__ == "__main__":
    main()
