<?php
/**********************************************************************
 * $Id: index_imagemap.php,v 1.1 2006/06/25 17:40:40 lbecchi Exp $
 * 
 * purpose: a simple script used to build imagemap
 *
 * author: Andrea Cappugi & Lorenzo Becchi
 *
 * 
 *
 * TODO:
 *
 * 
 *
 **********************************************************************
 *
 * Copyright (c) 2006, ominiverdi.org
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

?>
 <HTML>
 <HEAD>
 <TITLE>Imagemap demo</TITLE>
 <SCRIPT>
 function Clicked(p)
 {
        pid = '';
        if (p)
                pid = p;
        alert('Poly '+pid+' clicked !');
 }

 function SymbolClicked(p)
 {
        pid = '';
        if (p)
                pid = p;
        alert('Point/Symbol '+pid+' clicked !');
 }
 </SCRIPT>
 </HEAD>
 <BODY>

 <FORM NAME="mymap" METHOD=POST ACTION="<? print $self?>">
 <SCRIPT>

 if (navigator.appName=="Microsoft Internet Explorer"){
        document.write('<IMG NAME="IEmapa" usemap="#map1" BORDER=1 SRC="<?php echo $image_url?>"><BR>');
        document.write('<INPUT TYPE=HIDDEN NAME="mapa_x" VALUE="0"><BR>');
        document.write('<INPUT TYPE=HIDDEN NAME="mapa_y" VALUE="0"><BR>');
 } else {
        document.write('<INPUT TYPE=IMAGE NAME="mapa" usemap="#map1" BORDER=1 SRC="<?php echo $image_url?>"><BR>');
 }

 </SCRIPT>
 <? include $imagemap_url ?>
 </FORM>
 </HTML>
