<?php

// Parametri di default

$script_name = "network.php";
$map_path = "/home/geko/progetti/pywps/";
$map_file = "spearfish_net.map";
$img_path = "/var/www/localhost/htdocs/tmp/";
$pywps_path = "/var/www/localhost/htdocs/wps/wpsoutputs/";

// Crea l'oggetto map per il mapfile specificato

$map = ms_newMapObj($map_path.$map_file);



// Crea la prima immagine
    
	$map_id = sprintf("%0.6d",rand(0,999999));
        $image_name = "pywps".$map_id.".png";
        $image_url="/tmp/".$image_name;
        $image=$map->draw();
        $image->saveImage($img_path.$image_name);

// Il form viene inviato

if (isset($_POST['submit']))
    {
    
    $stringa_query = "http://localhost/cgi-bin/wps.py?service=wps&version=0.4.0&request=Execute&Identifier=shortestpath2&";
    $array = array('x1', $_POST['x1value'],'y1',$_POST['y1value'],'x2', $_POST['x2value'],'y2',$_POST['y2value'],'cost',$_POST['cost']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";

//L'indirizzo completo è terminato, estraggo il nome del file    

    $dom = new DOMDocument();
    $dom->load($stringa_query);
    $CVR = $dom->getElementsByTagName('ComplexValueReference');
    $nodo = $CVR->item(0)->getAttribute('reference');
    
// Estrae il nome del file
    $aNodo = explode('/',$nodo);
    $filename = end($aNodo);
    $pywps_path.=$filename;

// Aggiorna il mapfile con il file creato e visualizza il layer
        $layer = ms_newLayerObj($map);
        $layer->set('name', "path");
	$layer->set('status', MS_DEFAULT );
	$layer->set('connection', $pywps_path);
	$layer->set('type', MS_LAYER_LINE);
  	$layer->set('connectiontype',MS_OGR);  
        $class = ms_newClassObj($layer);
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
	$style->color->setRGB( 255,0,0);
        

        


// Creo l'immagine

    $map_id = sprintf("%0.6d",rand(0,999999));
    $image_name = "pywps".$map_id.".png";
    $image_url="/tmp/".$image_name;
    $image=$map->draw();
    $image->saveImage($img_path.$image_name);
    $map->save("/var/www/localhost/htdocs/tmp/mapfile_net.map");
}

?>
<html>
<head><title>Samplepage</title></head>
<body bgcolor="#E6E6E6">

 

  <table width="80%" border="1">

   <tr><td width="60%" rowspan="6">
        
	<input  name="img" type="image" src="<?php echo $image_url;?>"
         	width=640 height=480 border=2></td>

       <td width="40%" align="left" colspan="3">
        <form method=post action="<?php echo $script_name;?>">

	GRASS Shortest path module
	<p>
	For this test please input this value (javascript check are not jet implemented)
	</p> 
	<p>
	x1=594790 y1=4921822  
    	</p>
	<p>
	x2=596367 y2=4924878 
    	</p>
	<p>
	Cost=0  
    	</p>
	<p>
         X1:<br />
         	<input type=text name="x1value" size="20" maxlength="40" value="" />
    	</p>
	
	<p>
         Y1:<br />
         <input type=text name="y1value" size="20" maxlength="40" value="" />
    	</p>
    
	<p>
        
	<p>
         X2:<br />
         	<input type=text name="x2value" size="20" maxlength="40" value="" />
    	</p>
	
	<p>
         Y2:<br />
         <input type=text name="y2value" size="20" maxlength="40" value="" />
    	</p>
    
	<p>
	Cost:<br />
         	<input type=text name="cost" size="20" maxlength="40" value="" />
    	</p>
	
	<input type="submit" name = "submit" value="Go!" /> </td></tr>

   
  </table>
 </form>
</body>
</html>
