# EOMAP Extension

- **Title:** EOMAP
- **Identifier:** <https://eomapcompany.github.io/stac-extension-eomap/v0.1.0/schema.json>
- **Field Name Prefix:** eomap
- **Scope:** Item, Collection
- **Extension [Maturity Classification](https://github.com/radiantearth/stac-spec/tree/master/extensions/README.md#extension-maturity):** Proposal
- **Owner**: EOMAP GmbH & Co. KG

Fields for EOMAP's earth observation products: satellite-derived bathymetry deliveries and water quality time series.
It is used together with the standard extensions, which describe everything they can:

| Information | Use |
|---|---|
| CRS of a file | [projection](https://github.com/stac-extensions/projection) `proj:code` |
| Data type, nodata, unit, scale of bands | [raster](https://github.com/stac-extensions/raster) `raster:bands` |
| Software and versions, lineage | [processing](https://github.com/stac-extensions/processing) `processing:software`, `processing:lineage` |
| File size, checksum | [file](https://github.com/stac-extensions/file) |
| Classes of classified products | [classification](https://github.com/stac-extensions/classification) |
| Satellite and instrument | STAC common metadata `constellation`, `platform`, `instruments`, `gsd` |

This extension adds what none of them covers: EOMAP product codes, the sensors as EOMAP identifies them, vertical
datums with tide stations, accuracies, processing corrections and the access tags used by EOMAP's catalogue.

- Examples: [Item](examples/item.json), [Collection](examples/collection.json)
- [JSON Schema](json-schema/schema.json)
- Vocabularies: [products](vocabulary/products.json), [sensors](vocabulary/sensors.json),
  [vertical datums](vocabulary/vertical-datums.json)
- [Changelog](./CHANGELOG.md)

## Fields

The fields can be used in Item properties, Collections (top level) and Assets.
Any other field starting with `eomap:` is invalid.

| Field Name | Type | Description |
|---|---|---|
| eomap:products | \[string] | Product codes contained (Item, Collection), e.g. `["SDB", "VUC"]`. See [products](#products). |
| eomap:product | string | Product code of an Asset, e.g. `SDB`. |
| eomap:sensors | \[string] | Ids of the sensors the data is derived from, e.g. `["wv3"]`. See [sensors](#sensors). |
| eomap:country_code | string | ISO 3166-1 alpha-3 country code, or an EOMAP region code (`GLO` global, `INT` international waters). |
| eomap:vertical_datum | string | Vertical reference of heights and depths, e.g. `MSL`. See [vertical datums](#vertical-datums). |
| eomap:tide_stations | \[[Tide Station Object](#tide-station-object)] | Tide stations the vertical datum is based on. |
| eomap:horizontal_accuracy | number | Horizontal accuracy in metres (CE90). |
| eomap:vertical_accuracy | number | Vertical accuracy in metres. Omitted where a vertical uncertainty (`VUC`) product describes it per pixel. |
| eomap:corrections | \[string] | Correction modules applied: `noise` (sensor noise), `atm` (atmosphere), `adj` (adjacent land reflectance), `tur` (turbidity), `refr` (water refraction), `gcps` (ground control points), `insitu` (in-situ calibration). |
| eomap:uuid | string | Identifier written into the file: GeoTIFF tag `EOMAP_UUID`, ISO 19139 `fileIdentifier`. Links a file with its metadata. |
| eomap:source | string | System the record was created from: `eoarchive`, `sdbdeliveryapp` or `rastless`. |
| eomap:project_date | string | Delivery date of a project (Collection), `YYYY-MM-DD`. |
| eomap:access | \[string] | **Internal.** Who may see the record: `role#<client>:<role>`, `user#<username>` or `role#public`. Missing or empty means EOMAP-internal only. EOMAP's catalogue removes this field from responses for customers. |
| eomap:qa_flags | \[string] | Issues found while creating the record, for review, e.g. `unknown-sensor`. |

### Tide Station Object

Levels are in metres above chart datum.

| Field Name | Type | Description |
|---|---|---|
| name | string | **REQUIRED.** Name of the station. |
| number | string | Station number. |
| hat | number | Highest astronomical tide. |
| msl | number | Mean sea level. |
| lat | number | Lowest astronomical tide. |
| satrec | number | Water level at the time of the satellite recording. |

## Vocabularies

The vocabularies define the allowed codes. Each entry has a title and optional `aliases`: other spellings found in
EOMAP systems (file names, processing chains, legacy archives). **Matching ignores case and all characters except
letters and digits**, so `WorldView-Legion`, `WorldView Legion` and `WORLDVIEWLEGION` are the same. Producers should
write the id (the key), not an alias. Ids and aliases are unique across a vocabulary (checked in CI).

Codes that are not (yet) in a vocabulary are still valid values; consumers should flag them for review
(`eomap:qa_flags`) rather than reject them, and the vocabulary should then be extended.

### Products

[products.json](vocabulary/products.json): uppercase code → `title`, `family`, `unit` (null when unitless or
classified), optional `description`, `classified`, `aliases`. Families: `bathymetry`, `topography`, `seafloor`,
`reflectance`, `imagery`, `water-quality`, `land`, `shoreline`, `snow`, `atmosphere`, `quality`, `other`.

### Sensors

[sensors.json](vocabulary/sensors.json): lowercase id → `title`, `type` (`optical`, `radar`, `lidar`, `dataset`,
`model`, `uav`, `multi`), and the STAC common metadata `constellation`, `platform` and `instruments` where they are
known. `platform` is only set where the sensor is a single satellite.

### Vertical datums

[vertical-datums.json](vocabulary/vertical-datums.json): code → `title`, optional `aliases`.

## Contributing

Pull requests are welcome. Changes to fields need a new version of the schema (semantic versioning; `0.x` versions
may still change fields). Vocabulary entries can be added in any release.

```bash
uv run pytest    # schema, examples and vocabulary checks
```

A published release is deployed to `https://eomapcompany.github.io/stac-extension-eomap/v<version>/`
(`schema.json` and `vocabulary/*.json`).
