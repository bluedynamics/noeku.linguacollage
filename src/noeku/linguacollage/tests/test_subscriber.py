# -*- coding: utf-8 -*-
from Acquisition import aq_base
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
        ltool.use_cookie_negotiation = 1
        self.collage = api.content.create(
            self.portal,
            type='Collage',
            id='Collage',
            title='EN Collage',
            language='it',
        )

    def _switch_language(self, lang):
        self.layer['request']['LANGUAGE_TOOL'] = None
        self.layer['request']['set_language'] = lang

    def _reset_request(self):
        from noeku.linguacollage.subscriber import _MARK_MODE
        for mode in ['add', 'recursive']:
            mark = _MARK_MODE.format(mode)
            if mark in self.layer['request']:
                self.layer['request'][mark] = False

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
        self._reset_request()
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
        self._reset_request()
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
        self._reset_request()
        d1de = self.portal.d1.addTranslation('de')
        self._reset_request()
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        self._reset_request()
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        self._reset_request()
        alias = api.content.create(
            self.collage['r1']['c1'],
            type='CollageAlias',
            id='a1',
            title='Alias 1'
        )
        alias.set_target(self.portal.d1)
        self._reset_request()
        collage_de = self.collage.addTranslation('de')
        self.assertIn('a1', collage_de['r1']['c1'])

        # switch to de
        self._switch_language('de')

        self.assertIs(
            aq_base(collage_de['r1']['c1']['a1'].get_target()),
            aq_base(d1de)
        )

    def test_add_row_to_existing(self):
        # first translate
        collage_de = self.collage.addTranslation('de')
        self._reset_request()
        # then add a row
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        # now a translated row must exist
        self.assertIn('r1', collage_de)

    def test_add_col_to_existing(self):
        # first translate
        collage_de = self.collage.addTranslation('de')
        self._reset_request()
        # then add a row
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        self._reset_request()
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        # now a translated col must exist
        self.assertIn('c1', collage_de['r1'])

    def test_add_content_to_existing(self):
        collage_de = self.collage.addTranslation('de')
        self._reset_request()
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        self._reset_request()
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        self._reset_request()
        api.content.create(
            self.collage['r1']['c1'],
            type='Document',
            id='d1',
            title='Doc1 1'
        )
        # now a translated doc must exist
        self.assertIn('d1', collage_de['r1']['c1'])

    def test_add_alias_to_existing(self):
        collage_de = self.collage.addTranslation('de')
        self._reset_request()
        api.content.create(
            self.collage,
            type='CollageRow',
            id='r1',
            title='Row 1'
        )
        self._reset_request()
        api.content.create(
            self.collage['r1'],
            type='CollageColumn',
            id='c1',
            title='Col 1'
        )
        self._reset_request()
        # build doc and alias
        doc = api.content.create(
            self.portal,
            type='Document',
            id='d1',
            title='Doc 1',
            language='it',
        )
        self._reset_request()
        d1de = doc.addTranslation('de')
        self._reset_request()
        api.content.create(
            self.collage['r1']['c1'],
            type='CollageAlias',
            id='a1',
            title='Alias 1'
        )
        self.collage['r1']['c1']['a1']
        # now a translated alias must exist
        self.assertIn('a1', collage_de['r1']['c1'])

        self.collage['r1']['c1']['a1'].set_target(self.portal.d1)
        self.assertIs(
            aq_base(self.collage['r1']['c1']['a1'].get_target()),
            aq_base(doc)
        )

        # switch to de
        self._switch_language('de')
        self.assertIs(
            aq_base(self.collage['r1']['c1']['a1'].get_target()),
            aq_base(d1de)
        )
        self.assertIs(
            aq_base(collage_de['r1']['c1']['a1'].get_target()),
            aq_base(d1de)
        )
