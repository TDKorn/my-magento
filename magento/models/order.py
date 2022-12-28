from __future__ import annotations
import copy
from . import Model, APIResponse
from typing import TYPE_CHECKING, Optional
from functools import cached_property

if TYPE_CHECKING:
    from magento import Client
    from . import Product


class Order(Model):

    """Wrapper for the ``order`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/orders'

    def __init__(self, data: dict, client: Client):
        """Initialize an Order object using an API response from the ``orders`` endpoint

        :param data: raw API response
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
    def excluded_keys(self):
        return ['items', 'payment']

    def get_invoice(self) -> APIResponse:
        """Retrieve the :class:`~.Invoice` of the Order"""
        return self.client.invoices.by_order(self)

    @property
    def id(self):
        """Alias for ``entity_id``"""
        return getattr(self, 'entity_id', None)

    @property
    def number(self):
        """Alias for ``increment_id``"""
        return getattr(self, 'increment_id', None)

    @property
    def shipping_address(self) -> dict:
        """Retrieve the shipping details from ``shipping_assignments``"""
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
        data = copy.deepcopy(self.__payment)
        if additional_info := self.extension_attributes.get('payment_additional_info', {}):
            data.pop('additional_information', None)
            data.update(self.unpack_attributes(additional_info, key='key'))
        return data

    @cached_property
    def items(self):
        return [OrderItem(item, self) for item in self.__items if item.get('parent_item') is None]


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
    def order(self, order: Order):
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
