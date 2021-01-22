# -*- coding: utf-8 -*-
from sphinx.ext.autodoc import ClassDocumenter, bool_option
from sphinx.ext.napoleon.docstring import NumpyDocstring
from sphinx.util.docstrings import prepare_docstring
from sphinx.util import force_decode
from docutils.parsers.rst import directives
from pywps import Process
from pywps.app.Common import Metadata, MetadataUrl


class ProcessDocumenter(ClassDocumenter):
    """Sphinx autodoc ClassDocumenter subclass that understands the
    pywps.Process class.

    The Process description, its inputs and docputs are converted to a
    numpy style docstring.

    Additional sections (Notes, References, Examples, etc.) can be added
    in the Process subclass docstring using the `docstring` option.
    Additionally, docstring lines can be skipped using the `skiplines` option.

    For, example, the following would append the SimpleProcess class docstring
    to the published docs, skipping the first line.

    .. autoprocess:: pywps.SimpleProcess
       :docstring:
       :skiplines: 1

    """
    directivetype = 'class'
    objtype = 'process'
    priority = ClassDocumenter.priority + 1
    option_spec = {'skiplines': directives.nonnegative_int,
                   'docstring': bool_option}
    option_spec.update(ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        from six import class_types
        return isinstance(member, class_types) and issubclass(member, Process)

    def fmt_type(self, obj):
        """Input and output type formatting (type, default and allowed
        values).
        """
        nmax = 10

        doc = ''
        try:
            if getattr(obj, 'allowed_values', None):
                av = ', '.join(["'{}'".format(i.value) for i in obj.allowed_values[:nmax]])
                if len(obj.allowed_values) > nmax:
                    av += ', ...'

                doc += "{" + av + "}"

            elif getattr(obj, 'data_type', None):
                doc += obj.data_type

            elif getattr(obj, 'supported_formats', None):
                doc += ', '.join([':mimetype:`{}`'.format(f.mime_type) for f in obj.supported_formats])

            elif getattr(obj, 'crss', None):
                doc += "[" + ', '.join(obj.crss[:nmax])
                if len(obj.crss) > nmax:
                    doc += ', ...'
                doc += "]"

            if getattr(obj, 'min_occurs', None) is not None:
                if obj.min_occurs == 0:
                    doc += ', optional'
                    if getattr(obj, 'default', None):
                        doc += ', default:{0}'.format(obj.default)

            if getattr(obj, 'uoms', None):
                doc += ', units:[{}]'.format(', '.join([u.uom for u in obj.uoms]))

        except Exception as e:
            raise type(e)('{0} in {1} docstring'.format(e, self.object().identifier))
        return doc

    def make_numpy_doc(self):
        """Numpy style docstring where meta data is scraped from the
        class instance.

        The numpy style is used because it supports multiple outputs.
        """

        obj = self.object()

        # Description
        doc = list()
        doc.append(u":program:`{}` {} (v{})".format(obj.identifier, obj.title, obj.version or '', ))
        doc.append('')
        doc.append(obj.abstract)
        doc.append('')

        # Inputs
        doc.append('Parameters')
        doc.append('----------')
        for i in obj.inputs:
            doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
            if i.metadata:
                doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append('')

        # Outputs
        doc.append("Returns")
        doc.append("-------")
        for i in obj.outputs:
            doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
        doc.extend(['', ''])

        # Metadata
        hasref = False
        ref = list()
        ref.append("References")
        ref.append("----------")
        ref.append('')
        for m in obj.metadata:
            if isinstance(m, Metadata):
                title, href = m.title, m.href
            elif type(m) == dict:
                title, href = m['title'], m['href']
            else:
                title, href = None, None
            extra_underscore = ""
            if isinstance(m, MetadataUrl):
                extra_underscore = "_" if m.anonymous else ""
            if title and href:
                ref.append(u" - `{} <{}>`_{}".format(title, href, extra_underscore))
                hasref = True

        ref.append('')

        if hasref:
            doc += ref

        return doc

    def get_doc(self, encoding=None, ignore=1):
        """Overrides ClassDocumenter.get_doc to create the doc scraped from the Process object, then adds additional
        content from the class docstring.
        """
        from six import text_type
        # Get the class docstring. This is a copy of the ClassDocumenter.get_doc method. Using "super" does weird stuff.
        docstring = self.get_attr(self.object, '__doc__', None)

        # make sure we have Unicode docstrings, then sanitize and split
        # into lines
        if isinstance(docstring, text_type):
            docstring = prepare_docstring(docstring, ignore)
        elif isinstance(docstring, str):  # this will not trigger on Py3
            docstring = prepare_docstring(force_decode(docstring, encoding), ignore)

        # Create the docstring by scraping info from the Process instance.
        pdocstrings = self.make_numpy_doc()

        if self.options.docstring and docstring is not None:
            # Add the sections from the class docstring itself.
            pdocstrings.extend(docstring[self.options.skiplines:])

        # Parse using the Numpy docstring format.
        docstrings = NumpyDocstring(pdocstrings, self.env.config, self.env.app, what='class', obj=self.object,
                                    options=self.options)

        return [docstrings.lines()]


def setup(app):
    app.add_autodocumenter(ProcessDocumenter)
