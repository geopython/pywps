<?php
	header("Content-type: application/xhtml+xml");
?>
<StyledLayerDescriptor version="1.0.0">
  <NamedLayer>
    <Name>visibility2</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
        <RasterSymbolizer>
           <ColorMap>
			  <ColorMapEntry color="#00ff00" quantity="22"/> 
			  <ColorMapEntry color="#00bf3f" quantity="30"/> 
			  <ColorMapEntry color="#007f7f" quantity="37"/> 
			  <ColorMapEntry color="#003fbf" quantity="45"/> 
			  <ColorMapEntry color="#0000ff" quantity="52"/>
			  <ColorMapEntry color="#000000" quantity="60"/>
			</ColorMap>
        </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor> 
