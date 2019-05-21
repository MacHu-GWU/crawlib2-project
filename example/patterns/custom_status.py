# -*- coding: utf-8 -*-

from crawlib2 import Status, StatusDetail


class S70_NoWayToFinish(StatusDetail):
    id = 70
    description = "No way to finish!"
    description_en = description
    description_cn = "无法被完成!"


Status.S70_NoWayToFinish = S70_NoWayToFinish

if __name__ == "__main__":
    print(Status.S70_NoWayToFinish.id)
