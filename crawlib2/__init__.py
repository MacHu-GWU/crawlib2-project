# -*- coding: utf-8 -*-

"""
Package Description.
"""


from ._version import __version__

__short_description__ = "Package short description."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"


try:
    from .status import Status, StatusDetail
except ImportError as e:
    pass

try:
    from .middleware.url_builder import BaseUrlBuilder
except ImportError:
    pass