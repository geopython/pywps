/**********************************************************************
 *
 * $Id: jsExpander.js,v 1.3 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: manage expandable HTML elements
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 **********************************************************************
 *
 * Copyright (c) 2005, DM Solutions Group Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 * DEALINGS IN THE SOFTWARE.
 *
 **********************************************************************/

var goExpanderManager = new cExpanderManager();

/*
 * class to manage top level expander state between page
 * loads
 */
function cExpanderManager()
{
    this.expanders = new Array();
    this.formElement = null;
    
    this.add = cExpanderManager_Add;
    this.initialize = cExpanderManager_Initialize;
    this.registerOpen = cExpanderManager_RegisterOpen;
    this.registerClose = cExpanderManager_RegisterClose;
    this.isVisible = function() { return true; };
    this.isElementVisible = cExpanderManager_IsElementVisible;
    
    this.expandAll = cExpanderManager_ExpandAll;
    this.collapseAll = cExpanderManager_CollapseAll;
}

function cExpanderManager_Add( oExpander )
{
    this.expanders[this.expanders.length] = oExpander;
    oExpander.manager = this;
}

function cExpanderManager_Initialize()
{
    if (this.formElement == null)
        return;
        
    for(var i=0; i < this.expanders.length; i++)
    {
        if (this.expanders[i].bIsOpen)
            this.registerOpen( this.expanders[i] );
        this.expanders[i].initialize( this.isElementVisible( this.expanders[i].element.id ));
    }
}

function cExpanderManager_RegisterOpen( oExpander )
{
    if (this.formElement == null)
        return;

    if (this.formElement.value.indexOf( oExpander.element.id ) < 0 )
    {
        if (this.formElement.value != '')
            this.formElement.value += ",";
        this.formElement.value += oExpander.element.id;
    }  
}

function cExpanderManager_RegisterClose( oExpander )
{
    if (this.formElement == null)
        return;

    var rx = new RegExp( oExpander.element.id, '' );
    var text = this.formElement.value;
    text = text.replace( rx, '' );
    text = text.replace( /,,/g, ',' );
    if (text.substr(0, 1) == ',')
        text = text.slice( 1 );
    if (text.substr(-1) == ',')
        text = text.slice( 0, -1);
    this.formElement.value = text;
}

function cExpanderManager_IsElementVisible( id )
{
    rx = new RegExp( id, '' );
    return rx.test( this.formElement.value );
}

function cExpanderManager_ExpandAll()
{
    for(var i=0; i < this.expanders.length; i++)
    {
        this.expanders[i].expandAll();
    }
}

function cExpanderManager_CollapseAll()
{
    for(var i=0; i < this.expanders.length; i++)
    {
        this.expanders[i].collapseAll();
    }
    return true;
}

/*
 * basic expander class to handle an expandable element
 * that expands or contracts child elements.
 */
function cExpander( elm )
{
    this.element = elm;
    this.element.expander = this;
    this.children = new Array();
    this.bIsOpen = false;
    this.manager = null; 
    this.img = null;
    this.szExpandImgSrc = '';
    this.szCollapseImgSrc = '';
    
    this.addElement = cExpander_AddElement;
    this.open = cExpander_Open;
    this.close = cExpander_Close;
    this.expandAll = cExpander_ExpandAll;
    this.collapseAll = cExpander_CollapseAll;
    this.expand = cExpander_Expand;
    this.contract = cExpander_Contract;
    this.toggle = cExpander_Toggle;
    this.initialize = cExpander_Initialize;
    this.registerOpen = cExpander_RegisterOpen;
    this.registerClose = cExpander_RegisterClose;
    this.isVisible = cExpander_IsVisible;
}

function cExpander_AddElement( elm )
{
    this.children[this.children.length] = elm;
    elm.manager = this;
    return true;
}

function cExpander_Open()
{
    for( var i=0; i<this.children.length; i++)
    {
        this.children[i].element.style.display = 'block';
        if (this.children[i].bIsOpen)
        {
            this.children[i].open();
        }
    }
    if (this.img != null && this.szCollapseImgSrc != '')
    {
        this.img.src = this.szCollapseImgSrc;
    }
    return true;
}

function cExpander_Close()
{
    for( var i=0; i<this.children.length; i++)
    {
        this.children[i].element.style.display = 'none';
        this.children[i].close();
    }
    if (this.img != null && this.szExpandImgSrc != '')
    {
        this.img.src = this.szExpandImgSrc;
    }
    return true;
}

function cExpander_ExpandAll()
{
    for( var i=0; i<this.children.length; i++)
    {
        this.children[i].expandAll();
    }
    this.expand();
    return true;
}

function cExpander_CollapseAll()
{
    for( var i=0; i<this.children.length; i++)
    {
        this.children[i].collapseAll();
    }
    this.contract();
    return true;
}

function cExpander_Expand()
{
    this.bIsOpen = true;
    this.registerOpen( this );
    this.open();
    return true;
}

function cExpander_Contract()
{
    this.bIsOpen = false;
    this.registerClose( this );
    this.close();
    return true;
}

function cExpander_Toggle()
{
    if (this.bIsOpen)
        this.contract();
    else
        this.expand();
    return true;
}

/* intialize this and all children recursively */
function cExpander_Initialize( bState )
{
    this.bIsOpen = bState;
    for( var i=0; i<this.children.length; i++)
    {
        var child = this.children[i];
        if (this.isVisible())
            child.element.style.display = 'block';
        
        if (child.bIsOpen)
            this.registerOpen( child );
       
        this.children[i].initialize( goExpanderManager.isElementVisible( child.element.id ));
    }
    if( this.img != null )
    {
        if (this.bIsOpen && this.szCollapseImgSrc != '')
        {
            this.img.src = this.szCollapseImgSrc;
        }
        else if (!this.bIsOpen && this.szExpandImgSrc != '')
        {
            this.img.src = this.szExpandImgSrc;
        }
    }
    return true;
}

/* cascade registration to top level manager */
function cExpander_RegisterOpen(elm)
{
    if (this.manager != null)
        this.manager.registerOpen( elm );
        
    return true;
}

function cExpander_RegisterClose(elm)
{
    if (this.manager != null)
        this.manager.registerClose( elm );

    return true;
}

/* determine if all elements in heirarchy are also open */
function cExpander_IsVisible()
{
    var bVisible = this.bIsOpen;
    if (this.manager != null)
        bVisible = bVisible && this.manager.isVisible();
    return bVisible;
}
