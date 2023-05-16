from __future__ import annotations
from . import Model, Order
from typing import TYPE_CHECKING, Optional, List, Dict
from functools import cached_property

if TYPE_CHECKING:
    from magento import Client


class Customer(Model):

    """Wrapper for the ``customers`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/customerscustomerId'
    IDENTIFIER = 'id'

    def __init__(self, data: dict, client: Client):
        """Initialize a Customer object using an API response from the ``customers`` endpoint

        :param data: API response from the ``customers`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='customers',
            private_keys=False
        )

    def __repr__(self):
        return f'<Magento Customer: {self.name}>'

    @property
    def excluded_keys(self) -> List[str]:
        return ['default_billing', 'default_shipping']

    @property
    def name(self) -> str:
        """The customer's full name"""
        return getattr(self, "firstname") + " " + getattr(self, "lastname")

    @property
    def is_subscribed(self) -> bool:
        return self.extension_attributes.get('is_subscribed')

    @cached_property
    def default_billing(self) -> Dict:
        """Default billing address details"""
        for address in self.addresses:
            if address.get('default_billing') is True:
                return address
        return {}

    @cached_property
    def default_billing_address(self) -> str:
        """The default billing address, parsed into a single string"""
        return self._build_address(self.default_billing)

    @cached_property
    def default_shipping(self) -> Dict:
        """Default billing address details"""
        for address in self.addresses:
            if address.get('default_shipping') is True:
                return address
        return {}

    @cached_property
    def default_shipping_address(self) -> str:
        """The default shipping address, parsed into a single string"""
        return self._build_address(self.default_shipping)

    def _build_address(self, address_dict: Dict) -> str:
        """Parses an address dict into a single string

        :param address_dict: the address dict to parse
        """
        address_dict['region_code'] = address_dict.get('region', {}).get('region_code')
        address = ' '.join(address_dict.get('street', [])) + ', '

        for field in ('city', 'region_code', 'postcode', 'country_id'):
            if value := address_dict.get(field):
                address += value.replace('None', '') + ', '

        return address.strip(', ')

    def get_orders(self) -> Optional[Order | List[Order]]:
        """Retrieves :class:`~.Order`\s made by the customer

        :returns: orders made by the customer, as an individual or list of :class:`~.Order` objects
        """
        return self.client.orders.by_customer(self)

    def get_invoices(self):
        """Retrieves :class:`~.Invoice`\s for the customer

        :returns: invoices for the customer, as an individual or list of :class:`~.Invoice` objects
        """
        return self.client.invoices.by_customer(self)

    def get_ordered_products(self, exclude_cancelled: bool = True):
        """Retrieves :class:`~.Product`\s that the customer has ordered

        :param exclude_cancelled: flag indicating if products from cancelled orders should be excluded
        :returns: products that the customer has ordered, as an individual or list of :class:`~.Product` objects
        """
        orders = self.get_orders() or []
        products = []

        if not isinstance(orders, list):
            orders = [orders]

        for order in orders:
            if exclude_cancelled:
                products.extend(
                    item.product for item in order.items
                    if item.net_qty_ordered > 0
                )
            else:
                products.extend(order.products)

        unique_products = {product.id: product for product in products}
        return list(unique_products.values())
