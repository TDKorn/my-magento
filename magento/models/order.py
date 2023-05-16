from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Union
from functools import cached_property
from . import Model
import copy

if TYPE_CHECKING:
    from magento import Client
    from . import Product, Invoice, Customer


class Order(Model):

    """Wrapper for the ``orders`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/orders'
    IDENTIFIER = 'entity_id'

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
    def excluded_keys(self) -> List[str]:
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
        """The ordered items, returned as a list of :class:`OrderItem` objects

        .. note:: When a configurable :class:`~.Product` is ordered, the API returns data
           for both the configurable and simple product

           * The :class:`OrderItem` is initialized using the configurable product data, since
             the simple product data is incomplete
           * The :attr:`~.OrderItem.product` and :attr:`~.OrderItem.product_id` will still
             match the simple product though

           If both entries are needed, the unparsed response is in the :attr:`~.data` dict
        """
        return [OrderItem(item, order=self) for item in self.__items if item.get('parent_item') is None]

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
    def customer(self) -> Customer:
        return self.client.customers.by_order(self)

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
        address = ' '.join(address_dict.get('street', [])) + ', '
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
    IDENTIFIER = 'item_id'

    def __init__(self, item: dict, client: Optional[Client] = None, order: Optional[Order] = None):
        """Initialize an OrderItem using an API response from the ``orders/items`` endpoint

        .. note:: Initialization requires either a :class:`~.Client` or :class:`Order` object

        :param item: API response from the ``orders/items`` endpoint
        :param order: the :class:`Order` that this is an item of
        :param client: the :class:`~.Client` to use (if not initializing with an Order)
        :raise ValueError: if both the ``order`` and ``client`` aren't provided
        """
        if client is None:
            if order is None:
                raise ValueError('An Order or Client object must be provided')
            if not isinstance(order, Order):
                raise TypeError(f'`order` must be of type {Order}')

        super().__init__(
            data=item,
            client=client if client else order.client,
            endpoint='orders/items'
        )
        self.tax = item.get('base_tax_amount', item.get('tax_amount', 0))
        self.refund = item.get('base_amount_refunded', item.get('amount_refunded', 0))
        self.tax_refunded = item.get('base_tax_refunded', item.get('tax_refunded', 0))
        self.line_total = item.get('base_row_total_incl_tax', item.get('row_total_incl_tax', 0))
        self._order = order

    def __repr__(self):
        return f"<OrderItem ({self.sku})> from Order ID: {self.order_id}>"

    @property
    def excluded_keys(self) -> List[str]:
        return ['product_id']

    @cached_property
    def order(self) -> Order:
        """The corresponding :class:`Order`"""
        if self._order is None:
            return self.client.orders.by_id(self.order_id)
        return self._order

    @cached_property
    def product(self) -> Product:
        """The item's corresponding :class:`~.Product`

        .. note:: **If the ordered item:**

           * Is a configurable product - the child simple product is returned
           * Has custom options - the base product is returned
        """
        if self.product_type != 'configurable':
            return self.client.products.by_id(self.product_id)

        if not self.extension_attributes.get('custom_options'):
            return self.client.products.by_sku(self.sku)

        # Configurable + Custom Options -> configurable product id & unsearchable option sku
        for item in self.order.data['items']:  # Get simple product id from response data
            if item.get('parent_item_id') == self.item_id:
                return self.client.products.by_id(item['product_id'])

    @cached_property
    def product_id(self) -> int:
        """Id of the corresponding simple :class:`~.Product`"""
        return self.__product_id if self.product_type != 'configurable' else self.product.id

    @cached_property
    def extension_attributes(self) -> dict:
        return getattr(self, 'product_option', {}).get('extension_attributes', {})

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
