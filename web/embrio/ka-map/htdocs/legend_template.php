<?php
/**********************************************************************
 *
 * $Id: legend_template.php,v 1.6 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: server-side support for a mapserver template-based legend.
 *          This is deprecated by a new client-side only legend.
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original legend_template.php code was written by DM Solutions Group.
 *
 * TODO:
 *
 *   - remove this file from cvs.
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
include_once('../include/config.php');

$groups = isset( $_REQUEST['g'] ) ? $_REQUEST['g'] : "";
$layers = isset( $_REQUEST['layers'] ) ? $_REQUEST['layers'] : "";

if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}

$oMap = ms_newMapObj($szMapFile);
$oMap->legend->set( "template", dirname(__FILE__)."/legend_template.html" );
for($i=0;$i<$oMap->numlayers;$i++)
{
    $oLayer = $oMap->getLayer($i);
    if ($oLayer->group == '')
    {
        $oLayer->set('group', '__base__');
        $oLayer->setMetaData( 'hide_checkbox', '1' );
        $oLayer->setMetaData( 'group_title', 'Base Layers' );
    }
    else
        $oLayer->setMetaData( "group_title", $oLayer->group );
}

$szResult = $oMap->processLegendTemplate(array());
$szHeader = <<<EOT
<style type="text/css">
.legendClassLabel {
  font-family: arial;
  font-size: 11px;
  font-weight: normal;
}


.legendGroupLabel {
  font-family: arial;
  font-size: 11px;
  font-weight: bold;
}
.legendGroup {
  background-color: #d4d4d4;
  border-top: 1px solid #ffffff;
  border-left: 1px solid #ffffff;
  border-bottom: 1px solid #666666;
  margin-bottom: 0px;
}

.legendHeader {
  background-color: #a9a9a9;
  border-top: 1px solid #ffffff;
  border-left: 1px solid #ffffff;
  border-bottom: 1px solid #666666;
  
  margin-bottom: 0px;
  padding-left: 2px;
  font-family: arial;
  font-size: 12px;
  font-weight: bold;
}

a.legendHref {
    font-family: arial;
    font-size: 10px;
    font-weight: bold;
    text-decoration: none;
    color: #ffffff;
}

a.legendHref:link {

}

a.legendHref:active {

}

a.legendHref:hover {
    color: #eeeeee;
}
</style>
<div class="legendHeader">
<table cellspacing="0" cellpadding="2" width="100%">
<tr>
  <td>Layers</td>
  <td align="right">
<a class="legendHref" href="javascript:void(0)" onclick="goExpanderManager.expandAll( ); return false;"><img src="images/expand.png" border="0" alt="expand all" title="expand all"></a>
<a class="legendHref" href="javascript:void(0)" onclick="goExpanderManager.collapseAll( ); return false;"><img src="images/collapse.png" border="0"  alt="collapse all" title="collapse all"></a>
  </td>
</tr>
</table>
</div>
EOT;
echo $szHeader.$szResult."</table></div>";
?>
