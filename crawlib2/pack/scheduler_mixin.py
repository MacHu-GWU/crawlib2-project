# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class SchedulerMixin(object):
    _settings_STATUS_KEY_required = None
    _settings_EDIT_AT_KEY_required = None
    _settings_FINISHED_STATUS_required = None
    _settings_UPDATE_INTERVAL_required = 365 * 24 * 60 * 60

    @classmethod
    def get_all_unfinished(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_all_finished(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def validate_implementation(cls, *args, **kwargs):
        raise NotImplementedError