# `randonneur_data` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### [0.7.1] - 2025-11-05

* Add ecoinvent 3.11 to 3.12 mappings

## [0.7] - 2025-10-29

* Move default compression to GZ to allow for native browser decoding

### [0.6.2] - 2025-10-06

* Update ecoinvent - EF 3.1 mappings to align with energy densities expected in EF 3.1

### [0.6.1] - 2025-10-03

* Add ecoinvent - EF 3.1 mappings

## [0.6] - 2025-03-25

* Add ecoinvent 3.10.1-3.11 mappings
* Compatibility with upstream `randonneur` changes

### [0.5.5] - 2025-02-21

* Minor fixes for SimaPro 9 - ecoinvent 3.8 manual mappings

### [0.5.4] - 2024-12-02

* Add Agrifootprint transformations to ecoinvent unmodified names

### [0.5.3] - 2024-11-27

* Removed mappings from Agribalyse which lied about being ecoinvent processes

### [0.5.2] - 2024-11-26

* Updated mappings from Agribalyse 3.1.1

### [0.5.1] - 2024-11-26

* Updated mappings from Agribalyse 3.1.1

## [0.5] - 2024-10-15

* [#5 - SimaPro correspondence files include unit which can replace units with conversion](https://github.com/brightway-lca/randonneur_data/issues/5)
* Fix ecoinvent migrations making incorrect unit conversions

## [0.4.1] - 2024-10-14

* Add additional Agrifootprint transformation

## [0.4] - 2024-10-14

* Fixed bugs with custom registry paths
* Added transformations for Agribalyse and Agrifootprint

## [0.3] - 2024-09-26

* Added lots of new data transformations

### [0.2.1] - 2024-09-05

* Added `.sample()` and `.schema()` convenience functions
* Added some more SimaPro mapping

## [0.2] - 2024-09-02

* Add validation when adding data
* Updated imperfect migrations
* Added many migration files

### [0.1.2] - 2024-08-15

* Update ecoinvent version migrations with even moar patches

### [0.1.1] - 2024-08-13

* Update ecoinvent version migrations with additional patches

## [0.1] - 2024-08-13

Initial public release
