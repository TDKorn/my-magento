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

