# -*- coding: utf-8 -*-
from OFS.ObjectManager import ObjectManager
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import implementer


class IVeryEarlyObjectWillBeDeleted(IObjectEvent):
    pass


@implementer(IVeryEarlyObjectWillBeDeleted)
class VeryEarlyObjectWillBeDeletedEvent(ObjectEvent):
    pass

original_delObject = ObjectManager._delObject


def _patched_delObject(self, id, dp=1, suppress_events=False):

    ob = self._getOb(id)

    if not suppress_events:
        notify(VeryEarlyObjectWillBeDeletedEvent(ob))

    return original_delObject(self, id, dp=dp, suppress_events=suppress_events)

ObjectManager._delObject = _patched_delObject
