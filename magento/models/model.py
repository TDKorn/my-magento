from __future__ import annotations
from functools import cached_property
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Optional, List
from magento import clients
import urllib.parse
import inspect

if TYPE_CHECKING:
    from magento.search import SearchQuery


class Model(ABC):

    """The abstract base class of all API response wrapper classes

    **Overview**

    * A :class:`Model` wraps the response ``data`` from an API ``endpoint``
    * Several endpoints have subclasses with additional methods to retrieve/update data
    * All other endpoints are wrapped using a general :class:`~.APIResponse`
    * The endpoint's corresponding :class:`~.SearchQuery` can be accessed via :meth:`~.query_endpoint`
    """

    DOCUMENTATION: str = None  #: Link to the Official Magento 2 API documentation for the endpoint wrapped by the Model
    IDENTIFIER: str = None  #: The API response field that the endpoint's :attr:`~.Model.uid` comes from

    def __init__(self, data: dict, client: clients.Client, endpoint: str, private_keys: bool = True):
        """Initialize a :class:`Model` object from an API response and the ``endpoint`` that it came from

        ...

        .. tip:: The ``endpoint`` is used to:

           * Generate the :meth:`~.url_for` any requests made by subclass-specific methods
           * Match the :class:`~.Model` to its corresponding :class:`~.SearchQuery` object
           * Determine how to :meth:`~.Model.parse` new :class:`~.Model` objects from API responses

        ...

        :param data: the JSON from an API response to use as source data
        :param client: an initialized :class:`~.Client`
        :param endpoint: the API endpoint that the :class:`Model` wraps
        :param private_keys: if ``True``, sets the keys in the :attr:`~.excluded_keys` as private attributes
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

        .. admonition:: **Private Keys Clarification**
           :class: info

           Let's say that ``"status"`` is in the :attr:`~.excluded_keys`

           * No matter what, the ``status`` attribute will not be set on the :class:`Model`
           * If ``private_keys==True``, the ``__status`` attribute will be set (using the ``status`` data)
           * If ``private_keys==False``, the data from ``status`` is completely excluded
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
    def excluded_keys(self) -> List[str]:
        """API response keys that shouldn't be set as object attributes by :meth:`~.set_attrs`

        :returns: list of API response keys that shouldn't be set as attributes
        """
        pass

    @property
    def uid(self) -> Union[str, int]:
        """Unique item identifier; used in the url of the :meth:`~.Model.data_endpoint`"""
        return self.data.get(self.IDENTIFIER)

    def data_endpoint(self, scope: Optional[str] = None) -> str:
        """Endpoint to use when requesting/updating the item's data

        :param scope: the scope to generate the :meth:`~.url_for`
        """
        return self.client.url_for(f'{self.endpoint}/{self.uid}', scope)

    def query_endpoint(self) -> SearchQuery:
        """Initializes and returns the :class:`~.SearchQuery` object corresponding to the Model's ``endpoint``

        :returns: a :class:`~.SearchQuery` or subclass, depending on the ``endpoint``
        """
        return self.client.search(self.endpoint)

    def parse(self, response: dict) -> Model:
        """Uses the instance's corresponding :class:`~.SearchQuery` to parse an API response

        :param response: API response dict to use as source data
        :returns: a :class:`~.Model` with the same ``endpoint`` as the calling instance
        """
        return self.query_endpoint().parse(response)

    def refresh(self, scope: Optional[str] = None) -> bool:
        """Updates object attributes in place using current data from the :meth:`~.data_endpoint`

        .. hint:: :meth:`~.refresh` can be used to switch the scope of the source data
           without creating a new object or changing the :attr:`.Client.scope`

           .. admonition:: Example
              :class: example

              ::

                # Get product data on 'default' scope
                >>> product = client.products.by_sku('sku42')
                # Get fresh product data from different scope
                >>> product.refresh('all')

                Refreshed <Magento Product: sku42> on scope all

        :param scope: the scope to send the request on; uses the :attr:`.Client.scope` if not provided
        """
        url = self.data_endpoint(scope)
        response = self.client.get(url)

        if response.ok:
            self.clear(*self.cached)
            self.set_attrs(response.json())
            self.logger.info(
                f"Refreshed {self} on scope {self.get_scope_name(scope)}"
            )
            return True
        else:
            self.logger.error(  # Actual error message is logged by client
                f"Failed to refresh {self} on scope {self.get_scope_name(scope)}"
            )
            return False

    @staticmethod
    def unpack_attributes(attributes: List[dict], key: str = 'attribute_code') -> dict:
        """Unpacks a list of attribute dictionaries into a single dictionary

        .. admonition:: Example
           :class: example

           ::

            >> custom_attrs = [{'attribute_code': 'attr', 'value': 'val'},{'attribute_code': 'will_to_live', 'value': '0'}]
            >> print(Model.unpack_attributes(custom_attrs))

            {'attr': 'val', 'will_to_live': '0'}

        :param attributes: a list of custom attribute dictionaries
        :param key: the key used in the attribute dictionary (ex. ``attribute_code`` or ``label``)
        :returns: a single dictionary of all custom attributes formatted as ``{"attr": "val"}``
        """
        return {attr[key]: attr['value'] for attr in attributes}

    @staticmethod
    def pack_attributes(attribute_data: dict, key: str = 'attribute_code') -> List[dict]:
        """Packs a dictionary containing attributes into a list of attribute dictionaries

        .. admonition:: **Example**
           :class: example

           ::

            >> attribute_data = {'special_price': 12, 'meta_title': 'My Product'}
            >> print(Model.pack_attributes(attribute_data))
            >> print(Model.pack_attributes(attribute_data, key='label'))

            [{'attribute_code': 'special_price', 'value': 12}, {'attribute_code': 'meta_title', 'value': 'My Product'}]
            [{'label': 'special_price', 'value': 12}, {'label': 'meta_title', 'value': 'My Product'}]


        :param attribute_data: a dictionary containing attribute data
        :param key: the key to use when packing the attributes (ex. ``attribute_code`` or ``label``)
        :returns: a list of dictionaries formatted as ``{key : "attr", "value": "value"}``
        """
        return [{key: attr, "value": val} for attr, val in attribute_data.items()]

    @staticmethod
    def encode(string: str) -> str:
        """URL-encode with :mod:`urllib.parse`; used for requests that could contain special characters

        :param string: the string to URL-encode
        """
        if urllib.parse.unquote_plus(string) != string:
            return string  # Already encoded
        return urllib.parse.quote_plus(string)

    @cached_property
    def cached(self) -> List[str]:
        """Names of properties that are wrapped with :func:`functools.cached_property`"""
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

    def get_scope_name(self, scope: str) -> str:
        """Returns the appropriate scope name to use for logging messages"""
        return scope or 'default' if scope is not None else self.client.scope or 'default'


class APIResponse(Model):

    IDENTIFIER = 'entity_id'  # Most endpoints use this field

    def __init__(self, data: dict, client: clients.Client, endpoint: str):
        """A generic :class:`Model` subclass

        Wraps API responses when there isn't a :class:`Model` subclass defined for the ``endpoint``

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
    def excluded_keys(self) -> List[str]:
        return []

    def data_endpoint(self, scope: Optional[str] = None) -> Optional[str]:
        if self.uid:
            return super().data_endpoint(scope)
        else:
            self.logger.info('No uid found - unable to determine the data endpoint url')

    @property
    def uid(self) -> Optional[int]:
        """Unique item identifier

        .. note:: Since the :class:`~.APIResponse` can wrap any endpoint, the response
           is checked for commonly used id fields (``entity_id`` and ``id``)

           If the endpoint doesn't use those fields, ``None`` will be returned
        """
        if not (uid := super().uid):
            uid = self.data.get('id', None)
        return uid
