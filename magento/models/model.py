from __future__ import annotations
from functools import cached_property
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from magento import clients
import urllib.parse
import inspect

if TYPE_CHECKING:
    from magento.search import SearchQuery


class Model(ABC):
    """The base class for all API response wrapper classes

    **Overview**

    * A :class:`Model` is the object representation of any Magento API response
    * Initialized using the JSON response ``data`` from any API ``endpoint``
    * Most predefined subclasses use an ``endpoint`` that can be searched with criteria
    * Access the corresponding :class:`~magento.search.SearchQuery` object via :meth:`~.query_endpoint`
    """

    def __init__(self, data: dict, client: clients.Client, endpoint: str, private_keys: bool = True):
        """Initialize a :class:`Model` object from an API response and the ``endpoint`` that it came from

        ...

        **NOTE** that the ``endpoint`` is used to:

        * Generate the :meth:`~.url_for` any requests made by subclass-specific methods
        * Match the :class:`Model` to its corresponding :class:`~magento.search.SearchQuery` object,
          which is returned by :meth:`~.query_endpoint`
        * Determine how to :meth:`~Model.parse` new :class:`Model` objects from API responses

        ...

        :param data: the JSON from an API response to use as source data
        :param client: an initialized :class:`~.Client`
        :param endpoint: the base API endpoint that the :class:`Model` represents
        :param private_keys: if set to True, will set the keys in the :attr:`~.excluded_keys` as private attributes
            (prefixed with ``__``) instead of fully excluding them

        """
        if not isinstance(data, dict):
            raise TypeError(f'Parameter "data" must be of type {dict}')
        if not isinstance(endpoint, str):
            raise TypeError(f'Parameter "endpoint" must be of type {str}')
        if not isinstance(client, clients.Client):
            raise TypeError(f'Parameter "client" must be of type {clients.Client}')

        self.data = data
        self.client = client
        self.endpoint = endpoint
        self.logger = client.logger
        self.set_attrs(data, private_keys=private_keys)

    def set_attrs(self, data: dict, private_keys: bool = True) -> None:
        """Initializes object attributes using the JSON from an API response as the data source

        Called at the time of object initialization, but can also be used to update the source data and
        reinitialize the attributes without creating a new object

        :param data: the API response JSON to use as the object source data
        :param private_keys: if set to True, will set the :attr:`~.excluded_keys` as private attributes
            (prefixed with ``__``) instead of fully excluding them

        **Private Keys Clarification**

        Let's say that ``"status"`` is in the :attr:`~.excluded_keys`

        * No matter what, the :class:`Model` object will not have a ``status`` attribute set
        * If ``private_keys=True``, it **will** have a ``__status`` attribute set though
        * If ``private_keys=False``, then the attribute/key is completely excluded
        """
        keys = set(data) - set(self.excluded_keys)
        for key in keys:
            if key == 'custom_attributes':
                if attrs := data[key]:
                    setattr(self, key, self.unpack_attributes(attrs))
            else:
                setattr(self, key, data[key])

        if private_keys:
            private = '_' + self.__class__.__name__ + '__'
            for key in self.excluded_keys:
                setattr(self, private + key, data.get(key))

        self.data = data

    @property
    @abstractmethod
    def excluded_keys(self) -> list[str]:
        """API response keys that shouldn't be set as object attributes by :meth:`~.set_attrs`

        :returns: list of API response keys that shouldn't be set as attributes
        """
        pass

    def query_endpoint(self) -> SearchQuery:
        """Initializes and returns the :class:`~.SearchQuery` object corresponding to the Model's ``endpoint``

        :returns: a :class:`~.SearchQuery` or subclass, depending on the ``endpoint``
        :rtype: :class:`~.SearchQuery`
        """
        return self.client.search(self.endpoint)

    def parse(self, response: dict) -> Model:
        """Uses the instance's corresponding :class:`~.SearchQuery` to parse an API response

        :param response: JSON dictionary from the API to use as source data
        :return: a :class:`~.Model` object, initialized using the ``response`` as the source data
        :rtype: :class:`~.Model` with the same ``endpoint`` as the calling instance
        """
        return self.query_endpoint().parse(response)

    @staticmethod
    def unpack_attributes(attributes: list[dict], key: str = 'attribute_code') -> dict:
        """Unpacks a list of attribute dictionaries into a single dictionary

        **Example**::

               >>> custom_attrs = [{'attribute_code': 'attr', 'value': 'val'},{'attribute_code': 'will_to_live', 'value': '0'}]
               >>> print(Model.unpack_attributes(custom_attrs))

               {'attr': 'val', 'will_to_live': '0'}

        :param attributes: a list of custom attribute dictionaries
        :param key: the key used in the attribute dictionary (ex. ``attribute_code`` or ``label``)
        :returns: a single dictionary of all custom attributes formatted as ``{"attr": "val"}``
        """
        return {attr[key]: attr['value'] for attr in attributes}

    @staticmethod
    def pack_attributes(attribute_data: dict, key: str = 'attribute_code') -> list[dict]:
        """Packs a dictionary containing attributes into a list of attribute dictionaries

        **Example**::

               >>> attribute_data = {'special_price': 12, 'meta_title': 'My Product'}
               >>> print(Model.pack_attributes(attribute_data))
               >>> print(Model.pack_attributes(attribute_data, key='label'))

               [{'attribute_code': 'special_price', 'value': 12}, {'attribute_code': 'meta_title', 'value': 'My Product'}]
               [{'label': 'special_price', 'value': 12}, {'label': 'meta_title', 'value': 'My Product'}]

        :param attribute_data: a dictionary containing attribute data
        :param key: the key to use when packing the attributes (ex. ``attribute_code`` or ``label``)
        :returns: a list of dictionaries formatted as ``{ key : "attr", value: "value"}``
        """
        return [{key: attr, "value": val} for attr, val in attribute_data.items()]

    @staticmethod
    def encode(string: str) -> str:
        """URL-encode with :mod:`urllib`; used for requests that could contain special characters

        :param string: the string to URL-encode
        """
        return urllib.parse.quote_plus(string)

    @cached_property
    def cached(self) -> list[str]:
        """Names of properties that are wrapped with :class:`~functools.cached_property`"""
        return [member for member, val in inspect.getmembers(self.__class__) if
                isinstance(val, cached_property) and member != 'cached']

    def clear(self, *keys: str) -> None:
        """Deletes the provided keys from the object's :attr:`__dict__`

        To clear all cached properties::

            >> self.clear(*self.cached)

        :param keys: name of the object attribute(s) to delete
        """
        for key in keys:
            self.__dict__.pop(key, None)
        self.logger.debug(f'Cleared {keys} from {self}')


class APIResponse(Model):

    def __init__(self, data: dict, client: clients.Client, endpoint: str):
        """A generic :class:`Model` class

         Used to wrap API Responses when there isn't a :class:`Model` subclass defined for the endpoint

        :param data: the API response from an API endpoint
        :param client: an initialized :class:`~.Client` object
        :param endpoint: the endpoint that the API response came from
        """
        super().__init__(
            data=data,
            client=client,
            endpoint=endpoint,
            private_keys=False
        )

    @property
    def excluded_keys(self) -> list[str]:
        return []
