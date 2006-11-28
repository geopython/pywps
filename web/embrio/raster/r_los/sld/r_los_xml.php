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
			  <ColorMapEntry color="#00ff00" quantity="0"/> 
			  <ColorMapEntry color="#00bf3f" quantity="1"/> 
			  <ColorMapEntry color="#007f7f" quantity="255"/> 
			</ColorMap>
        </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor> 
