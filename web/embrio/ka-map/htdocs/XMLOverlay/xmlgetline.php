<?php
/*
 * Created on 13-feb-2006
 *
 * To change the template for this generated file go to
 * Window - Preferences - PHPeclipse - PHP - Code Templates
 */

header("Content-Type: text/xml");
header("Cache-Control: no-store, no-cache, must-revalidate");

echo '<?xml version="1.0" encoding="UTF-8"?>';
?>

<kml xmlns="http://earth.google.com/kml/2.0">
<Placemark>
  <description>Transparent green wall with yellow outlines</description>
  <name>Absolute Extruded</name>
  <LookAt>
    <longitude>-112.2643334742529</longitude>
    <latitude>36.08563154742419</latitude>
    <range>4451.842204068102</range>
    <tilt>44.61038665812578</tilt>
    <heading>-125.7518698668815</heading>
  </LookAt>
  <visibility>1</visibility>
  <open>0</open>
  <Style>
    <LineStyle>
      <color>ff00ffff</color>
    </LineStyle>
    <PolyStyle>
      <color>7f00ff00</color>
    </PolyStyle>
  </Style>
  <LineString>
    <extrude>1</extrude>
    <tessellate>1</tessellate>
    <altitudeMode>absolute</altitudeMode>
    <coordinates>
        -112.2550785337791,36.07954952145647,2357
        -112.2549277039738,36.08117083492122,2357
        -112.2552505069063,36.08260761307279,2357
        -112.2564540158376,36.08395660588506,2357
        -112.2580238976449,36.08511401044813,2357
        -112.2595218489022,36.08584355239394,2357
        -112.2608216347552,36.08612634548589,2357
        -112.262073428656,36.08626019085147,2357
        -112.2633204928495,36.08621519860091,2357
        -112.2644963846444,36.08627897945274,2357
        -112.2656969554589,36.08649599090644,2357
    </coordinates>
  </LineString>
</Placemark>
</kml>