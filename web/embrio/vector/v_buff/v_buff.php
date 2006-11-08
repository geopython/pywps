<?php

// Parametri di default

$script_name = "buffer.php";
$map_path = "/home/geko/progetti/mapfile/";
$map_file = "buffer.map";
$img_path = "/var/www/localhost/htdocs/tmp/";
$pywps_path = "/var/www/localhost/htdocs/wps/wpsoutputs/";

// Crea l'oggetto map per il mapfile specificato

	$map = ms_newMapObj($map_path.$map_file);

// Creo la prima immagine
    
	$map_id = sprintf("%0.6d",rand(0,999999));
        $image_name = "pywps".$map_id.".png";
        $image_url="/tmp/".$image_name;
        $image=$map->draw();
        $image->saveImage($img_path.$image_name);

// Il form viene inviato

if (isset($_POST['submit']))
    	{

//Crea il file contenente le coordinate
        
	$input_id = sprintf("%0.6d",rand(0,999999));
        $input_name = "input".$input_id.".txt";
        $input_url="/var/www/localhost/htdocs/tmp/".$input_name;
  	$x=$_POST['x'];
	$y=$_POST['y'];
        $array_cord = array($x,$y);
        $coord = implode(",", $array_cord);
	file_put_contents($input_url,$coord);

//Crea la richiesta per pywps
    
   $stringa_query = "http://localhost/cgi-bin/wps.py?service=wps&version=0.4.0&request=Execute&Identifier=buffer&";
    $array = array('point',$input_url,'radius',$_POST['radius']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";
    #var_dump($stringa_query);
    #die();

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
        $layer->set('name', "buffer");
	$layer->set('status', MS_DEFAULT );
	$layer->set('connection', $pywps_path);
	$layer->set('type', MS_LAYER_POLYGON);
  	$layer->set('transparency',"50");
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
    $map->save("/var/www/localhost/htdocs/tmp/mapfile_buffer.map");
}

?>
<html>
<head><title>Test for buffer function</title></head>
<body bgcolor="#E6E6E6">

 

  <table width="80%" border="1">

   <tr><td width="60%" rowspan="6">
        
	<input  name="img" type="image" src="<?php echo $image_url;?>"
         	width=640 height=480 border=2></td>

       <td width="40%" align="left" colspan="3">
        <form method=post action="<?php echo $script_name;?>">

	GRASS Buffer module
	<p>
	For this test please input this value (javascript check are not jet implemented)
	</p> 
	<p>
	x=594790 y=4921822  
    	</p>
	<p>
	Radius=1000
    	</p>
	<p>
         X:<br />
         	<input type=text name="x" size="20" maxlength="40" value="" />
    	</p>
	
	<p>
         Y:<br />
         <input type=text name="y" size="20" maxlength="40" value="" />
    	</p>
    
	<p>
        
	<p>
         Radius:<br />
         	<input type=text name="radius" size="20" maxlength="40" value="" />
    	</p>
	
	
	<input type="submit" name = "submit" value="Go!" /> </td></tr>

   
  </table>
 </form>
</body>
</html>
	

?>
