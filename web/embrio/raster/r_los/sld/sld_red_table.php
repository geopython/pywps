<?php
	header("Content-type: application/xhtml+xml");
?>
<StyledLayerDescriptor version="1.0.0">
	<!-- raster sample -->
	<NamedLayer>
		<Name>visibility2</Name>
		<UserStyle>
			<FeatureTypeStyle>
				<Rule>
					<RasterSymbolizer>
						<ColorMap>
							<ColorMapEntry color="#11ffff" quantity="1"/>
							<ColorMapEntry color="#22ffff" quantity="15"/>
							<ColorMapEntry color="#33ffff" quantity="30"/>
							<ColorMapEntry color="#55ffff" quantity="45"/>
							<ColorMapEntry color="#77ffff" quantity="60"/>
							<ColorMapEntry color="#99ffff" quantity="75"/>
							<ColorMapEntry color="#aaffff" quantity="82"/>
							<ColorMapEntry color="#ccffff" quantity="90"/>
							<ColorMapEntry color="#aaffff" quantity="97"/>
							<ColorMapEntry color="#99ffff" quantity="105"/>
							<ColorMapEntry color="#77ffff" quantity="120"/>
							<ColorMapEntry color="#55ffff" quantity="135"/>
							<ColorMapEntry color="#33ffff" quantity="150"/>
							<ColorMapEntry color="#22ffff" quantity="165"/>
							<ColorMapEntry color="#11ffff" quantity="180"/>
						</ColorMap>
					</RasterSymbolizer>
				</Rule>
			</FeatureTypeStyle>
		</UserStyle>
	</NamedLayer>

	<!-- vector: polygon sample -->
	<NamedLayer>
		<Name>buffer</Name>
		<UserStyle>
			<Title>buffer</Title>
			<FeatureTypeStyle>
				<Rule>
					<PolygonSymbolizer>
						<Geometry>
							<PropertyName>the_area</PropertyName>
						</Geometry>
						<Fill>
							<CssParameter name="fill">#ff0000</CssParameter>
						</Fill>
						<Stroke>
							<CssParameter name="stroke">#0000ff</CssParameter>
							<CssParameter name="stroke-width">2.0</CssParameter>
						</Stroke>
					</PolygonSymbolizer>
				</Rule>
			</FeatureTypeStyle>
		</UserStyle>
	</NamedLayer>

	<!-- vector: Point sample -->
	<NamedLayer>
		<Name>WorldPOI</Name>
		<UserStyle>
			<Title>xxx</Title>
			<FeatureTypeStyle>
				<Rule>
					<PointSymbolizer>
						<Geometry>
							<PropertyName>locatedAt</PropertyName>
						</Geometry>
						<Graphic>
							<Mark>
								<WellKnownName>star</WellKnownName>
								<Fill>
									<CssParameter name="fill">#ff0000</CssParameter>
								</Fill>
							</Mark>
							<Size>10.0</Size>
						</Graphic>
					</PointSymbolizer>
				</Rule>
			</FeatureTypeStyle>
		</UserStyle>
	</NamedLayer>

	<!-- vector: Line sample 1 (dashed line) -->
	<NamedLayer>
		<Name>shortestpath</Name>
		<UserStyle>
			<Title>xxx</Title>
			<FeatureTypeStyle>
				<Rule>
					<LineSymbolizer>
						<Geometry>
							<PropertyName>center-line</PropertyName>
						</Geometry>
						<Stroke>
							<CssParameter name="stroke">#0000ff</CssParameter>
							<CssParameter name="stroke-width">3.0</CssParameter>
							<CssParameter name="stroke-dasharray">10.0 5 5 10</CssParameter>
						</Stroke>
					</LineSymbolizer>
				</Rule>
			</FeatureTypeStyle>
		</UserStyle>
	</NamedLayer>

	<!-- vector: Line sample 2 (simple line) -->
	<NamedLayer>
		<Name>minorcostpath</Name>
		<UserStyle>
			<Title>xxx</Title>
			<FeatureTypeStyle>
				<Rule>
					<LineSymbolizer>
						<Geometry>
							<PropertyName>center-line</PropertyName>
						</Geometry>
						<Stroke>
							<CssParameter name="stroke">#0000ff</CssParameter>
						</Stroke>
					</LineSymbolizer>
				</Rule>
			</FeatureTypeStyle>
		</UserStyle>
	</NamedLayer>
</StyledLayerDescriptor> 
