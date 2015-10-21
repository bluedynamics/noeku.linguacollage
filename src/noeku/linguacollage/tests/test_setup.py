# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from noeku.linguacollage.testing import NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that noeku.linguacollage is properly installed."""

    layer = NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if noeku.linguacollage is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'noeku.linguacollage'))

    def test_browserlayer(self):
        """Test that INoekuLinguacollageLayer is registered."""
        from noeku.linguacollage.interfaces import (
            INoekuLinguacollageLayer)
        from plone.browserlayer import utils
        self.assertIn(INoekuLinguacollageLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['noeku.linguacollage'])

    def test_product_uninstalled(self):
        """Test if noeku.linguacollage is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'noeku.linguacollage'))
