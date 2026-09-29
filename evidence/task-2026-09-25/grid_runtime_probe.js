/** Grid/support probe. Run in the Earth Engine Code Editor.
 * Console records are JSON prefixed GRID_PROBE; each evaluation retains its error.
 * Geometry uses synthetic rasters. Final checks read public Sentinel-2 bands at
 * one unverified development point, not reference imagery or the holdout.
 * No site verification, gate verdict, threshold change, or export is performed.
 * Executed evidence: results/earth_engine_runtime_2026-09-29.json.
 */
var ANALYSIS_CRS = 'EPSG:3857';
var ANALYSIS_SCALE_M = 10;
var metric = ee.Projection(ANALYSIS_CRS); // unscaled projected metres for geometry
// Obtain the delivered affine exactly as the production helper does, including y sign.
var grid = ee.Image.constant(0).reproject({crs: ANALYSIS_CRS,
  scale: ANALYSIS_SCALE_M}).projection();
var PROBE_POINTS = {
  'dev-01-braided-lat': ee.Geometry.Point([102.3, 47.3]),
  'equator-control': ee.Geometry.Point([102.3, 0])
};

function report(label, value) {
  value.evaluate(function (result, error) {
    print('GRID_PROBE ' + JSON.stringify({label: label,
      status: error ? 'ERROR' : 'OK', value: error ? null : result,
      error: error || null}));
  });
}

function first(image, point) {
  return image.reduceRegion({reducer: ee.Reducer.first(), geometry: point,
    crs: grid, maxPixels: 1000000});
}

function reportGeometry(label, point) {
  var xy = point.transform(metric, 0.001).coordinates();
  var x = ee.Number(xy.get(0)).divide(10).floor().multiply(10);
  var y = ee.Number(xy.get(1)).divide(10).floor().multiply(10);
  var center = ee.Geometry.Point([x.add(5), y.add(5)], metric);
  var east = ee.Geometry.Point([x.add(15), y.add(5)], metric);
  var north = ee.Geometry.Point([x.add(5), y.add(15)], metric);
  // A grid-aligned non-square rectangle: ten columns by five rows, exactly 50 cells.
  var box = ee.Geometry.Rectangle([x, y, x.add(100), y.add(50)], metric, false);
  var stats = ee.Image.pixelArea().rename('area').addBands(ee.Image.constant(1).rename('cells'))
    .reduceRegion({reducer: ee.Reducer.sum(), geometry: box, crs: grid, maxPixels: 1000000});
  report(label + ':geometry', ee.Dictionary({
    crs: grid.crs(), transform: grid.transform(), nominal_scale_m: grid.nominalScale(),
    center_lonlat: center.transform('EPSG:4326', 0.001).coordinates(),
    east_lonlat: east.transform('EPSG:4326', 0.001).coordinates(),
    north_lonlat: north.transform('EPSG:4326', 0.001).coordinates(),
    east_distance_m: center.distance(east, 0.001),
    north_distance_m: center.distance(north, 0.001),
    pixel_area_m2: first(ee.Image.pixelArea(), center).get('area'),
    footprint_projected_bounds: ee.List([x, y, x.add(100), y.add(50)]),
    footprint_area_m2: box.area(0.001), raster_footprint: stats
  }));

  // Observe a metre-kernel's actual support on the analysis grid using an impulse.
  var coords = ee.Image.pixelCoordinates(grid);
  var cell = first(coords, center);
  var dx = coords.select('x').subtract(ee.Number(cell.get('x')));
  var dy = coords.select('y').subtract(ee.Number(cell.get('y')));
  var impulse = dx.eq(0).and(dy.eq(0));
  var outer = impulse.reduceNeighborhood(ee.Reducer.sum(),
    ee.Kernel.circle({radius: 800, units: 'meters', normalize: false}));
  var inner = impulse.reduceNeighborhood(ee.Reducer.sum(),
    ee.Kernel.circle({radius: 200, units: 'meters', normalize: false}));
  var ring = outer.subtract(inner).gt(0).rename('ring');
  var region = ee.Geometry.Rectangle([x.subtract(1500), y.subtract(1500),
    x.add(1500), y.add(1500)], metric, false);
  var support = ring.addBands(outer.gt(0).rename('outer')).addBands(inner.gt(0).rename('inner'))
    .reduceRegion({reducer: ee.Reducer.sum(), geometry: region, crs: grid, maxPixels: 1000000});
  var radial = dx.hypot(dy).multiply(10).rename('radius_projected_m').updateMask(ring);
  report(label + ':ring', ee.Dictionary({counts: support,
    radial_extent: radial.reduceRegion({reducer: ee.Reducer.minMax(), geometry: region,
      crs: grid, maxPixels: 1000000})}));
}

Object.keys(PROBE_POINTS).forEach(function (label) {
  reportGeometry(label, PROBE_POINTS[label]);
});

// Preserve the original prepared collection, dates and development point.
// Evaluate each order separately so an order-1 failure cannot hide order 2.
var point = PROBE_POINTS['dev-01-braided-lat'];
var collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(point).filterDate('2023-07-01', '2023-08-01')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40));
var source = ee.Image(collection.sort('system:index').first());
var bands = collection.select(['B4', 'B8']);
var composite = bands.median();
var order1 = composite.resample('bilinear').reproject(grid);
var order2 = bands.map(function (img) { return img.resample('bilinear'); }).median().reproject(grid);
report('resampling:metadata', ee.Dictionary({scene_count: collection.size(),
  scene_ids: collection.aggregate_array('system:index'),
  source_crs: source.select('B4').projection().crs(),
  composite_crs: composite.select('B4').projection().crs(),
  source_B4_transform: source.select('B4').projection().transform(),
  source_B11_transform: source.select('B11').projection().transform(),
  source_B4_nominal_m: source.select('B4').projection().nominalScale(),
  source_B11_nominal_m: source.select('B11').projection().nominalScale()}));
report('resampling:composite_then_resample', first(order1, point));
report('resampling:resample_then_composite', first(order2, point));
report('resampling:difference', first(order1.subtract(order2), point));
