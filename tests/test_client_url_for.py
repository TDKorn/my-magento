# magento/tests/test_client_url_for.py
import os
import unittest
from magento import Client


domain = os.getenv('MAGENTO_DOMAIN')
user = os.getenv('MAGENTO_USERNAME')
pw = os.getenv('MAGENTO_PASSWORD')


class TestLocalClientUrlFor(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        self.api = Client(domain, user, pw, local=True, login=False)

    def test_base_url(self):
        self.assertEqual(self.api.BASE_URL, f'http://{domain}/rest/V1/')

    def test_url_for_none_none(self):
        self.api.scope = None
        self.assertEqual(self.api.url_for('products'), f'http://{domain}/rest/V1/products')

    def test_url_for_none_null(self):
        self.api.scope = None
        self.assertEqual(self.api.url_for('products', ""), f'http://{domain}/rest/V1/products')
        self.assertEqual(self.api.scope, None)

    def test_url_for_none_scope(self):
        self.api.scope = None
        self.assertEqual(self.api.url_for('products', "en"), f'http://{domain}/rest/en/V1/products')
        self.assertEqual(self.api.scope, None)

    def test_url_for_null_none(self):
        self.api.scope = ""
        self.assertEqual(self.api.url_for('products'), f'http://{domain}/rest/V1/products')

    def test_url_for_null_null(self):
        self.api.scope = ""
        self.assertEqual(self.api.url_for('products', ""), f'http://{domain}/rest/V1/products')

    def test_url_for_null_scope(self):
        self.api.scope = ""
        self.assertEqual(self.api.url_for('products', "en"), f'http://{domain}/rest/en/V1/products')
        self.assertEqual(self.api.scope, "")

    def test_url_for_scope_none(self):
        self.api.scope = "en"
        self.assertEqual(self.api.url_for('products'), f'http://{domain}/rest/en/V1/products')

    def test_url_for_scope_null(self):
        self.api.scope = "en"
        self.assertEqual(self.api.url_for('products', ""), f'http://{domain}/rest/V1/products')
        self.assertEqual(self.api.scope, "en")

    def test_url_for_scope_scope(self):
        self.api.scope = "en"
        self.assertEqual(self.api.url_for('products', "fr"), f'http://{domain}/rest/fr/V1/products')
        self.assertEqual(self.api.scope, "en")


if __name__ == '__main__':
    unittest.main()
