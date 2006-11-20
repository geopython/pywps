<?php
/*
 * Created on 13-feb-2006
 *
 * To change the template for this generated file go to
 * Window - Preferences - PHPeclipse - PHP - Code Templates
 */

header("Content-Type: text/xml");
header("Cache-Control: no-store, no-cache, must-revalidate");
echo '<?xml version="1.0" encoding="UTF-8"?>'

?>


<kml xmlns="http://earth.google.com/kml/2.0">
<Placemark>
  <name>Three objects Polygon</name>
  <description>Click me to see my description!</description>
  <LookAt>
    <longitude>-77.05580139178142</longitude>
    <latitude>38.870832443487</latitude>
    <range>742.0552506670548</range>
    <tilt>48.09646074797388</tilt>
    <heading>59.88865561738225</heading>
  </LookAt>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
            -20,40,0 
            20,40,0 
            20,-40,0 
            -20,-40,0 
            -20,40,0 
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
    <innerBoundaryIs>
      <LinearRing>
        <coordinates>
             -15,30,0 
            15,30,0 
            15,-30,0 
            -15,-30,0 
            -15,30,0 
        </coordinates>
      </LinearRing>
    </innerBoundaryIs>
  </Polygon>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
            -90,90,0 
            -90,-90,0 
            90,-90,0 
            90,-70,0 
            -70,-70,0 
            -70,90,0 
            -90,90,0 
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
    
  </Polygon>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
           -10,20,0
            10,20,0
            10,-20,0
            -10,-20,0
            -10,20,0
         </coordinates>
      </LinearRing>
    </outerBoundaryIs>
    
  </Polygon>
</Placemark>
</kml>
<?
/*
GPolyline

A polyline represents a vector polyline overlay on the map. 
A polyline is drawn with the vector drawing facilities of the browser 
if they are available or an image overlay from Google servers otherwise.

Constructor -> GPolyline(points, color?, weight?, opacity?)
Description -> Constructs a polyline from the given array of latitude/longitude points. 
color is a hex HTML color (such as "#0000ff"), weight is an integer representing the width of the 
line in pixels, and opacity is a float between 0 and 1.
Params -> outlinecolor, size, (symbol,symbolname)
*/
?>	