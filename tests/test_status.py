# -*- coding: utf-8 -*-

import pytest
from crawlib2.status import Status


class TestStatus(object):
    def test(self):
        assert Status.S0_ToDo.id == 0
        assert Status.S50_Finished == 50
        assert Status.S99_Finalized == 99


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
