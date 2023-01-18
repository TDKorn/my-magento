from __future__ import annotations
from . import Model, Order, OrderItem, Product
from typing import TYPE_CHECKING, Optional, List, Union
from functools import cached_property

if TYPE_CHECKING:
    from magento import Client
    from magento.search import SearchQuery


class Invoice(Model):

    """Wrapper for the ``invoices`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/invoices'
    IDENTIFIER = 'entity_id'

    def __init__(self, data: dict, client: Client):
        """Initialize an Invoice object using an API response from the ``invoices`` endpoint

        :param data: API response from the ``invoices`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='invoices',
            private_keys=True
        )

    def __repr__(self):
        return f'<Magento Invoice: #{self.number}> for {self.order}'

    @property
    def excluded_keys(self) -> List[str]:
        return ['items']

    @property
    def id(self) -> int:
        """Alias for ``entity_id``"""
        return getattr(self, 'entity_id', None)

    @property
    def number(self) -> str:
        """Alias for ``increment_id``"""
        return getattr(self, 'increment_id', None)

    @cached_property
    def order(self) -> Order:
        """The corresponding :class:`~.Order`"""
        return self.client.orders.by_id(self.order_id)

    @cached_property
    def items(self) -> List[InvoiceItem]:
        """The invoiced items, returned as a list of :class:`InvoiceItem` objects"""
        return [InvoiceItem(item, self) for item in self.__items
                if item['order_item_id'] in self.order.item_ids]


class InvoiceItem(Model):

    """Wraps an item entry of an :class:`Invoice`"""

    DOCUMENTATION = "https://adobe-commerce.redoc.ly/2.3.7-admin/tag/invoicesid"
    IDENTIFIER = 'entity_id'

    def __init__(self, item: dict, invoice: Invoice):
        """Initialize an InvoiceItem of an :class:`Invoice`

        :param item: API response to use as source data
        :param invoice: the :class:`Invoice` that this is an item of
        """
        super().__init__(
            data=item,
            client=invoice.client,
            endpoint=f'invoices/{invoice.id}'
        )
        self.invoice = invoice

    def __repr__(self):
        return f"<InvoiceItem ({self.sku})> from {self.invoice}"

    def data_endpoint(self, scope: Optional[str] = None) -> None:
        """No data endpoint exists for invoice items"""
        return self.logger.info("There is no data endpoint for invoice items")

    def query_endpoint(self) -> None:
        """No search endpoint exists for invoice items"""
        return self.logger.info("There is no search interface for invoice items")

    @property
    def excluded_keys(self) -> List[str]:
        return ['product_id']

    @property
    def order(self) -> Order:
        """The :class:`~.Order` this item is from"""
        return self.invoice.order

    @cached_property
    def order_item(self) -> OrderItem:
        """The item's corresponding :class:`~.OrderItem`"""
        for item in self.order.items:
            if item.item_id == self.order_item_id:
                return item

    @property
    def product(self) -> Product:
        """The item's corresponding simple :class:`~.Product`"""
        return self.order_item.product

    @property
    def product_id(self) -> int:
        """Id of the corresponding simple :class:`~.Product`"""
        return self.order_item.product_id
