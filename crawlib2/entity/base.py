# -*- coding: utf-8 -*-

from typing import List, Dict, Set, Optional, Type
import six
import attr
import random
import string
from datetime import datetime
from abc import abstractmethod
from loggerFactory import StreamOnlyLogger
from ..status import Status, FINISHED_STATUS_CODE
from ..util import get_all_subclass


class EntityBase(object):
    logger = StreamOnlyLogger(name="".join(random.sample(string.hexdigits, 16)))

    @classmethod
    def full_classname(cls):
        return cls.__module__ + "." + cls.__name__

    @abstractmethod
    def build_url(self, **kwargs) -> str:
        """
        Build ``url`` endpoint
        """
        raise NotImplementedError

    @abstractmethod
    def build_request(self, url, **kwargs):
        """
        Build Http ``Request`` object
        """
        raise NotImplementedError

    @abstractmethod
    def send_request(self, request, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, url, request, response, **kwargs) -> 'ParseResult':
        """
        Extract data from ``Response`` object

        :param url:
        :param request:
        :param response:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def process_pr(self, pres: 'ParseResult', **kwargs):
        """
        Process Parse Result.

        :type pres: ParseResult
        :param pres:

        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def start(self,
              build_url_kwargs=None,
              build_request_kwargs=None,
              send_request_kwargs=None,
              parse_response_kwargs=None,
              process_pr_kwargs=None):
        # pre process additional kwargs
        if build_url_kwargs is None:
            build_url_kwargs = dict()
        if build_request_kwargs is None:
            build_request_kwargs = dict()
        if send_request_kwargs is None:
            send_request_kwargs = dict()
        if parse_response_kwargs is None:
            parse_response_kwargs = dict()
        if process_pr_kwargs is None:
            process_pr_kwargs = dict()

        url = self.build_url(**build_url_kwargs)
        self.logger.info("sending request to %s" % url)
        request = self.build_request(url, **build_request_kwargs)
        response = self.send_request(request, **send_request_kwargs)
        pres = self.parse_response(url=url, request=request, response=response, **parse_response_kwargs)
        if pres.is_finished():
            self.logger.info("success!")
        else:
            self.logger.info("failed")
        self.process_pr(pres, **process_pr_kwargs)


