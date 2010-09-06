"""
Template
--------
PyWPS Templating system

.. moduleauthor:: Jachym Cepicky <jachym les-ejk cz>

"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
# License:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import os
import re
import cPickle 
import types
import copy

TMPLEXT = "tmpl"
TMPLCEXT = "tmplc"
INCDIR = "inc"
PREF = "TMPL"
VARTYPES=[types.StringType, types.FileType,
        types.FloatType, types.IntType,
        types.NoneType,
        types.BooleanType, types.LongType, types.UnicodeType]

class Token:
    """Base Token class. Token is snipplet of input template. Template
    consits from list of tokens. 
    """
    name = None
    value = None
    _childs = None
    parent = None
    type = None
    closed = False
    statement = None
    printAsTemplate = False
    ifOrElseChild = "if"
    closing = False

    def __init__(self,type=None):
        """Constructor of the Token.

        :param type: Initial type of the object
        :type type: string
        """

        self._childs = [] # initialize empty list of childs
        if type == "loop":
            self.value = []  # loop tokens do need special handeling
        elif type =="if":   
            self.value = False # if tokens do need special handeling
        else:
            self.value = ""
        
        self.type = type

    def addChild(self, childs):
        """Add child to this Token

        .. note:: You can submit also only one child to this method, it will
            be converted to list automatically.

        :param child: list of child tokens
        :type child: [childs]
        """

        # convert single child object to list
        if type(childs) != types.ListType:
            childs = [childs]

        # append each child to self._childs and set parent of it to self
        for child in childs:
            self._childs.append(child)
            child.setParent(self)

    def setParent(self, parent):
        """Set parent of this Token, assign it as child to other Token

        :param parent: parent
        :type parent: Token
        """
        self.parent = parent

    def _printAsValue(self):
        """Format the actual value of this token as string

        :rtype: string
        """
        return str(self.value)

    def __str__(self):
        """Print value or template in output format

        :rtype: string
        """
        if self.value == None:
            raise TemplateError("Token's value not set [%s %s, parent: %s] " % \
                    (self.statement,[self], [self.parent]))
        return self._printAsValue()
    
    def setValue(self,value):
        """Set value for this token

        :param value: any text or attribute, which will be assigned as
            value of this token
        """

        # set string value of the input parameter 
        if value == None:
            value = str(value)
        self.value = value

class IfToken(Token):
    """Special token used for IF/ELSE constructions. This token contains
    childs for the whole IF block as well as ELSE block. It's childs do
    have assigned `ifOrElseChild` attribute, which indicates, whether the
    child token belongs to IF block or the ELSE block.

    .. note:: Childs of this token should appear on the same level of
        nesting, as this token. So any child token with the same name will
        get the same value.
    """
    type = "if"
    value = False
    ifOrElseChilds = "if"

    def addChild(self, childs):

        # convert single child input to list of childs
        if type(childs) != types.ListType:
            childs = [childs]

        # append child to self._childs, set parent to self for each child,
        # indicate, whether it is in IF-THEN block or it belongs to ELSE
        for child in childs:
            self._childs.append(child)
            child.setParent(self)
            child.ifOrElseChild = self.ifOrElseChilds

    def setParent(self, parent):

        # set parent for each child in self._childs list, as well as for
        # this one
        for child in self._childs:
            child.setParent(self)
        self.parent = parent

    def _printAsValue(self):

        # format the output string
        val = ''
        for child in self._childs:
            # if this value is True and child belongs to IF-THEN block or
            # this value is False and child belongs to the ELSE block,
            # print it
            if (self.value and child.ifOrElseChild == "if") or \
               (not self.value and child.ifOrElseChild == "else"):
                val += child.__str__()
        return val

    def setValue(self,value):
            
        self.value = not not value
        # set the value for childs as well, because self.name can be the
        # same, as child.name and they chould seem to be on one level
        for child in self._childs:
            if child.name == self.name:
                child.setValue(value)


class LoopToken(Token):
    """Special token used for LOOPing constructions

    .. note:: Childs of this token should appear on the same level of
        nesting, as this token. So any child token with the same name will
        get the same value.
    """
    type = 'loop'

    def __init__(self,*args):
        Token.__init__(self, args)
        self.value = []

    def _printAsValue(self):
        val = ''
        
        # since this value is list of childs, we have to approach in two
        # loops
        for child in self.value:
            for value in child:
                val += value.__str__()
        return val

    def setParent(self, parent):

        # set parent to each childs 
        for child in self._childs:
            child.setParent(self)

        # and set parent to each child within existing value
        # since this value is list of childs, we have to approach in two
        # loops
        for value in self.value:
            for child in value:
                child.setParent(self)
        self.parent = parent

class VarToken(Token):
    """Token used for VAR constructions"""
    type = 'var'

    def _printAsValue(self):

        # return 'None', if this value is None and string representation
        # in general
        if self.parent == None:
            return str(self.value)
        elif self.parent.value != None:
            return str(self.value)

class TemplateProcessor:
    """Processor of the template class. This class is used for
    
        - loading template from text file
        - parsing (tokenizing) it to tokens object
        - setting values for each token
        - printing the result
    """
    _compile = True
    _file = None
    _cfile = None
    template = None
    _vars = {}

    def __init__(self, fileName = None, compile=True):
        """Class constructor

        :param fileName: file name of the template
        :type fileName: string
        :param compile: Should this template be stored in compiled form?
        :type compile: boolean
        """

        self._file = fileName
        self._compile = compile

        if self._file:
            # parse the file, if it is compiled and it should not be
            # compiled by configuration and if it is up-to-date
            try:
                if self.isCompiled() and\
                        self.isUpToDate():
                    self.readFromCompiled()
                elif compile == True:
                    self.recompile()
            except:
                self.recompile()

    def readFromCompiled(self):
        """Set self.tokens from existing compiled file
        """
        self.tokens =  cPickle.load(open(self._cfile,"rb"))

    def recompile(self):
        """Set self.tokens from input text file and store them in compiled
        form for later usage.
        """

        # parse input data
        self.tokens  = self.tokenize(open(self._file,"r").read())

        # store to binary form
        if self._compile:
            try:
                cPickle.dump(self.tokens, open(self._cfile,"w"), True)
            except Exception,e:
                raise TemplateError("Could not store file in compiled form: %s. Try to set permission for this directory to 777" % e)

    def tokenize(self, templateData):
        """Tokenize input text data.

        :param templateData: input text 
        :type templateData: string
        :return: list of tokens
        """

        # define regexp pattern for statements
        pattern = r"""
            (?:^[ \t]+)?               # eat spaces, tabs (opt.)
            (<
             /?%s_[A-Z]+             # closing slash + statement
             [ a-zA-Z0-9""/.=:_\\-]*   # statement content, to final >
             >)
            [%s]?                      # eat trailing newline (opt.)
        """ % (PREF,os.linesep)
        regex = re.compile(pattern, re.VERBOSE | re.MULTILINE)

        # list of tokens
        tokens = []
        # list of opend statements
        stack = []
        for statement in regex.split(templateData):
                
            # skip empty statements
            if not statement:
                continue

            # create new token from class, based on it's type
            token = self.getToken(statement)

            # if this token is closing some other token (SHOULD be
            # stack[-1] token), remove it from the stack and mark as
            # closed. Closing tokens are not included to final list of
            # tokens
            if token.closing:
                closedToken = stack.pop()
                closedToken.closed = True
                continue
            
            # handle 'else' token - just indicate for the last if token,
            # that all comming childs will belong to ELSE block
            if token.type == "else":
                lastIfToken = self._getLastIfToken(stack)
                lastIfToken.ifOrElseChilds = "else"
                continue

            # handle include statement right here. token is then list of
            # tokens, not single one
            if token.type == "include":
                token = self.getIncludedTokens(token)

            # add token to parent token (if exists) or to root list of
            # tokens
            if len(stack):
                stack[-1].addChild(token)
            else:
                # if the token was of type 'include', than we are handeling
                # list of tokens now - add to parent, according to this
                if type(token) == types.ListType:
                    tokens += token
                else:
                    tokens.append(token)

            # if the token is opened one, like IF or LOOP, add the token to
            # tokens stack
            if type(token) == types.InstanceType and\
                not token.closed:
                stack.append(token)

        # handle error: some opened token was not closed, the template
        # might be written bad
        if len(stack):
            tokenNames = ""
            for token in stack:
                tokenNames += "type: %s, name: %s; " % (token.type.upper(), token.name)
            raise TemplateError("Statement(s) [%s] not closed! The document is noto well formated."% tokenNames)

        return tokens

    def getToken(self,statement):
        """Create new token object, based on input text statement

        :param statement: some statement from the template
        :type statement: string
        :return: new token instance
        """
        
        # the statement does start on something like "<TMPL_", this needs
        # special care
        if statement.startswith("<"+PREF) or \
           statement.startswith("</"+PREF):

            # remove <> from the statement
            statement = self._debracketize(statement)
                
            # get special parameters
            params = re.split(r"\s+", statement)

            # get desired class and type name
            (tokenType,typeName) = self._getTokenType(params)

            # create new instance of desired token, set type, name, value
            # (if any), closed attribute and statement attribute
            token = tokenType()
            token.type = typeName
            token.name = self._getTokenName(params)
            token.setValue(self._getTokenValue(token.type,params))
            token.closed = self._getTokenClosed(token.type,statement)

            # if this token starts on something like </TMPL_, it must be
            # closing something
            if statement.startswith("/"+PREF):
                token.closing = True
        else:
            # create some normal text token otherwise
            token = Token()
            token.setValue(statement)
            token.closed = True
        token.statement = statement
        return token

    def getIncludedTokens(self, token):
        """Return list of tokens, which are taken from the included file

        :param token: input token of type include
        :return: list of tokens
        """
        (templateDir, fileName) = os.path.split(self._file)

        # use our tokenize method for this work
        tokens = self.tokenize(
                open(os.path.join(templateDir,INCDIR,token.value),"r").read())
        return tokens

    def _getLastIfToken(self, tokens):
        """Get last token in the list of tokens (stack)

        :param tokens: stack of tokens
        """

        # find the index of last IF token
        lastIfToken = None
        for (i,token) in enumerate(tokens):
            if token.type == "if":
                lastIfToken = i
        return tokens[i]


    def _debracketize(self, statement):
        """Remove starting and final <> marks from the statement

        :param statement: template statement
        :type statement: string
        """

        if statement.startswith("<"):
            statement=statement.replace("<","")
        if statement.endswith(">"):
            statement=statement.replace(">","")

        return statement

    def _getTokenName(self,params):
        """Get name of the token based on it's parameters
        
        :param params: list of statement parameters
        :type params: [string]
        :return: string|None
        """

        # name is the first parameter, if any
        if len(params) > 1:
            return params[1].replace("/","")
        else:
            return None

    def _getTokenType(self,params):
        """Get type of the token based on it's parameters and coresponding
        class
        
        :param params: list of statement parameters
        :type params: [string]
        :return: class and type name
        :rtype: (:class:`Token`, string)
        """

        type = params[0].replace(PREF+"_","").lower().replace("/","")
        if type == "loop":
            return (LoopToken,type)
        elif type == "var":
            return (VarToken,type)
        elif type == "if":
            return (IfToken,type)
        else:
            return (Token,type)

    def _getTokenValue(self,type,params):
        """Some tokens might already have initial value -- usualy 'normal'
        text tokens the text

        :param type: token type
        :param params: list of statement parameters
        """

        if type == "include":
            return params[1].replace("/","")
        elif type == "if":
            return False
        elif type == "loop":
            return []
        else:
            return None

    def _getTokenClosed(self,type,statement):
        """Control, if the statement is closed

        :param type: type of the token
        :type type: string
        :type statement: string
        :rtype: boolean
        :return: token is closed or not
        """
        if statement.endswith("/") or \
            statement.startswith("/") or \
            type == "var" or \
            type == "include" or \
            type == "else" or \
            type == None:
            return True
        else:
            return False

    def isCompiled(self):
        """Check, if the template is compied -- any *.tmplc file does exist

        :rtype: boolean
        """
        (self.templateDir, fileName) = os.path.split(self._file)
        compiledFileName = fileName.replace(TMPLEXT,TMPLCEXT)
        self._cfile = os.path.join(self.templateDir,compiledFileName)
        return os.path.isfile(self._cfile)

    def isUpToDate(self):
        """Check, if the template is up-to-date, the compiled file is
        younger, than the original template file.

        :rtype: boolean
        """
        templateTime = os.path.getmtime(self._file)
        compiledTemplateTime = os.path.getmtime(self._cfile)
        if templateTime <= compiledTemplateTime:
            return True
        else:
            return False


    def __str__(self):
        """Format this template to text form"""

        str = ""
        # construct the final string from string representation of each
        # token
        for token in self.tokens:
            str += token.__str__()
        return str

    def _setVarValue(self,key,value,tokens,parent=None):
        """Set value of the VAR (or IF) type of token

        :param key: key identificator
        :type key: string
        :param value: the actual value of the token
        :type value: mixed (string, list, boolean, object
        :param tokens: list of tokens, where the search the right one,
            based on the token's name
        :param parent: expected parent token
        :returns: list of tokens (with value set to desired value)
        """

        # search for the token with token.name == value and where
        # token.parent.name == parent.name
        pName = parent
        for token in tokens:
            tParent = None
            if token.parent:
                tParent = token.parent.name

            if pName:
                pName = parent.name

            # if token.name == key and parent.name are the same, this is
            # the one
            if token.name == key and\
                tParent == pName:

                # now, we are setting the VAR value, the type has to
                # correspond. But since IF childs must be on the same
                # level, as IF token, we have to take this into account as
                # well
                if token.type in ("var" , "if"):
                    token.setValue(value)
                else: 
                    raise TemplateError("Token <%s> is not of type VAR"%(token.statement))

            # as already metioned, childs of IF token must appear to be on
            # the same level, as IF token, so try to find the corresponding
            # child
            if token.type == "if":
                self.set(key,value,token._childs)
                for child in token._childs:
                    if child.name == key:
                        child.setValue(value)
            
        return tokens

    def _setLoopValue(self,key,values,tokens):
        """Set value of the loop token

        :param key: key identificator
        :type key: string
        :param value: the actual value of the token
        :type value: mixed (string, list, boolean, object
        :param tokens: list of tokens, where the search the right one,
            based on the token's name
        :param parent: expected parent token
        :returns: list of tokens (with value set to desired value)
        """

        for token in tokens:
            # it can happen, that there is some IF token as well, we set
            # the value of their child as well
            if token.type == "if" and \
                token.name == key:
                    token.setValue(values)

            if token.type == "if":
                self.set(key,values,token._childs)

            # we found the right one  token
            if token.type == "loop" and token.name == key:
                # looptoken.value is list of copies of looptoken._childs,
                # with values set to something. so first, we create empty
                # object
                newValues = []
                # for each value within the input, we make a copy of
                # _childs, fill value of each child with propper value, and
                # at the and, it will be assinged as value to base
                # looptoken
                for value in values:
                    appendChilds = copy.deepcopy(token._childs[:])
                    for name in value:
                        appendChilds = self.set(name,value[name],appendChilds,token)
                    newValues.append(appendChilds)

                token.setValue(newValues)
                token.setParent(token.parent)

        return tokens

    def set(self,key,value,tokens = None, parent=None):
        """Set value of some token

        :param key: key identificator
        :type key: string
        :param value: the actual value of the token
        :type value: mixed (string, list, boolean, object
        :param tokens: list of tokens, where the search the right one,
            based on the token's name
        :param parent: expected parent token
        :returns: list of tokens (with value set to desired value)
        """

        # work on the top level, if on tokens are defined
        if not tokens:
            tokens = self.tokens

        # consider, if we are supposed to set normal token or LOOP token
        if type(value) in VARTYPES:
            return self._setVarValue(key,value,tokens,parent)
        elif type(value) == type([]):
            return self._setLoopValue(key,value,tokens)
        else:
            raise TemplateError("Unknown data type %s of '%s'"%\
                    (type(value), value))

    def _printTokens(self,tokens = None,indent = 0):
        """Print 'dom' like representation of tokens
        """
        # start from the root, if no tokens are given
        if tokens == None:
            tokens = self.tokens

        # for each token, print is representation, name and value with
        # proper indentation and call this method for it's childs as well
        for t in tokens:
            print "\t"*indent,[t], t.name or t.value.strip()
            if t._childs:
                self._printTokens(t._childs, indent+1)

class TemplateError(Exception):
    """General template exception"""
    pass
