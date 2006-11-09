<?php
 /**********************************************************************
 *
 * purpose: a connector v.net.path GRASS function
 *
 * authors: Luca Casagrande (luca.casagrande@gmail.com) and Lorenzo Becchi (lorenzo@ominiverdi.com)
 *
 * TODO:
 *   - a lot...
 *
 **********************************************************************
 *
 * Copyright (C) 2006 ominiverdi.org
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 **********************************************************************/
 
// Parametri di default

if(file_exists('include/config.php')) include('include/config.php');
else die('create your include/config.php using include/config.php.dist as template');


// Crea l'oggetto map per il mapfile specificato

$map = ms_newMapObj($map_path.$map_file);



// Crea la prima immagine
	$map_id = sprintf("%0.6d",rand(0,999999));
	$image_name = "pywps".$map_id.".png";
	$image_url=$img_rel_path.$image_name;
	$image=$map->draw();
	$image->saveImage($img_path.$image_name);

// Il form viene inviato

if (isset($_POST['submit']))
    {
    
    // Verifica l esattezza dei parametri inseriti
    

if ($_POST['cost'] != 0) {
      die ("Sorry in this example, the path can't be selected using a cost parameter.Please assign 0 to the cost form");
}  
elseif ($_POST['x1value']  < 589435 |  $_POST['y1value']  < 4914010 | $_POST['x1value']  > 609527 |  $_POST['y1value'] >  4928060) { 
	die("The first point it's outside the extent. Please use suggested value.");
} elseif ($_POST['x2value']  < 589435 |  $_POST['y2value']  < 4914010 | $_POST['x2value']  > 609527 |  $_POST['y2value'] >  4928060) { 
	die("The second point it's outside the extent. Please use suggested value.");
}  else    {
    $stringa_query = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=shortestpath2&";
    #$stringa_query = "http://localhost/cgi-bin/wps.py?service=wps&version=0.4.0&request=Execute&Identifier=shortestpath2&";
    $array = array('x1', $_POST['x1value'],'y1',$_POST['y1value'],'x2', $_POST['x2value'],'y2',$_POST['y2value'],'cost',$_POST['cost']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";

//Indirizzo completo terminato, estraggo il nome del file    

    $dom = new DOMDocument();
    $dom->load($stringa_query);
    $CVR = $dom->getElementsByTagName('ComplexValueReference');
    $nodo = $CVR->item(0)->getAttribute('reference');
    
// Estrae il nome del file
    $aNodo = explode('/',$nodo);
    $filename = end($aNodo);
    $pywps_outputPath.=$filename;

// Aggiorna il mapfile con il file creato e visualizza il layer
        $layer = ms_newLayerObj($map);
        $layer->set('name', "path");
	$layer->set('status', MS_DEFAULT );
	$layer->set('connection', $pywps_outputPath);
	$layer->set('type', MS_LAYER_LINE);
  	$layer->set('connectiontype',MS_OGR);  
        $class = ms_newClassObj($layer);
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
	$style->color->setRGB( 255,0,0);
        
// Creo l'immagine
    
    $map_id = sprintf("%0.6d",rand(0,999999));
    $image_name = "pywps".$map_id.".png";
    $image_url=$img_rel_path.$image_name;
    $image=$map->draw();
    $image->saveImage($img_path.$image_name);
//non dovrebbe esserci bisogno di salvare questo mapfile
    $map->save($img_path."/mapfile_path.map");
}
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
	x1=590436 y1=4927222  
    	</p>
	<p>
	x2=608598 y2=4915649 
    	</p>
	<p>
	Cost=0  
    	</p>
	<p>
         X1:<br />
         	<input type=text name="x1value" size="20" maxlength="6" value="590436" />
    	</p>
	
	<p>
         Y1:<br />
         <input type=text name="y1value" size="20" maxlength="7" value="4927222" />
    	</p>
    
	<p>
        
	<p>
         X2:<br />
         	<input type=text name="x2value" size="20" maxlength="6" value="608598" />
    	</p>
	
	<p>
         Y2:<br />
         <input type=text name="y2value" size="20" maxlength="7" value="4915649" />
    	</p>
    
	<p>
	Cost:<br />
         	<input type=text name="cost" size="20" maxlength="1" value="0" />
    	</p>
	
	<input type="submit" name = "submit" value="Go!" /> </td></tr>

   
  </table>
 </form>
</body>
</html>
