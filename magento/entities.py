from __future__ import annotations
from .utils import ItemManager
from . import clients


class Entity:

    def __init__(self, json: {}):
        self.json = json
        self.id = json['entity_id']


class Order(Entity):

    def __init__(self, json: {}, client: clients.Client):
        super().__init__(json)
        self.client = client
        self.item_manager = OrderItemManager(self)

        self.status = self.json.get('status', '')
        self.number = self.json.get('increment_id', '')
        self.created_at = self.json.get('created_at', '')
        self.updated_at = self.json.get('updated_at','')
        self.raw_billing_address = self.json.get('billing_address', {})

        self.items = self.item_manager.items
        self.item_count = self.json.get('total_item_count', 0)
        self.total_qty_ordered = self.json.get('total_qty_ordered', 0)
        self.total_qty_invoiced = self.item_manager.qty_invoiced
        self.total_qty_shipped = self.item_manager.qty_shipped
        self.total_qty_refunded = self.item_manager.qty_refunded
        self.total_qty_canceled = self.item_manager.qty_canceled

        self.subtotal = self.json.get('subtotal', 0)
        self.subtotal_refunded = abs(self.json.get('subtotal_refunded', 0))
        self.subtotal_canceled = abs(self.json.get('subtotal_canceled', 0))

        self.tax = self.json.get('tax_amount', 0)
        self.tax_refunded = abs(self.json.get('tax_refunded', 0))
        self.tax_canceled = abs(self.json.get('tax_canceled', 0))

        self.shipping = self.json.get('shipping_amount', 0)
        self.shipping_tax = self.json.get('shipping_tax_amount', 0)
        self.shipping_discount = abs(self.json.get('shipping_discount_amount', 0))
        self.shipping_refunded = abs(self.json.get('shipping_refunded', 0))
        self.shipping_tax_refunded = abs(self.json.get('shipping_tax_refunded', 0))
        self.shipping_canceled = abs(self.json.get('shipping_canceled', 0))
        self.shipping_desc = self.json.get('shipping_description', '')

        self.discount = abs(self.json.get('discount_amount', 0))
        self.discount_refund = abs(json.get('discount_refunded', 0))
        self.discount_canceled = abs(json.get('discount_canceled', 0))
        self.discount_desc = self.json.get('discount_description', '')

        self.gross_total = self.payment.get('amount_ordered', 0)
        self.total_paid = self.payment.get('amount_paid', 0)

        self.total_refund = abs(self.json.get('total_refunded', 0))  # Includes adjustment refund, tax refund, discount refund, shipping refund
        self.total_canceled = abs(self.json.get('total_canceled', 0))
        self.adjustment_positive = abs(self.json.get('base_adjustment_positive', 0))

    def __str__(self):
        return "Order Number " + self.number + " placed on " + self.created_at

    def get_invoice(self) -> {}:
        return self.client.invoices.by_order(self)

    @property
    def bill_to(self) -> {}:
        return {
            'firstname': self.raw_billing_address.get('firstname', ''),
            'lastname': self.raw_billing_address.get('lastname', ''),
            'email': self.raw_billing_address.get('email'),
            'address': self._bill_to_address
        }

    @property
    def _bill_to_address(self):
        address = (
                ' '.join(self.raw_billing_address.get('street', [''])) + ',' +
                self.raw_billing_address.get('city', '') + ',' +
                self.raw_billing_address.get('region_code', '') + ',' +
                self.raw_billing_address.get('postcode', '') + ',' +
                self.raw_billing_address.get('country_id', '').replace('None', '')
        )
        return ', '.join(component for component in address.split(',') if component)

    @property
    def raw_shipping_address(self) -> {}:
        return self.json.get('extension_attributes',
                             {}).get('shipping_assignments',
                                     [{}])[0].get('shipping',
                                                  {}).get('address',
                                                          {})

    @property
    def ship_to(self) -> {}:
        return {
            'firstname': self.raw_shipping_address.get('firstname', ''),
            'lastname': self.raw_shipping_address.get('lastname', ''),
            'email': self.raw_shipping_address.get('email', ''),
            'address': self._ship_to_address
        }

    @property
    def _ship_to_address(self) -> str:
        address = (
                ' '.join(self.raw_shipping_address.get('street', [''])) + ',' +
                self.raw_shipping_address.get('city', '') + ',' +
                self.raw_shipping_address.get('region_code', '') + ',' +
                self.raw_shipping_address.get('postcode', '') + ',' +
                self.raw_shipping_address.get('country_id', '').replace('None', '')
        )
        return ', '.join(component for component in address.split(',') if component)

    @property
    def payment(self) -> {}:
        payment = self.json.get('payment', {}).copy()
        payment.pop('additional_information', -1)
        payment.update(self._payment_additional_info())
        return payment

    def _payment_additional_info(self) -> {}:
        additional_info = self.json.get('extension_attributes', {}).get('payment_additional_info', [{}])
        return {info['key']: info['value'] for info in additional_info if info}

    @property
    def net_total(self):
        return self.gross_total - self.total_refund - self.total_canceled

    @property
    def grand_total(self):
        # For consistency
        return self.net_total

    @property
    def net_tax(self):
        return self.tax - self.tax_canceled - self.tax_refunded

    @property
    def net_shipping(self):
        shipping_cost = self.shipping + self.shipping_tax
        shipping_deductions = self.shipping_canceled + self.shipping_discount + self.shipping_refunded + self.shipping_tax_refunded
        return shipping_cost - shipping_deductions

    @property
    def item_refunds(self):
        return self.total_refund - self.adjustment_positive


