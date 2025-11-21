"""Service layer for business logic in the sample project."""

from datetime import datetime
from typing import Any

from models import Order, OrderStatus, PaymentResult, User, UserRole


class UserService:
    """Service for managing user operations."""

    def __init__(self) -> None:
        """Initialize the user service."""
        self.users: dict[int, User] = {}

    def create_user(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User object to create

        Returns:
            Created user with timestamp

        Raises:
            ValueError: If user ID already exists
        """
        if user.id in self.users:
            raise ValueError(f"User with ID {user.id} already exists")

        if not user.validate_email():
            raise ValueError("Invalid email format")

        user.created_at = datetime.now()
        self.users[user.id] = user
        return user

    def get_user(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User object or None if not found
        """
        return self.users.get(user_id)

    def update_user(self, user_id: int, **updates: Any) -> User | None:
        """Update user information.

        Args:
            user_id: ID of the user to update
            **updates: Fields to update

        Returns:
            Updated user or None if not found
        """
        user = self.users.get(user_id)
        if not user:
            return None

        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deleted, False if not found
        """
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def list_users(self, role: UserRole | None = None) -> list[User]:
        """List all users, optionally filtered by role.

        Args:
            role: Optional role filter

        Returns:
            List of users
        """
        if role is None:
            return list(self.users.values())
        return [user for user in self.users.values() if user.role == role]


class OrderService:
    """Service for managing order operations."""

    def __init__(self) -> None:
        """Initialize the order service."""
        self.orders: dict[int, Order] = {}

    def create_order(self, order: Order) -> Order:
        """Create a new order.

        Args:
            order: Order object to create

        Returns:
            Created order with timestamps

        Raises:
            ValueError: If order ID already exists or order is invalid
        """
        if order.id in self.orders:
            raise ValueError(f"Order with ID {order.id} already exists")

        if not order.products:
            raise ValueError("Order must contain at least one product")

        order.created_at = datetime.now()
        order.updated_at = datetime.now()
        order.status = OrderStatus.PENDING
        self.orders[order.id] = order
        return order

    def get_order(self, order_id: int) -> Order | None:
        """Get order by ID.

        Args:
            order_id: ID of the order to retrieve

        Returns:
            Order object or None if not found
        """
        return self.orders.get(order_id)

    def update_order_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Update order status.

        Args:
            order_id: ID of the order to update
            status: New order status

        Returns:
            Updated order or None if not found
        """
        order = self.orders.get(order_id)
        if not order:
            return None

        order.status = status
        order.updated_at = datetime.now()
        return order

    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order.

        Args:
            order_id: ID of the order to cancel

        Returns:
            True if cancelled, False if not found or already completed
        """
        order = self.orders.get(order_id)
        if not order:
            return False

        if order.status == OrderStatus.COMPLETED:
            return False

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        return True

    def get_orders_by_user(self, user_id: int) -> list[Order]:
        """Get all orders for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of orders for the user
        """
        return [order for order in self.orders.values() if order.user_id == user_id]

    def get_orders_by_status(self, status: OrderStatus) -> list[Order]:
        """Get all orders with a specific status.

        Args:
            status: Order status to filter by

        Returns:
            List of orders with the specified status
        """
        return [order for order in self.orders.values() if order.status == status]


class PaymentProcessor:
    """Service for processing payments."""

    def __init__(self, gateway_config: dict[str, Any] | None = None) -> None:
        """Initialize the payment processor.

        Args:
            gateway_config: Configuration for payment gateway
        """
        self.gateway_config = gateway_config or {}
        self.transactions: dict[str, PaymentResult] = {}

    def process_payment(self, order: Order) -> PaymentResult:
        """Process payment for an order.

        Args:
            order: Order to process payment for

        Returns:
            Payment result with transaction details
        """
        if order.total <= 0:
            return PaymentResult(
                success=False, error="Invalid order amount", amount=order.total
            )

        # Simulate payment processing
        transaction_id = f"TXN-{order.id}-{int(datetime.now().timestamp())}"

        # In real implementation, this would call external payment gateway
        result = PaymentResult(
            success=True, transaction_id=transaction_id, amount=order.total
        )

        self.transactions[transaction_id] = result
        return result

    def refund_payment(self, transaction_id: str, amount: float) -> PaymentResult:
        """Process a refund for a transaction.

        Args:
            transaction_id: Original transaction ID
            amount: Amount to refund

        Returns:
            Refund result
        """
        original = self.transactions.get(transaction_id)
        if not original:
            return PaymentResult(
                success=False,
                error=f"Transaction {transaction_id} not found",
                amount=amount,
            )

        if amount > original.amount:
            return PaymentResult(
                success=False, error="Refund amount exceeds original", amount=amount
            )

        refund_id = f"REFUND-{transaction_id}-{int(datetime.now().timestamp())}"
        result = PaymentResult(success=True, transaction_id=refund_id, amount=amount)

        self.transactions[refund_id] = result
        return result

    def get_transaction(self, transaction_id: str) -> PaymentResult | None:
        """Get transaction details.

        Args:
            transaction_id: Transaction ID to look up

        Returns:
            Payment result or None if not found
        """
        return self.transactions.get(transaction_id)

    def verify_payment(self, transaction_id: str) -> bool:
        """Verify if a payment was successful.

        Args:
            transaction_id: Transaction ID to verify

        Returns:
            True if payment was successful, False otherwise
        """
        result = self.transactions.get(transaction_id)
        return result is not None and result.is_successful()
