# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.Collage import interfaces as collageifaces
import logging


logger = logging.getLogger(__name__)


def _log(msg):
    logger.log(logging.INFO, msg)


def translate_collage_recursivly(context, event):
    """Event handler on translate of a collage.

    - Iterates over all contained rows and translates them.
    """
    if not collageifaces.ICollage.providedBy(context):
        return
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
    if not collageifaces.ICollageRow.providedBy(context):
        return
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
    if not collageifaces.ICollageColumn.providedBy(context):
        return
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
        content.addTranslation(event.language)


def added_row(context, event):
    """Event handler on create of a new row

    - creates translations of itself at the right place in all
      translations of its parent collage
    """
    if not collageifaces.ICollageRow.providedBy(context):
        return
    for language, record in aq_parent(context).getTranslations().items():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def added_col(context, event):
    """Event handler on create of a new col

    - creates translations of itself at the right place in all
      translations of its parent row
    """
    if not collageifaces.ICollageColumn.providedBy(context):
        return
    for language, record in aq_parent(context).getTranslations().items():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def added_content(context, event):
    """Event handler on create of a new content

    - not for aliases
    - creates translations of itself at the right place in all
      translations of its parent col
    - target workflow state is private
    """
    parent = aq_parent(context)
    if not collageifaces.ICollageColumn.providedBy(parent):
        return
    for language in aq_parent(context).getTranslations():
        if context.hasTranslation(language):
            continue
        context.addTranslation(language)


def deleted_row(context, event):
    """Event handler on delete of a row

    - deletes all translations of itself with all their content
    """
    if not collageifaces.ICollageRow.providedBy(context):
        return


def deleted_col(context, event):
    """Event handler on delete of a col

    - deletes all translations of itself with all their content
    """
    if not collageifaces.ICollageCol.providedBy(context):
        return


def deleted_content(context, event):
    """Event handler on delete of a content

    - valid for aliases too
    - deletes all translations of itself
    """
    parent = aq_parent(context)
    if not collageifaces.ICollageRow.providedBy(parent):
        return


# aq_parent(context).moveObjectToPosition(
#     context.getId(),
#     context.getCanonical().getObjPositionInParent()
# )