class OrderItem(object):

    def __init__(self, order, item):
        self.json = item
        self.order = order
        self.sku = item.get('sku', '')
        self.name = item.get('name', '')
        self.order_id = item.get('order_id', 0)
        self.product_id = item.get('product_id', 0)
        self.price = item.get('price', 0)
        self.qty_ordered = item.get('qty_ordered', 0)
        self.qty_invoiced = item.get('qty_invoiced', 0)
        self.qty_shipped = item.get('qty_shipped', 0)
        self.qty_canceled = item.get('qty_canceled', 0)
        self.qty_refunded = item.get('qty_refunded', 0)

        self.base_refund = abs(item.get('amount_refunded', 0))
        self.tax = item.get('tax_amount', 0)
        self.tax_percent = item.get('tax_percent', 0)
        self.tax_refund = abs(item.get('tax_refunded', 0))
        self.tax_canceled = abs(item.get('tax_canceled', 0))
        self.discount = abs(item.get('discount_amount', 0))
        self.discount_invoiced = abs(item.get('discount_invoiced', 0))
        self.discount_refund = abs(item.get('discount_refunded', 0))
        self.row_total = item.get('row_total_incl_tax', 0)

    @property
    def qty_outstanding(self):
        """Number of unshipped units"""
        return self.qty_ordered - self.qty_shipped - self.qty_refunded - self.qty_canceled

    @property
    def gross_subtotal(self):
        return self.price * self.qty_ordered

    @property
    def net_qty(self):
        return self.qty_ordered - self.qty_refunded - self.qty_canceled

    @property
    def net_subtotal(self):
        return self.net_qty * self.price

    @property
    def net_tax(self):
        return self.tax - self.tax_refund - self.tax_canceled

    @property
    def net_discount(self):
        """The final discount amount of the OrderItem, after cancellations and refunds are taken into account."""
        # If discount_invoiced is 0, there's either (1) no discount or (2) a discount but the order is cancelled
        if self.discount_invoiced == 0:
            # If there's no discount, or there's a discount but the order is cancelled, then the net discount is 0
            if self.discount == 0 or self.qty_canceled != 0:
                return 0
        # Otherwise, there's a discount and the order hasn't been cancelled. However, it may be partially/fully refunded
        return self.discount - self.discount_refund

    @property
    def total_refund(self):
        return self.base_refund + self.tax_refund - self.discount_refund

    @property
    def total_canceled(self):
        """Partial cancellation isn't possible, so if there's a cancellation, it'll be equal to the total order value"""
        if self.qty_canceled != 0:
            return self.row_total
        return 0

    @property
    def grand_total(self):
        return self.row_total - self.total_canceled - self.total_refund


