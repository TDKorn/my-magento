from . import search


class Entity(object):

    def __init__(self, json: {}):
        self.json = json
        self.id = json['entity_id']


class Order(Entity):

    def __init__(self, json: {}):
        super().__init__(json)
        self.number = self.json.get('increment_id', '')
        self.status = self.json.get('status', '')
        self.purchase_date = self.json.get('created_at', '')
        self.raw_billing_address = self.json.get('billing_address')
        self.total_qty_ordered = self.json.get('total_qty_ordered', 0)
        self.item_count = self.json.get('total_item_count', 0)
        self.discount = abs(json.get('base_discount_amount', 0))
        self.discount_desc = self.json.get('discount_description', '')
        self.discount_refund = abs(json.get('base_discount_refunded', 0))
        self.total_paid = self.json.get('total_paid', 0)

    def get_invoice(self) -> {}:
        return search.InvoiceSearch().by_order(self)

    def get_item_attrs(self, attr: str):
        return [getattr(item, attr) for item in self.items]

    def sum_item_attr(self, attr: str):
        return round(sum(self.get_item_attrs(attr)), 2)

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
                self.raw_billing_address.get('street', [''])[0] + ',' +
                self.raw_billing_address.get('city', '') + ',' +
                self.raw_billing_address.get('region_code', '') + ',' +
                self.json.get('postcode', '') + ',' +
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
            'email': self.raw_shipping_address.get('email'),
            'address': self._ship_to_address
        }

    @property
    def _ship_to_address(self) -> str:
        return (
                f"{str(self.raw_shipping_address.get('street', [','])[0])}, " +
                f"{str(self.raw_shipping_address.get('city', ''))}, " +
                f"{str(self.raw_shipping_address.get('region_code', ''))},  {str(self.raw_shipping_address.get('postcode', ''))}, " +
                str(self.raw_shipping_address.get('country_id')).replace('None', '')
        )

    @property
    def payment(self):
        return {
            info['key']: info['value'] for info in self.json.get(
                'extension_attributes', {}).get(
                'payment_additional_info', [{}])
        }

    @property
    def items(self):
        result = []
        for item in self.json.get('items', [{}]):
            if item and not item.get('parent_item'):
                result.append(OrderItem(self, item))
        return result

    @property
    def net_discount(self):
        return self.sum_item_attr('net_discount')

    '''
        Subtotal
        Gross -> sum of price * qty ordered for each item
        Net -> sum of price * (qty ordered - qty refunded - qty cancelled) for each item
    '''

    @property
    def gross_subtotal(self):
        return self.sum_item_attr('gross_subtotal')

    @property
    def net_subtotal(self):
        return self.sum_item_attr('net_subtotal')

    '''
        Taxes
        Gross -> sum of tax on each item irrespective of refunds/cancellations/etc.
        Tax Refund -> sum of tax refunded on each item
        Net Tax -> sum of (tax - tax refund - tax canceled) for each item
    '''

    @property
    def gross_tax(self):
        return self.sum_item_attr('tax_amount')

    @property
    def tax_refund(self):
        return self.sum_item_attr('tax_refund')

    @property
    def net_tax(self):
        return self.sum_item_attr('net_tax')

    '''
        Item Refunds -> sum of (refund amount + tax refund - discount refund) for each item
    '''

    @property
    def item_refunds(self):
        return self.sum_item_attr('total_refund')

    '''
        Gross -> sum of gross subtotal + gross tax - gross discount  for each item
        Net -> sum of net total + net tax - net discount
    '''

    @property
    def gross_total(self):
        return self.sum_item_attr('row_total')

    @property
    def net_total(self):
        return self.sum_item_attr('net_total')


class Invoice(Entity):

    def __init__(self, json: {}):
        super().__init__(json)
        self.billing_address_id = json.get("billing_address_id"),  # int
        self.created = json.get("created_at"),  # "2021-12-01 14:13:11",
        self.discount = json.get("discount_amount"),  # int
        self.currency_code = json.get("global_currency_code")  # str
        self.grand_total = json.get("grand_total"),  # float
        self.comments = json.get("comments"),  # []
        self.increment_id = json.get("increment_id"),  # str
        self.used_for_refund = json.get("is_used_for_refund"),  # int: 1,
        self.items = json.get("items")  # []
