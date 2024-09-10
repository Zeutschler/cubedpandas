# Changelog

All notable changes to the CubedPandas project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Categories: Added, Changed, Fixed, Deprecated, Removed, Security, Fixed, Security

## [0.2.32] - in progress

### Added

- Class DateText added to resolve date keywords.
- Added cubed() method to Context to create new cube from filtered cube.

### Changed

### Fixed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.31] - 2024-09-09

### Changed

- Added automated testing for real-world data sets located in`tests/datasets`.
- Added first version of time series intelligence. Needs full redesign.
- Added support for boolean string keywords as member names.
  True values: `true`, `t`, `1`, `yes`, `y`, `on`, `1`, `active`, `enabled`, `ok`, `done`
  False values: everything else
- Added support for `in` operator = `__contains__` method on DimensionContext to test
  if a member is contained in a dimension.

### Fixed

- NaN member names and values not properly recognized, #non.
- Member names containing `,` delimiter not properly recognized, #non.
- Numpy `__array_priority__` attribute calls not recognized and handled, #non.
- MkDocs documentation build on GitHub failing. Switched to static upload as a temp. solution, #non.

## Earlier changes

Earlier changes, before [0.2.30], are not documented as they to related to  
a comprehensive redesign and complete refactoring of the initial design.