class OrderItemManager(ItemManager):

    def __init__(self, order: Order):
        super().__init__()
        self.order = order
        self.find_order_items()

    def find_order_items(self):
        for item in self.order.json.get('items', [{}]):
            if item.get('parent_item') is None:
                self.add(OrderItem(self.order, item))

    @property
    def qty_ordered(self):
        return self.sum_attrs('qty_ordered')

    @property
    def qty_invoiced(self):
        return self.sum_attrs('qty_invoiced')

    @property
    def qty_shipped(self):
        return self.sum_attrs('qty_shipped')

    @property
    def qty_canceled(self):
        return self.sum_attrs('qty_canceled')

    @property
    def qty_refunded(self):
        return self.sum_attrs('qty_refunded')

    @property
    def net_qty_ordered(self):
        return self.sum_attrs('net_qty')

    @property
    def gross_discount(self):
        """Sum of discounts on all items irrespective of payment/refunds/cancellations"""
        return self.sum_attrs('discount')

    @property
    def discount_refund(self):
        return self.sum_attrs('discount_refund')

    @property
    def net_discount(self):
        """Sum of discounts on all items after refunds/cancellations"""
        return self.sum_attrs('net_discount')

    @property
    def gross_subtotal(self):
        return self.sum_attrs('gross_subtotal')

    @property
    def net_subtotal(self):
        return self.sum_attrs('net_subtotal')

    @property
    def gross_tax(self):
        return self.sum_attrs('tax')

    @property
    def tax_refund(self):
        return self.sum_attrs('tax_refund')

    @property
    def net_tax(self):
        return self.sum_attrs('net_tax')

    @property
    def total_refund(self):
        return self.sum_attrs('total_refund')

    @property
    def gross_total(self):
        return self.sum_attrs('row_total')

    @property
    def grand_total(self):
        """Grand total of each item in the order (net amount after refunds/cancellations/discounts)"""
        return self.sum_attrs('grand_total')


class Invoice(Entity):

    def __init__(self, json: {}, client):
        super().__init__(json)
        self.client = client
        self.billing_address_id = json.get("billing_address_id", 0)
        self.comments = json.get("comments", [])
        self.created = json.get("created_at", ''),
        self.currency_code = json.get("global_currency_code", '')
        self.discount = json.get("discount_amount", 0)
        self.subtotal = json.get('subtotal', 0)
        self.tax = json.get('tax_amount', 0)
        self.total_qty = json.get('total_qty', 0)
        self.grand_total = json.get("grand_total", 0)
        self.number = json.get("increment_id", '')
        self.used_for_refund = json.get("is_used_for_refund")
        self.items = json.get("items", [])


class InvoiceItem(Entity):

    def __init__(self, item, client):
        super().__init__(item)
        self.json = item
        self.client = client
        self.sku = item.get('sku', '')
        self.name = item.get('name', '')
        self.price = item.get('price', 0)
        self.qty = item.get('qty', 0)
        self.subtotal = item.get('row_total', 0)
        self.tax = item.get('tax_amount', 0)
        self.grand_total = item.get('row_total_incl_tax', 0)

        self.order_item_id = item.get('order_item_id', 0)
        self.product_id = item.get('product_id', 0)
        self.parent_id = item.get('parent_id', 0)

    def get_order_item(self):
        return self.client.search('orders/items').add_criteria(field='item_id',
                                                               value=self.order_item_id).execute()

    def get_product(self):
        return self.client.products.add_criteria(field='product_id',
                                                 value=self.product_id).execute()

