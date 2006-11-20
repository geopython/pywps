<?php
/********************************************************************************
 Copyright (c) 2002-2003 Armin Burger
 
 Permission is hereby granted, free of charge, to any person obtaining 
 a copy of this software and associated documentation files (the "Software"), 
 to deal in the Software without restriction, including without limitation 
 the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 and/or sell copies of the Software, and to permit persons to whom the Software 
 is furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included 
 in all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR 
 COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
**********************************************************************************/

//require_once('fpdf.php');
//require_once('print.php');

class Pdf extends FPDF
{

    function Pdf($map, $prScale, $orientation, $units, $format)
    {
        $this->FPDF($orientation,$units,$format);
        
        $mapW = 700; 
        $mapH = 530; 
        $printMap = new PRINTMAP($map, $mapW, $mapH, $prScale, "pdf", 144);
        $printUrlList = $printMap->returnImgUrlList();
        
        $this->initPDF("Armin Burger", "p.mapper", "Arial", 9);
        $this->setPrTitle($prTitle); 
        $this->printPDF($map, $mapW, $mapH, $printUrlList, $prScale);
        $this->printScale(_("Scale"), $prScale);
        $this->printLegendPDF($map, $prScale, 30, 500);
    }
    
    
    function initPDF($author, $title, $defFontType, $defFontSize)
    {
        $this->setAuthor($author);
        $this->setTitle($title);
        $this->Open();
        $this->SetLineWidth(1.5);
        $this->AddPage();
        $this->defaultFontType = $defFontType;
        $this->defaultFontSize = $defFontSize;
    }
    
    
    // TITLE
    function setPrTitle($prTitle) 
    {
        $this->prTitle = $prTitle;
    }
    
    function getPrTitle() 
    {
        $prTitle = $this->prTitle;
        return $prTitle;
    }
    
    
    // FONTS 
    function resetDefaultFont()
    {
        $this->SetFont($this->defaultFontType, "", $this->defaultFontSize); 
        $this->SetTextColor(0, 0, 0);
    }
    
    
    
    /*
     * PRINT FUNCTIONS
     ***********************/
    
    // MAIN PDF PAGE PTINTING
    function printPDF($map, $pdfMapW, $pdfMapH, $printUrlList, $prScale)
    {
        $printmapUrl  = $printUrlList[0];
        $printrefUrl  = $printUrlList[1];
        $printsbarUrl = $printUrlList[2];
    
        // Dimensions: A4 Portrait
        $pageWidth = 595;
        $pageHeight = 842;
    
        // Reduction factor, calculated from PDF resolution (72 dpi)
        // reolution from map file and factor for increased map size for PDF output
        //$redFactor = 72/(($map->resolution) / $_SESSION["pdfres"]);
        $redFactor = 72 / 96; 
    
        $imgWidth = $pdfMapW * $redFactor;
        $imgHeight = $pdfMapH * $redFactor;
    
        // Margin lines around page
        $this->margin = round(($pageWidth - ($pdfMapW * $redFactor)) / 2);
        $this->xminM = $this->margin;                                     //   ____________
        $this->yminM = $this->margin;                                     //  |             |topLineDelta
        $this->xmaxM = $pageWidth - $this->margin;                        //  |------------  topLineY
        $this->ymaxM = $pageHeight - $this->margin;                       //  |   IMG
                                                                          //  |
        $this->topLineDelta = 26;                                         //  |------------  botLineY
        $this->topLineY = $this->yminM + $this->topLineDelta;             //  |   LEG
        $this->botLineY = $this->topLineY + $imgHeight;                   //  |------------
    
    
        // Draw Map Image
        $web = $map->web;
        $basePath = $web->imagepath;
        $mapImgBaseName = basename($printmapUrl);
        $mapImgFullName = $basePath . $mapImgBaseName;
        $this->Image($mapImgFullName, $this->xminM, $this->topLineY , $imgWidth, $imgHeight);
    
        //Draw Reference Image
        $refImgBaseName = basename($printrefUrl);
        $refImgFullName = $basePath . $refImgBaseName;
        $refmap = $map->reference;
        $this->refmapwidth = ($refmap->width) * $redFactor ;
        $this->refmapheight = ($refmap->height) * $redFactor ;
        $this->Image($refImgFullName, $this->xminM, $this->topLineY, $this->refmapwidth, $this->refmapheight);
    
        //Draw Scalebar Image
        $sbarImgBaseName = basename($printsbarUrl);
        $sbarImgFullName = $basePath . $sbarImgBaseName;
        $sbar = $map->scalebar;
        $sbarwidth = ($sbar->width) * $redFactor ;
        $sbarheight = ($sbar->height);
        $this->Image($sbarImgFullName, $this->xminM, $this->botLineY - 20, $sbarwidth, $sbarheight + 15);
        
        // Print title bar with logo
        $this->printTitle($this->getPrTitle());
        
        // Print frame lines (margins, inner frames)
        $this->printFrameLines(1);
        
        $this->redFactor = $redFactor;
    }
    
    
    // PRINT OUTER AND INNER FRAME LINES AROUND IMAGE AND LEGEND
    function printFrameLines($firstPage)
    {
        $this->printMargins();
    
        // Inner frame lines
        $this->SetLineWidth(1);
        $this->Line($this->xminM, $this->topLineY, $this->xmaxM, $this->topLineY);
        
        if ($firstPage) { 
            // Bottom line for map image
            $this->Line($this->xminM, $this->botLineY, $this->xmaxM, $this->botLineY);
        
            // Frame around ref map
            $this->Line($this->xminM, $this->topLineY + $this->refmapheight, $this->xminM + $this->refmapwidth, $this->topLineY + $this->refmapheight);
            $this->Line($this->xminM + $this->refmapwidth, $this->topLineY + $this->refmapheight, $this->xminM + $this->refmapwidth, $this->topLineY);
        }
    }
    
