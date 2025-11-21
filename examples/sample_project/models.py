"""Data models for the sample project."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class User:
    """User model representing a customer or admin."""

    id: int
    username: str
    email: str
    role: UserRole = UserRole.USER
    created_at: datetime | None = None

    def is_admin(self) -> bool:
        """Check if user has admin privileges.

        Returns:
            True if user is an admin, False otherwise
        """
        return self.role == UserRole.ADMIN

    def validate_email(self) -> bool:
        """Validate user email format.

        Returns:
            True if email is valid, False otherwise
        """
        return "@" in self.email and "." in self.email


@dataclass
class Product:
    """Product model representing an item for sale."""

    id: int
    name: str
    price: float
    description: str = ""
    stock_quantity: int = 0
    category: str = "general"

    def is_available(self) -> bool:
        """Check if product is in stock.

        Returns:
            True if product has stock, False otherwise
        """
        return self.stock_quantity > 0

    def calculate_discount_price(self, discount_percent: float) -> float:
        """Calculate price after discount.

        Args:
            discount_percent: Discount percentage (0-100)

        Returns:
            Discounted price
        """
        return self.price * (1 - discount_percent / 100)


@dataclass
class Order:
    """Order model representing a customer purchase."""

    id: int
    user_id: int
    products: list[Product]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def add_product(self, product: Product) -> None:
        """Add a product to the order.

        Args:
            product: Product to add
        """
        self.products.append(product)
        self.total += product.price

    def remove_product(self, product_id: int) -> bool:
        """Remove a product from the order.

        Args:
            product_id: ID of the product to remove

        Returns:
            True if product was removed, False if not found
        """
        for i, product in enumerate(self.products):
            if product.id == product_id:
                self.total -= product.price
                self.products.pop(i)
                return True
        return False

    def calculate_total(self) -> float:
        """Calculate total order amount.

        Returns:
            Total price of all products
        """
        return sum(product.price for product in self.products)


@dataclass
class PaymentResult:
    """Payment processing result."""

    success: bool
    transaction_id: str | None = None
    error: str | None = None
    amount: float = 0.0

    def is_successful(self) -> bool:
        """Check if payment was successful.

        Returns:
            True if payment succeeded, False otherwise
        """
        return self.success and self.transaction_id is not None
