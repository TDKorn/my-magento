from __future__ import annotations
from . import Model, APIResponse
from typing import TYPE_CHECKING, Optional, List
from functools import cached_property
import copy

if TYPE_CHECKING:
    from magento import Client
    from . import Product


class Order(Model):

    """Wrapper for the ``orders`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/orders'

    def __init__(self, data: dict, client: Client):
        """Initialize an Order object using an API response from the ``orders`` endpoint

        :param data: API response from the ``orders`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='orders',
            private_keys=True
        )

    def __repr__(self):
        return f'<Magento Order: #{self.number} placed on {self.created_at}>'

    @property
    def excluded_keys(self) -> list[str]:
        return ['items', 'payment']

    @property
    def id(self) -> int:
        """Alias for ``entity_id``"""
        return getattr(self, 'entity_id', None)

    @property
    def number(self) -> str:
        """Alias for ``increment_id``"""
        return getattr(self, 'increment_id', None)

    @cached_property
    def items(self) -> List[OrderItem]:
        """The ordered items, returned as a list of :class:`OrderItem` objects"""
        return [OrderItem(item, self) for item in self.__items if item.get('parent_item') is None]

    @cached_property
    def item_ids(self) -> List[int]:
        """The ``item_id`` s of the ordered :attr:`~.items`"""
        return [item.item_id for item in self.items]

    @cached_property
    def products(self) -> List[Product]:
        """The ordered :attr:`~items`, returned as their corresponding :class:`~.Product` objects"""
        return [item.product for item in self.items]

    def get_invoice(self) -> Invoice:
        """Retrieve the :class:`~.Invoice` of the Order"""
        return self.client.invoices.by_order(self)

    @property
    def shipping_address(self) -> dict:
        """Shipping details, from ``extension_attributes.shipping_assignments``"""
        return self.extension_attributes.get(
            'shipping_assignments', [{}])[0].get(
            'shipping', {}).get(
            'address', {})

    @property
    def bill_to(self) -> dict:
        """Condensed version of the ``billing_address`` dict"""
        if hasattr(self, 'billing_address'):
            return {
                'firstname': self.billing_address.get('firstname', ''),
                'lastname': self.billing_address.get('lastname', ''),
                'email': self.billing_address.get('email', ''),
                'address': self.bill_to_address
            }

    @property
    def bill_to_address(self) -> str:
        """The billing address, parsed into a single string"""
        return self._build_address('billing')

    @property
    def ship_to(self) -> dict:
        """Condensed version of the :attr:`~.shipping_address` dict"""
        return {
            'firstname': self.shipping_address.get('firstname', ''),
            'lastname': self.shipping_address.get('lastname', ''),
            'email': self.shipping_address.get('email', ''),
            'address': self.ship_to_address
        }

    @property
    def ship_to_address(self) -> str:
        """The shipping address, parsed into a single string"""
        return self._build_address('shipping')

    def _build_address(self, address_type: str) -> str:
        """Parses an address dict into a single string

        :param address_type: the address to parse; either ``shipping`` or ``billing``
        """
        address_dict = getattr(self, f'{address_type}_address')
        address = ' '.join(address_dict.get('street')) + ', '
        for field in ('city', 'region_code', 'postcode', 'country_id'):
            if value := address_dict.get(field):
                address += value.replace('None', '') + ', '
        return address.strip(', ')

    @cached_property
    def payment(self) -> dict:
        """Payment data"""
        data = copy.deepcopy(self.__payment)
        if additional_info := self.extension_attributes.get('payment_additional_info'):
            data.pop('additional_information', None)
            data.update(self.unpack_attributes(additional_info, key='key'))
        return data

    @property
    def net_tax(self) -> float:
        """Final tax amount, with refunds and cancellations taken into account"""
        return self.base_tax_amount - getattr(self, 'base_tax_refunded', 0) - getattr(self, 'base_tax_canceled', 0)

    @property
    def net_total(self) -> float:
        """Final Order value, with refunds and cancellations taken into account"""
        return self.base_grand_total - getattr(self, 'base_total_refunded', 0) - getattr(self, 'base_total_canceled', 0)

    @property
    def item_refunds(self) -> float:
        """Total amount refunded for items; excludes shipping and adjustment refunds/fees"""
        return sum(item.net_refund for item in self.items)

    @cached_property
    def total_qty_invoiced(self) -> int:
        """Total number of units invoiced"""
        return sum(item.qty_invoiced for item in self.items)

    @cached_property
    def total_qty_shipped(self) -> int:
        """Total number of units shipped"""
        return sum(item.qty_shipped for item in self.items)

    @cached_property
    def total_qty_refunded(self) -> int:
        """Total number of units refunded"""
        return sum(item.qty_refunded for item in self.items)

    @cached_property
    def total_qty_canceled(self) -> int:
        """Total number of units canceled"""
        return sum(item.qty_canceled for item in self.items)

    @cached_property
    def total_qty_outstanding(self) -> int:
        """Total number of units that haven't been shipped/fulfilled yet"""
        return sum(item.qty_outstanding for item in self.items)

    @cached_property
    def net_qty_ordered(self) -> int:
        """Total number of units ordered, after accounting for refunds and cancellations"""
        return sum(item.net_qty_ordered for item in self.items)


class OrderItem(Model):

    """Wrapper for the ``order/items`` endpoint"""

    DOCUMENTATION = "https://adobe-commerce.redoc.ly/2.3.7-admin/tag/ordersitems"

    def __init__(self, item: dict, order: Optional[Order] = None, client: Optional[Client] = None):
        """Initialize an OrderItem using an API response from the ``orders/items`` endpoint

        .. note:: Initialization requires either a :class:`~.Client` or :class:`Order` object

        :param item: API response from the ``orders/items`` endpoint
        :param order: the :class:`Order` that this is an item of
        :param client: the :class:`~.Client` to use (if not initializing with an Order)
        :raise ValueError: if both the ``order`` and ``client`` aren't provided
        """
        if order is None and client is None:
            raise ValueError('An Order or Client object must be provided')

        super().__init__(
            data=item,
            client=client if client else order.client,
            endpoint='orders/items'
        )
        self.order = order

        self.tax = item.get('base_tax_amount', item.get('tax_amount', 0))
        self.refund = item.get('base_amount_refunded', item.get('amount_refunded', 0))
        self.tax_refunded = item.get('base_tax_refunded', item.get('tax_refunded', 0))
        self.line_total = item.get('base_row_total_incl_tax', item.get('row_total_incl_tax', 0))

    def __repr__(self):
        return f"<OrderItem ({self.sku})> from {self.order}"

    @property
    def excluded_keys(self) -> list[str]:
        return []

    @property
    def order(self) -> Order:
        """The corresponding :class:`Order`"""
        return self._order

    @order.setter
    def order(self, order: Optional[Order]):
        if order is None:
            self._order = self.client.orders.by_id(self.order_id)
        elif isinstance(order, Order):
            self._order = order
        else:
            raise TypeError

    @cached_property
    def product(self) -> Product:
        """The corresponding simple :class:`~.Product`

        If the ordered item:

        * Is a configurable product - the child product is returned
        * Has customizable options - the base product is returned
        """
        if self.product_type == 'simple':
            return self.client.products.by_id(self.product_id)
        return self.client.products.by_sku(self.sku)

    @cached_property
    def qty_outstanding(self) -> int:
        """Number of units that haven't been shipped/fulfilled yet"""
        return self.net_qty_ordered - self.qty_shipped

    @cached_property
    def net_qty_ordered(self) -> int:
        """Number of units ordered, after accounting for refunds and cancellations"""
        return self.qty_ordered - self.qty_refunded - self.qty_canceled

    @cached_property
    def net_tax(self) -> float:
        """Tax amount after accounting for refunds and cancellations"""
        return self.tax - self.tax_refunded - getattr(self, 'tax_canceled', 0)

    @cached_property
    def net_total(self) -> float:
        """Row total (incl. tax) after accounting for refunds and cancellations"""
        return self.line_total - self.net_refund - self.total_canceled

    @cached_property
    def net_refund(self) -> float:
        """Refund amount after accounting for tax and discount refunds"""
        return self.refund + self.tax_refunded - getattr(self, 'discount_refunded', 0)

    @cached_property
    def total_canceled(self) -> float:
        """Cancelled amount; note that partial cancellation is not possible"""
        if self.qty_canceled != 0:
            return self.line_total
        return 0
