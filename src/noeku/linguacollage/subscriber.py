# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Product.Collage import interfaces as collageifaces


def translate_collage_recursivly(event, context):
    """Event handler on translate of a collage.

    - Iterates over all contained rows and translates them.
    """
    if not collageifaces.ICollage.providedBy(context):
        return


def translate_row_recursivly(event, context):
    """Event handler on translate of a row.

    - Iterates over all contained cols and translates them.
    """
    if not collageifaces.ICollageRow.providedBy(context):
        return


def translate_col_recursivly(event, context):
    """Event handler on translate of a column.

    - Iterates over all contained content and translates it.
    - fails if an untranslated alias target exists
    """
    if not collageifaces.ICollageColumn.providedBy(context):
        return


def added_row(event, context):
    """Event handler on create of a new row

    - creates translations of itself at the right place in all
      translations of its parent collage
    """
    if not collageifaces.ICollageRow.providedBy(context):
        return


def added_col(event, context):
    """Event handler on create of a new col

    - creates translations of itself at the right place in all
      translations of its parent row
    """
    if not collageifaces.ICollageColumn.providedBy(context):
        return


def added_content(event, context):
    """Event handler on create of a new content

    - not for aliases
    - creates translations of itself at the right place in all
      translations of its parent col
    - target workflow state is private
    """
    parent = aq_parent(context)
    if (
        not collageifaces.ICollageRow.providedBy(parent)
        or collageifaces.ICollageAlias.providedBy(context)
    ):
        return


def added_alias(event, context):
    """Event handler on create of a new content

    - creates translations of itself at the right place in all
      translations of its parent col
    - target workflow state is private
    """
    if not collageifaces.ICollageAlias.providedBy(context):
        return


def deleted_row(event, context):
    """Event handler on delete of a row

    - deletes all translations of itself with all their content
    """
    if not collageifaces.ICollageRow.providedBy(context):
        return


def deleted_col(event, context):
    """Event handler on delete of a col

    - deletes all translations of itself with all their content
    """
    if not collageifaces.ICollageCol.providedBy(context):
        return


def deleted_content(event, context):
    """Event handler on delete of a content

    - valid for aliases too
    - deletes all translations of itself
    """
    parent = aq_parent(context)
    if not collageifaces.ICollageRow.providedBy(parent):
        return