class EntityExtendScheduler(EntityBase):
    CONF_STATUS_KEY = None  # usually it is "status"
    CONF_EDIT_AT_KEY = None  # usually it is "edit_at"
    CONF_FINISHED_STATUS = FINISHED_STATUS_CODE  # Default 50
    CONF_UPDATE_INTERVAL = 365 * 24 * 60 * 60  # Default 1 Day

    CONF_RELATIONSHIP = None  # type: RelationshipConfig

    @classmethod
    @abstractmethod
    def get_unfinished(cls, **kwargs):
        """
        Execute a query to get all **Not Finished** web page ORM entity
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_finished(cls, **kwargs):
        """
        Execute a query to get all **Finished** web page ORM entity
        """
        raise NotImplementedError

    @classmethod
    def get_all_subclass(cls) -> Set['EntityExtendScheduler']:
        return get_all_subclass(cls)

    @classmethod
    def start_all(cls):
        cls.logger.info("Working on Entity({}) ...".format(cls))
        for entity in cls.get_unfinished():
            entity.start()
        for klass in cls.CONF_RELATIONSHIP.iter_non_recursive_child_class():
            klass.start_all()

    @classmethod
    def validate_implementation_additional(cls):
        """
        Run ORM framework specified implementation validation
        """
        pass

    @classmethod
    def validate_implementation(cls):
        """
        Check if the subclass of :class:`EntityOrm` is correctly implemented.
        """
        if cls.CONF_STATUS_KEY is None:
            raise NotImplementedError("you have to specify `CONF_STATUS_KEY`!")
        if not isinstance(cls.CONF_STATUS_KEY, six.string_types):
            raise TypeError("`CONF_STATUS_KEY` has to be a str!")

        if cls.CONF_EDIT_AT_KEY is None:
            raise NotImplementedError("you have to specify `CONF_EDIT_AT_KEY`!")
        if not isinstance(cls.CONF_EDIT_AT_KEY, six.string_types):
            raise TypeError("`CONF_EDIT_AT_KEY` has to be a str!")

        cls.validate_implementation_additional()

    @classmethod
    def validate_relationship_config(cls):
        """
        Validate ``cls.CONF_RELATIONSHIP``
        """
        subclasses = cls.get_all_subclass()

        for subclass in subclasses:
            if len(subclass.CONF_RELATIONSHIP.mapping) == 0:
                continue

            for klass, relation in subclass.CONF_RELATIONSHIP.mapping.items():
                # all related klass has to be subclass of Entity
                if klass not in subclasses:
                    msg = "`{}` is not subclass of `crawlib2.Entity`".format(
                        klass.full_classname()
                    )
                    raise NotImplementedError(msg)

                # check if "relationship" key exists
                if "relationship" not in relation:
                    msg = "'relationship' key not found!"
                    raise NotImplementedError(msg)

                # check if "relationship" value is valid
                relationship = relation["relationship"]
                if relationship not in ["one", "many"]:
                    msg = "`relationship` has to be one of 'one' or 'many'!"
                    raise NotImplementedError(msg)

                # if it is many relationship, check n_child_key field
                if relationship == "many":
                    if "n_child_key" not in relation:
                        msg = ("You have to define ``{EntitySubclass: "
                               "{'n_child_key': '<a_field_name>'}`` in "
                               "`Entity.CONF_RELATIONSHIP`")
                        raise NotImplementedError(msg)

                    # forget to define `n_child_key` attribute with
                    # ORM column / field
                    n_child_key = relation["n_child_key"]
                    if not hasattr(subclass, n_child_key):
                        msg = "`{}` doesn't define `{}` attribute!".format(
                            subclass.full_classname(), n_child_key
                        )
                        raise NotImplementedError(msg)


class Relationship(object):
    """
    :class:`Relationship` defines crawlable entity relationship.

    Use blog app as example. You want to extract all Post from ListPage.
    Then on ListPage should have many Post. So one ListPage has ``MANY`` Post.

    Then you can define the relationship this way::

        Relationship(child_klass=Post, relationship="many", n_child_key="n_post")

    .. note::

        One crawlable entity may relate to multiple child entity.
        See :class:`RelationshipConfig` for more info.
    """

    class Option(object):
        one = "one"
        many = "many"

    def __init__(self,
                 child_klass: Type[EntityBase],
                 relationship,
                 n_child_key,
                 recursive=True):
        """
        :type child_klass:
        :param child_klass:

        :type relationship: str
        :param relationship:

        :type n_child_key: str
        :param n_child_key:
        """
        if not issubclass(child_klass, EntityBase):
            msg = "'{}' has to be subclass of 'Entity'!".format(child_klass)
            raise TypeError(msg)
        if relationship not in (self.Option.one, self.Option.many):
            msg = "`relationship` has to be one of 'one' or 'many'!"
            raise ValueError(msg)

        self.child_klass = child_klass
        self.relationship = relationship
        self.n_child_key = n_child_key
        self.recursive = recursive


class RelationshipConfig(object):
    def __init__(self, relationship_collection=None):
        """
        :type relationship_collection: List[Relationship]
        :param relationship_collection:
        """
        if relationship_collection is None:
            relationship_collection = list()
        self.relationship_collection = relationship_collection
        self.mapping = dict()  # type: Dict[Type[EntityExtendScheduler], Dict]
        for relationship in relationship_collection:
            self.mapping[relationship.child_klass] = dict(
                relationship=relationship.relationship,
                n_child_key=relationship.n_child_key,
            )

    def get_relationship(self, klass: Type[EntityBase]) -> str:
        """
        Get relationship of the parent Entity to the child Entity.

        :rtype: str
        """
        return self.mapping[klass]["relationship"]

    def get_n_child_key(self, klass: Type[EntityBase]) -> str:

        """
        Get the column / field name that identified how many child it has
        in ORM entity class.

        :type klass: Type[Entity]
        :rtype: str
        """
        return self.mapping[klass]["n_child_key"]

    def __iter__(self):
        return iter(self.mapping)

    def iter_non_recursive_child_class(self):
        for relationship in self.relationship_collection:
            if relationship.recursive:
                yield relationship.child_klass


EntityExtendScheduler.CONF_RELATIONSHIP = RelationshipConfig()


class Entity(EntityExtendScheduler):
    pass


@attr.s
class ParseResult(object):
    """

    :param entity:

    **中文文档**

    :param entity:
    :param children: 从 entity 所对应的 url 页面上抓取下来的其他 entity 实例. 在
        ``Entity.process_pr`` 方法中, 会根据 child entity 的类型进行归类, 然后对
        每类进行处理.
    :param data: 额外的数据
    :param status:
    :param endit_at:
    """
    entity = attr.ib(default=None)  # type: Optional[Entity]
    children = attr.ib(factory=list)  # type: Optional[List[Entity]]
    data = attr.ib(factory=dict)  # type: Dict
    status = attr.ib(
        default=Status.S30_ParseError.id,
        validator=attr.validators.instance_of(int)
    )  # type: int
    edit_at = attr.ib(default=lambda: datetime.utcnow())  # type: datetime

    @entity.validator
    def check_entity(self, attribute, value):
        """
        - :attr:`ParseResult.entity` could be None, it means the SELF entity
            will not be updated.
        - :attr:`ParseResult.entity` should be Any subclass of :class:`Entity`
        """
        if value is not None:
            if not isinstance(value, Entity):
                raise TypeError("ParseResult.entity has to be an Entity")

    @children.validator
    def check_children(self, attribute, value):
        for item in value:
            if not isinstance(item, Entity):
                raise TypeError("ParseResult.children has to be a list of Entity")

    # -- utility methods
    def set_status_todo(self):
        self.status = Status.S0_ToDo.id

    def set_status_url_error(self):
        self.status = Status.S5_UrlError.id

    def set_status_http_error(self):
        self.status = Status.S10_HttpError.id

    def set_status_wrong_page(self):
        self.status = Status.S20_WrongPage.id

    def set_status_decode_error(self):
        self.status = Status.S25_DecodeError.id

    def set_status_parse_error(self):
        self.status = Status.S30_ParseError.id

    def set_status_incomplete_data(self):
        self.status = Status.S40_InCompleteData.id

    def set_status_finished(self):
        self.status = Status.S50_Finished.id

    def set_status_server_side_error(self):
        self.status = Status.S60_ServerSideError.id

    def set_status_finalized(self):
        self.status = Status.S99_Finalized.id

    def is_finished(self):
        """
        test if the status should be marked as `finished`.

        :rtype: bool
        """
        try:
            return self.status >= FINISHED_STATUS_CODE
        except:  # pragma: no cover
            return False
