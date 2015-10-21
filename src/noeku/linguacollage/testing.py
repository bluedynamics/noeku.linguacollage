# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import noeku.linguacollage


class NoekuLinguacollageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=noeku.linguacollage)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'noeku.linguacollage:default')


NOEKU_LINGUACOLLAGE_FIXTURE = NoekuLinguacollageLayer()


NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NOEKU_LINGUACOLLAGE_FIXTURE,),
    name='NoekuLinguacollageLayer:IntegrationTesting'
)


NOEKU_LINGUACOLLAGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NOEKU_LINGUACOLLAGE_FIXTURE,),
    name='NoekuLinguacollageLayer:FunctionalTesting'
)


NOEKU_LINGUACOLLAGE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        NOEKU_LINGUACOLLAGE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='NoekuLinguacollageLayer:AcceptanceTesting'
)
