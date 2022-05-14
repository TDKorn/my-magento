# Everything without entity_id
import magento


class Product:
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    def __init__(self, data: {}, client: magento.Client):
        if not isinstance(data, dict) or not isinstance(client, magento.Client):
            raise ValueError

        self.client = client
        for attr in data:
            if attr == 'custom_attributes':
                # Unpack list of custom attribute dicts into a single dict
                custom_attrs = {
                    attr['attribute_code']: attr['value']
                    for attr in data[attr]
                }
                setattr(self, attr, custom_attrs)
            else:
                setattr(self, attr, data[attr])

    @property
    def stock(self):
        if hasattr(self, 'extension_attributes'):
            return self.extension_attributes.get(
                'stock_item', {}).get(
                'qty', None
            )

