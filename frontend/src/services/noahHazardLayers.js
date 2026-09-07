// Project NOAH hazard maps, re-published as per-hazard PMTiles files (ODC-ODbL
// licensed) by BetterGov.ph. Loaded directly from HuggingFace over HTTP range
// requests via the `pmtiles` protocol — nothing is downloaded in full.
// https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps
export const NOAH_PMTILES_BASE_URL =
  'https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/layers'

// Each layer's `id` doubles as its PMTiles filename and its vector source-layer
// name (verified directly against the archives' own metadata). `field` is the
// attribute each layer's polygons carry: 1 = Low, 2 = Medium, 3 = High.
export const NOAH_HAZARD_LAYERS = {
  Flood: [
    { id: 'flood_5yr', label: '5-Year Flood', field: 'Var' },
    { id: 'flood_25yr', label: '25-Year Flood', field: 'Var' },
    { id: 'flood_100yr', label: '100-Year Flood', field: 'Var' },
  ],
  Landslide: [{ id: 'landslide', label: 'Landslide Hazard', field: 'HAZ' }],
  'Debris Flow': [{ id: 'debris_flow', label: 'Debris Flow / Alluvial Fan', field: 'HAZ' }],
  'Storm Surge': [
    { id: 'storm_surge_ssa1', label: 'Storm Surge Advisory 1', field: 'HAZ' },
    { id: 'storm_surge_ssa2', label: 'Storm Surge Advisory 2', field: 'HAZ' },
    { id: 'storm_surge_ssa3', label: 'Storm Surge Advisory 3', field: 'HAZ' },
    { id: 'storm_surge_ssa4', label: 'Storm Surge Advisory 4', field: 'HAZ' },
  ],
}

export const HAZARD_SEVERITY_COLORS = {
  1: '#facc15', // Low
  2: '#fb923c', // Medium
  3: '#ef4444', // High
}

export const HAZARD_SEVERITY_LABELS = {
  1: 'Low',
  2: 'Medium',
  3: 'High',
}
