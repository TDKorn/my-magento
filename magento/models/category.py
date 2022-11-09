from . import Model


class Category(Model):
    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/categories'

    def __init__(self, data, client):
        super().__init__(
            data=data,
            client=client,
            endpoint='categories'
        )
        self._products = None  # Attributes that are stored after retrieving the first time
        self._subcategories = None

    def __str__(self):
        return f'Magento Category: {self.name}'

    @property
    def excluded_keys(self):
        return []

    @property
    def subcategories(self):
        """Retrieve and temporarily store the category's child categories"""
        if self._subcategories is None:
            if hasattr(self, 'children_data'):
                # children_data: a list of mostly complete subcategory API response dicts
                self._subcategories = [self.parse(child) for child in self.children_data]
            elif hasattr(self, 'children'):
                # children: a comma separated string of subcategory ids; self.subcategory_ids returns them as list
                self._subcategories = [self.query_endpoint().by_id(child_id) for child_id in self.subcategory_ids]
            else:
                self._subcategories = []  # Data comes from those two fields... no subcategories
        return self._subcategories

    @property
    def subcategory_ids(self):
        if hasattr(self, 'children'):
            return self.children.split(',')
        else:
            return [category.id for category in self.subcategories]

    @property
    def subcategory_names(self):
        return [category.name for category in self.subcategories]

    @property
    def products(self):
        if self._products is None:
            endpoint = self.client.url_for(f'categories/{self.id}/products')
            response = self.client.request(endpoint)
            self._products = [product['sku'] for product in response.json()]
        return self._products

    @property
    def all_products(self):
        """Products of the category AND its subcategories"""
        products = self.products.copy()
        for child in self.subcategories:
            if child.name != 'Default Category':
                products.extend(child.products)
        # In case there are products in more than one subcategory
        return set(products)
