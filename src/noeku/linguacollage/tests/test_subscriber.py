# -*- coding: utf-8 -*-
from noeku.linguacollage.testing import NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
import unittest


class TestSetup(unittest.TestCase):
    """Test that noeku.linguacollage is properly installed."""

    layer = NOEKU_LINGUACOLLAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        ltool = self.portal.portal_languages
        ltool.start_neutral = 0
        ltool.addSupportedLanguage('de')
        ltool.addSupportedLanguage('it')
        self.collage = api.content.create(
            self.portal,
            type='Collage',
            id='Collage',
            title='EN Collage',
            language='it',
        )

    def test_recursive_translate_collage_with_rows(self):
        api.content.create(
            self.collage,
            type='CollageRow',
            id='1',
            title='Row 1'
        )
        api.content.create(
            self.collage,
            type='CollageRow',
            id='2',
            title='Row 2'
        )
        collage_de = self.collage.addTranslation('de')
        self.assertIn('1', collage_de)
        self.assertIn('2', collage_de)

    def test_recursive_translate_collage_with_cols(self):
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c2',
            title='Col 2'
        )
        collage_de = self.collage.addTranslation('de')
        self.assertIn('c1', collage_de['r1'])
        self.assertIn('c2', collage_de['r1'])

    def test_recursive_translate_collage_with_alias(self):
        api.content.create(
            self.portal,
            type='Document',
            id='d1',
            title='Doc 1',
            language='it',
        )
        self.portal.d1.addTranslation('de')
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        alias = api.content.create(
            self.collage['r1']['c1'],
            type='CollageAlias',
            id='a1',
            title='Alias 1'
        )
        alias.set_target(self.portal.d1)
        collage_de = self.collage.addTranslation('de')
        self.assertIn('a1', collage_de['r1']['c1'])
