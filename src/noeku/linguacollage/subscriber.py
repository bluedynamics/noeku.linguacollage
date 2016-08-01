# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Acquisition import aq_base
from Products.Collage import interfaces as collageifaces
from Products.statusmessages.interfaces import IStatusMessage
import logging


logger = logging.getLogger(__name__)


def _log(msg):
    logger.log(logging.INFO, msg)


def _marked(context, marker):
    mark = '__noekulinguacollage_{0}__'.format(marker)
    req = context.REQUEST
    if req.get(mark, False):
        return True
    req.set(mark, True)
    return False


_MARK_MODE = '__noekulinguacollage_{0}__'


def _set_mode(context, mode):
    req = context.REQUEST
    req.set(_MARK_MODE.format(mode), True)


def _is_mode_set(context, mode):
    req = context.REQUEST
    return req.get(_MARK_MODE.format(mode), False)


def translate_collage_recursivly(context, event):
    """Event handler on translate of a collage.

    - Iterates over all contained rows and translates them.
    """
    __traceback_info__ = 'Target-Language: {0}, context: {1}'.format(
        event.language,
        '/'.join(context.getPhysicalPath()),
    )
    if not collageifaces.ICollage.providedBy(context):
        return
    if _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'recursive')
    canonical = context.getCanonical()
    _log('recursive translate collage {0}'.format(
        '/'.join(context.getPhysicalPath())
    ))
    for rowid in canonical.contentIds():
        row = context[rowid]
        if row.hasTranslation(event.language):
            # already translated in target language
            # this happends in rare case one translates a row manually
            continue
        row.addTranslation(event.language)


def translate_row_recursivly(context, event):
    """Event handler on translate of a row.

    - Iterates over all contained cols and translates them.
    """
    __traceback_info__ = 'Target-Language: {0}, context: {1}'.format(
        event.language,
        '/'.join(context.getPhysicalPath()),
    )
    if not collageifaces.ICollageRow.providedBy(context):
        return
    if _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'recursive')
    canonical = context.getCanonical()
    _log('recursive translate collage row {0}'.format(
        '/'.join(context.getPhysicalPath())
    ))
    for colid in canonical.contentIds():
        col = context[colid]
        if col.hasTranslation(event.language):
            # already translated in target language
            # this happends in rare case one translates a col manually
            continue
        col.addTranslation(event.language)


def translate_col_recursivly(context, event):
    """Event handler on translate of a column.

    - Iterates over all contained content and translates it.
    - fails if an untranslated alias target exists
    """
    __traceback_info__ = 'Target-Language: {0}, context: {1}'.format(
        event.language,
        '/'.join(context.getPhysicalPath()),
    )
    if not collageifaces.ICollageColumn.providedBy(context):
        return
    if _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'recursive')
    canonical = context.getCanonical()
    _log('recursive translate collage column {0}'.format(
        '/'.join(context.getPhysicalPath())
    ))
    for contentid in canonical.contentIds():
        content = context[contentid]
        if content.hasTranslation(event.language):
            # already translated in target language
            # this happends in rare case one translates a content manually
            continue
        if collageifaces.ICollageAlias.providedBy(content):
            # check if alias target is translated, otherwise fail.
            target = content.get_target()
            if target is None:
                raise ValueError(
                    'Alias without target {0}'.format(
                        content.absolute_url()
                    )
                )
            elif not target.hasTranslation(event.language):
                msg = 'Der verknüpfte Alias <a href="{0}">{1}</a> wurde noch nicht übersetzt.'.format(
                    target.absolute_url(), target.absolute_url()
                )
                IStatusMessage(context.REQUEST).addStatusMessage(msg, type='warn')
        content.addTranslation(event.language)


def added_row(context, event):
    """Event handler on create of a new row

    - creates translations of itself at the right place in all
      translations of its parent collage
    """
    __traceback_info__ = 'Language: {0}, context: {1}'.format(
        context.Language(),
        '/'.join(context.getPhysicalPath()),
    )
    if not collageifaces.ICollageRow.providedBy(context):
        return
    if _is_mode_set(context, 'recursive') or _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'add')
    _log('handle added row {0} of language {1}'.format(
        '/'.join(context.getPhysicalPath()),
        context.Language()
    ))
    collage = aq_parent(context)
    for language in collage.getTranslations():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def added_col(context, event):
    """Event handler on create of a new col

    - creates translations of itself at the right place in all
      translations of its parent row
    """
    __traceback_info__ = 'Language: {0}, context: {1}'.format(
        context.Language(),
        '/'.join(context.getPhysicalPath()),
    )
    if not collageifaces.ICollageColumn.providedBy(context):
        return
    if _is_mode_set(context, 'recursive') or _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'add')
    _log('translate added column {0} of language {1}'.format(
        '/'.join(context.getPhysicalPath()),
        context.Language()
    ))
    row = aq_parent(context)
    for language in row.getTranslations():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def added_content(context, event):
    """Event handler on create of a new content

    - creates translations of itself at the right place in all
      translations of its parent col
    - target workflow state is private
    """
    __traceback_info__ = 'Language: {0}, context: {1}'.format(
        context.Language(),
        '/'.join(context.getPhysicalPath()),
    )
    parent = aq_parent(context)
    if not collageifaces.ICollageColumn.providedBy(parent):
        return
    if _is_mode_set(context, 'recursive') or _is_mode_set(context, 'add'):
        return
    _set_mode(context, 'add')
    for language in parent.getTranslations():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def deleted_collage_item(context, event):
    """Event handler on delete of a collage, row or column or contained

    - deletes all translations of itself with all their content
    """
    parent = aq_parent(context)
    if (
        _marked(context, 'del') or
        not (
            collageifaces.ICollage.providedBy(context) or
            collageifaces.ICollageRow.providedBy(context) or
            collageifaces.ICollageColumn.providedBy(context) or
            collageifaces.ICollageColumn.providedBy(parent)
        )
    ):
        return
    _log('recursive delete collage structure {0}'.format(
        '/'.join(context.getPhysicalPath())
    ))
    for language, record in context.getTranslations().items():
        content = record[0]
        if aq_base(content) == aq_base(context):
            continue
        cid = content.getId()
        parent = aq_parent(content)
        if cid in parent:
            parent.manage_delObjects(cid)

# aq_parent(context).moveObjectToPosition(
#     context.getId(),
#     context.getCanonical().getObjPositionInParent()
# )