    // OUTER (MARGIN) LINES
    function printMargins()
    {
        // Outer margin
        $this->SetLineWidth(1.5);
        $this->Line($this->xminM, $this->yminM, $this->xminM, $this->ymaxM);
        $this->Line($this->xminM, $this->ymaxM, $this->xmaxM, $this->ymaxM);
        $this->Line($this->xmaxM, $this->ymaxM, $this->xmaxM, $this->yminM);
        $this->Line($this->xmaxM, $this->yminM, $this->xminM, $this->yminM);
    }
    
    
    // TITLE IN TITLE BAR
    function printTitle($prTitle)
    {
        // Draw background in image color
        $this->SetFillColor(51, 102, 153);
        $this->Rect($this->xminM, $this->yminM, $this->xmaxM - $this->xminM, $this->topLineDelta , "F");
        
        // Print logo image
        $this->Image('./images/logo.png', $this->xminM, $this->yminM, 124);
        
        if (strlen($prTitle) > 0) {
            // Print title
            $this->SetTextColor(255, 255, 255);
            $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize + 5);
            $this->SetXY($this->xminM + 120, $this->yminM + (0.5 * $this->topLineDelta));
            $this->Cell(0, 0, $prTitle);
        }    	
    }
    
    // SCALE ABOVE SCALEBAR
    function printScale($prString, $prScale)
    {
        $this->SetTextColor(0, 0, 0);
        $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize);
        $scaleStr = $prString . " 1: $prScale";
        $this->SetXY($this->xminM + 6, $this->botLineY - 25);
        $this->Cell(50, 0, $scaleStr);
    }
    
    
    // 2-COLUMN LEGEND
    function printLegendPDF($map, $scale)
    {
        $grouplist = $_SESSION["grouplist"];
        $defGroups = $_SESSION["defGroups"];
        $icoW      = $_SESSION["icoW"] * $this->redFactor;  // Width in pixels
        $icoH      = $_SESSION["icoH"] * $this->redFactor;  // Height in pixels
        $imgFormat = $_SESSION["imgFormat"];
        
        // Vertical differerence between lines (for new groups and classes)
        /*$dy_grp = $icoH + 4;
        $dy_cls = $icoH + 2; */
    
        // GET LAYERS FOR DRAWING AND IDENTIFY
        if (isset ($_SESSION["groups"]) && count($_SESSION["groups"]) > 0){
            $groups = $_SESSION["groups"];
        }else{
            $groups = $defGroups;
        }
    
        $legPath = "images/legend/";
    
        $x0 = $this->xminM + 10;
        $x = $x0;
        $y = $this->botLineY + 10;
    
        $xr = (($this->xmaxM - $this->xminM) + (2 * $this->margin)) / 2 + 5;
        $mcellW = (($this->xmaxM - $this->xminM) / 2) - $icoW - 28;
    
        // Text Color for legend annotations
        $this->SetTextColor(0, 0, 0);
    
        foreach ($grouplist as $grp){
            if (in_array($grp->getGroupName(), $groups, TRUE)) {
                $glayerList = $grp->getLayers();
                $grpClassList = array();
                $grpcnt = -1;  // used to identify if layers are still in the same group
    
                // Get number of classes for each group
                // write group classes to array
                $numcls = 0;
                foreach ($glayerList as $glayer) {
                    $legendLayer = $map->getLayer($glayer->getLayerIdx());
                    $numClasses = count($glayer->getClasses());
                    $skipLegend = $glayer->getSkipLegend();
                    
                    //if ($legendLayer->type < 3 && checkScale($map, $legendLayer, $scale) == 1) {
                    if (($legendLayer->type < 3 || $legIconPath || $numClasses > 1) && checkScale($map, $legendLayer, $scale) == 1 && $skipLegend < 2) {
    
                        $leglayers[] = $legendLayer;
                        $numcls += $legendLayer->numclasses;
                        
                        $legLayerName = $glayer->getLayerName();
                        $layClasses = $glayer->getClasses();
                        $clsno = 0;
                        foreach ($layClasses as $cl) {
                            $icoUrl = $legPath.$legLayerName.'_i'.$clsno.'.'.$imgFormat;
                            $grpClassList[] = array($cl, $icoUrl);
                            $clsno++;
                        }
                    }
                }
    
                error_log("$numcls  \n");
                // Only 1 class for all Layers -> 1 Symbol for Group
                if ($numcls == 1) {
                    $legLayer = $leglayers[0];
                    $legLayerName = $legLayer->name;
                    $icoUrl = $legPath.$legLayerName.'_i0.'.$imgFormat;
    
                    // Putput PDF
                    $this->Image($icoUrl, $x, $y, $icoW, $icoH);
                    $this->SetXY($x + $icoW + 5, $y + 6);
                    $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize);
                    $this->Cell(0, 0, $grp->getDescription());
    
                    $y += 18;   // y-difference between GROUPS
    
                // More than 2 classes for Group  -> symbol for *every* class
                } elseif ($numcls > 1) {
                    $this->SetXY($x - 2, $y + 6);
                    $this->SetFont($this->defaultFontTyped, "B", $this->defaultFontSized);
                    $this->Cell(0, 0, $grp->getDescription());
                    $y += 14;  // y-difference between GROUP NAME and first class element
    
                    $allc = 0;
                    $clscnt = 0;
    
                    #if ($clscnt < $numcls) {
                    foreach ($grpClassList as $cls) {
                        $clsStr = $cls[0];
                        $icoUrl = $cls[1];
                        $clno = 0;
                        
                        // Output PDF
                        $this->Image($icoUrl, $x, $y, $icoW, $icoH);
                        $this->SetFont($this->defaultFontTyped, "", $this->defaultFontSized);
    
                        // What to do if CLASS string is too large for cell box
                        if ($this->GetStringWidth($clsStr) >= $mcellW) {   // test if string is wider than cell box
                            $mcellH = 10;
                            $ydiff = 0;
                            $yadd = 1;
                        } else {
                            $mcellH = 0;
                            $ydiff = 6;
                        }
                        $this->SetXY($x + $icoW + 5, $y + $ydiff);
                        $this->MultiCell($mcellW, $mcellH, $clsStr, 0, "L", 0);
    
                        // change x and y coordinates for img and cell placement
                        if ($clscnt % 2) {   // after printing RIGHT column
                            $y += 16;
                            $y += ($clscnt == ($numcls - 1) ? 2 : 0);  // Begin new group when number of printed classes equals total class number
                            $x = $x0;
                            if ($yadd) $y += 8;
                            $yadd = 0;
                        } else {           // after printing LEFT column
                            if ($clscnt == ($numcls - 1)) {    // Begin new group when number of printed classes equals total class number
                                $y += 18;
                                $x = $x0;
                            } else {
                                $x = $xr;     // Continue in same group, add only new class item
                            }
                        }
                        
                        $allc++;
                        $clscnt++;
    
                        // if Y too big add new PDF page and reset Y to beginning of document
                        if ($y > (($this->ymaxM) - 30)) {
                            $this->AddPage("P");
                            $this->printTitle("");
                            $this->printFrameLines(0);
                            $this->resetDefaultFont();
                            $y = $this->yminM + 35;
                        }
                    }
                }
            }
            unset($leglayers);
            unset($grpClassList);
        }
    }


}  // END CLASS


?>
