def get_translation(obj, attribute, language):
    """Get the translation from an object, for an attribute.

    The `obj` object is expected to have an attribute or key named `translations`
    and its value should be of type `dict[str,dict[str,str]]`.

    If the translation can't be found in the translations mapping,
    get the attribute on the object itself and raise
    :py:exc:`AttributeError` if it can't be found.

    The language property is converted to lowercase (see :py:func:`lower_case_dict`
    which must have been called on the translations first.

    :param str attribute: The attribute to get
    :param str language: The RFC 4646 language code
    """
    language = language.lower()
    try:
        return obj.translations[language][attribute]
    except (AttributeError, KeyError, TypeError):
        pass
    try:
        return obj["translations"][language][attribute]
    except (AttributeError, KeyError, TypeError):
        pass

    if hasattr(obj, attribute):
        return getattr(obj, attribute)

    try:
        return obj[attribute]
    except (TypeError, AttributeError):
        pass

    raise AttributeError(
        "Can't find translation '{}' for object type '{}'".format(attribute, type(obj).__name__)
    )


def lower_case_dict(translations=None):
    """Returns a new dict, with its keys converted to lowercase.

    :param dict[str, Any] translations: A dictionnary to be converted.
    """
    if translations is None:
        return
    return {k.lower(): v for k, v in translations.items()}
