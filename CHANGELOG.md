# Changelog

This project follows semantic versioning.

Possible log types:

- `[added]` for new features.
- `[changed]` for changes in existing functionality.
- `[deprecated]` for once-stable features removed in upcoming releases.
- `[removed]` for deprecated features removed in this release.
- `[fixed]` for any bug fixes.
- `[security]` to invite users to upgrade in case of vulnerabilities.

## [Unreleased]

 - ...

## [1.2.0] - 2024-10-16

 - [changed] Improve display by using rich instead of texttable (#37)
 - [changed] Remove "Occupancy" column which hasn't been provided by the API since 2017 (#38)

## [1.1.2] - 2019-10-09

 - No changes, new release to fix a packaging problem

## [1.1.1] - 2019-09-12

 - [fixed] Consistent train / bus numbers (#34)

## [1.1.0] - 2019-08-17

 - [added] Support being called with two arguments (#33)
 - [removed] Drop Python 2 and 3.4 support (#30)
 - [changed] Relax texttable dependency constraint (#29)

## [1.0.0] - 2017-09-10

 - [added] Support for HTTP proxies (#21)
 - [added] Display train numbers (#22)
 - [added] Date parsing (#10) and support of time without columns (#17)
 - [changed] Improve display by using texttable
 - [changed] Improve code modularity, use argparse for argument parsing
 - [fixed] Python 2 and 3 bugfixes. Tests using nose2. Removed dependency on envoy.
 - [fixed] Handle connections without platform (#23)

## [0.2.3] - 2014-09-18

 - [changed] Improved testing using tox
 - [added] Allow requests 2.x

## [0.2.2] - 2013-09-20

 - [changed] Improved docs
 - [changed] Improved testing
 - [fixed] Potential bug with stdout encoding
 - [changed] Updated requirements

## [0.2.1] - 2013-02-13

 - [added] Display walks in "platform" and "travel with" fields

## [0.2.0] - 2013-02-13

 - Initial Python 3 compatible release.
   No changelog information before this.

[Unreleased]: https://github.com/dbrgn/fahrplan/compare/v1.1.3...HEAD
[1.1.3]: https://github.com/dbrgn/fahrplan/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/dbrgn/fahrplan/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/dbrgn/fahrplan/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/dbrgn/fahrplan/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dbrgn/fahrplan/compare/v0.2.3...v1.0.0
[0.2.3]: https://github.com/dbrgn/fahrplan/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/dbrgn/fahrplan/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/dbrgn/fahrplan/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/dbrgn/fahrplan/compare/cf24396...v0.2.0
