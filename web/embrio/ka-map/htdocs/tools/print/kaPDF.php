<?php
/**********************************************************************
 *
 * $Id: kaPDF.php,v 1.2 2006/06/19 15:37:42 lbecchi Exp $
 *
 * purpose: printing system (bug 1498)
 *
 * author: Lorenzo Becchi and Andrea Cappugi
 *
 *
 * TODO:
 * - PDF output with FPDF lib (no PDF server support needed)
 * - GeoTiff output
 * - 
 *
 **********************************************************************
 *
 * Copyright (c)  2006, ominiverdi.org
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
 class kaPDF extends FPDF {
		//map object
		var $oMap;
		//image infos
		var $imageH;
		var $imageW;
		var $imageUrl;
		//legend infos
		var $legendUrl;
		var $legendW;
		var $legendH;
		//scalebar infos
		var $scalebarUrl;
		var $scalebarW;
		var $scalebarH;
		//page dimensions
		var $pageW;
		var $pageH;
		//map extent
		var $extentMx;
		var $extentmx;
		var $extentMy;
		var $extentmy;
		//map scale
		var $scale;
		
	function kaPDF ($oMap, $orientation, $units, $format,$pageW,$pageH){
		$this->FPDF($orientation,$units,$format);	
		$this->oMap=$oMap;
		// Dimensions: A4 Portrait
		
        $this->pageW = $pageW;
        $this->pageH = $pageH;
	}

	function init( $title, $defFontType, $defFontSize) {
        $this->setTitle($title);
        $this->Open();
        $this->SetLineWidth(1.5);
        $this->AddPage();
        $this->defaultFontType = $defFontType;
        $this->defaultFontSize = $defFontSize;
        
   }
  	  
	function drawPage(){
		//da fare
        $this->printBody();
        
        $this->printTitle();
        $this->printExtent();
        $this->printScale();
        $this->printScalebar();
        $this->printLegend();
	} 
	
	function setImage($img,$pw,$ph){
		$this->imageUrl = $img;
		$this->imageW=$pw;
		$this->imageH=$ph;
	}
	function setLegend($img,$pw,$ph){
		$this->legendUrl = $img;
		$this->legendW=$pw;
		$this->legendH=$ph;
	}
	function setScalebar($img,$pw,$ph){
		$this->scalebarUrl=$img;
		$this->scalebarW=$pw;
		$this->scalebarH=$ph;
	}
	function setMapExtent($mx,$my,$Mx,$My){
		$this->extentMx = $mx;
		$this->extentmx = $my;
		$this->extentMy = $Mx;
		$this->extentmy = $My;
		
	}
	function setScale($scale){
		$this->scale = $scale;
	}
	
	function printLegend(){
		if($this->legendUrl){	    		
	    		$newW = $this->pageW-$this->margin*2;
	   		$newH = $newW * $this->imageH/$this->imageW;
	   		
	   		$lW= $newW *$this->legendW/$this->imageW;
	   		$lH= $newH *$this->legendH/$this->imageH;
	  
	    		$this->Image($this->legendUrl, $this->xminM, $this->botLineY+2, $lW);
	    }  	
	}
	function printScalebar(){
		if($this->scalebarUrl){	    
	    		$newW = $this->pageW-$this->margin*2;
	   		$newH = $newW * $this->imageH/$this->imageW;
	  		
	  		$sW= $newW *$this->scalebarW/$this->imageW;
	   		$sH= $sW *$this->scalebarH/$this->scalebarW;
	   		//$sH =20;
	  		//$newX =($this->legendW)?$this->legendW+$this->xminM: $this->xminM;
	  		
	    		$this->Image($this->scalebarUrl, $this->xmaxM - $sW-2, $this->topLineY -$sH -2 , $sW,$sH);
	    }  	
	}
	function printExtent(){
		if ($this->extentMx && $this->extentmx && $this->extentMy && $this->extentmy) {
	
            // Print map extent
            $this->SetTextColor(60, 60, 60);
            $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize +1);
            $this->SetXY($this->xminM + 2, $this->topLineY - $this->defaultFontSize+5);
            $this->Cell(0, 0, 'Map Extent: '.round($this->extentmx,2).', '.round($this->extentmy,2).', '.round($this->extentMx,2).', '.round($this->extentMy,2));
        } 
	}
	function printScale(){
		if ($this->scale) {
            $this->SetTextColor(60, 60, 60);
            $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize +1);
            $this->SetXY($this->xminM + 2, $this->topLineY - $this->defaultFontSize*2+9);
            $this->Cell(0, 0, 'Scale: '.round($this->scale));
        } 
	}
	
	function printTitle(){
        $this->SetLineWidth(0.3);
        $this->Rect($this->xminM, $this->yminM, $this->xmaxM - $this->xminM, $this->topLineDelta , "D");
        
        // Print logo image
        $this->Image('../../images/powered_by_kamap_lt.png', $this->xmaxM - 32, $this->yminM+1, 30);
        
        if (strlen($this->title) > 0) {
            // Print title
            $this->SetTextColor(233,99,0);
            $this->SetFont($this->defaultFontType, "B", $this->defaultFontSize + 8);
            $this->SetXY($this->xminM + 2, $this->yminM + 5);
            $this->Cell(0, 0, $this->title);
        }  
	}
	

	function printBody()
	{
		
		//codeo from Armin Burger pmapper.sourceforge.org
	 	$this->margin = round(20);
        $this->xminM = $this->margin;                                     //   ____________
        $this->yminM = $this->margin;                                     //  |             |topLineDelta
        $this->xmaxM = $this->pageW - $this->margin;                        //  |------------  topLineY
        $this->ymaxM = $this->pageH - $this->margin;                       //  |   IMG
                                                                          //  |
        $this->topLineDelta = 26;                                         //  |------------  botLineY
        $this->topLineY = $this->yminM + $this->topLineDelta;             //  |   LEG
        $this->botLineY = $this->topLineY + $this->imageH;
        
        // Draw Map Image
          
        
	    if($this->imageUrl){
	    		//newh:imageh = neww:imgagew
	    		$newW = $this->pageW-$this->margin*2;
	   		$newH = $newW * $this->imageH/$this->imageW;
	  		$this->botLineY = $this->topLineY + $newH;
	  		
	    		$this->Image($this->imageUrl, $this->xminM, $this->topLineY , $newW,$newH);
	    }
	   // $this->Ln();
	    
	   
	}


}
 
 
 
 ?>