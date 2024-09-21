# Changelog

## 1.0.19 - 2024-09-21

_Download of collected data donations is only possible through the API not through the admin interface. 
Fix and comprehensive documentation will be released in a subsequent version._

### Fixed
- Fixed mobile layout of matrix question items ([`5e87ac5`](https://github.com/uzh/ddm/commit/5e87ac5).


## 1.0.18 - 2024-09-19

_Download of collected data donations is only possible through the API not through the admin interface. 
Fix and comprehensive documentation will be released in a subsequent version._

### Changed
- Questionnaire: Optimize mobile layout of matrix questions and semantic differential type questions. ([`b1607e7`](https://github.com/uzh/ddm/commit/b1607e7), 
[`0c60352`](https://github.com/uzh/ddm/commit/0c60352), [`b6b9b58`](https://github.com/uzh/ddm/commit/b6b9b58))
- Questionnaire: Jump to top of page after clicking on 'next page'. ([`fb55c10`](https://github.com/uzh/ddm/commit/fb55c10))
- Allow customization of briefing consent labels through html. ([`32d7c59`](https://github.com/uzh/ddm/commit/32d7c59))


## 1.0.17 - 2024-07-29

_Download of collected data donations is only possible through the API not through the admin interface. 
Fix and comprehensive documentation will be released in a subsequent version._

### Changed
- Hide instruction steps bar if only one instruction page is defined. ([`600ba44`](https://github.com/uzh/ddm/commit/600ba44))
- Updated citation. ([`2a23537`](https://github.com/uzh/ddm/commit/2a23537))

### Fixed
- Remove deprecated 'ddm_graph' template tag from question rendering. ([`a3881d5`](https://github.com/uzh/ddm/commit/a3881d5))


## 1.0.16 - 2024-07-19

_Questionnaire was not working in this version due to the inclusion of a deprecated template tag (see fix in v1.0.17)._ 

### Changed

- Improve robustness of extraction operators: ([`5b3a0af`](https://github.com/uzh/ddm/commit/5b3a0af), [`855796f`](https://github.com/uzh/ddm/commit/855796f)) 

    - Detect and convert date-strings (in ISO, RFC2822, or HTTP format) to date objects for greater/smaller-comparisons.
    - Detect and convert numeric-strings to numbers for 'greater/smaller'-comparisons.
    - Exclude strings from 'greater/smaller'-comparisons.
    - Convert all variable types to string before regex comparison functions.
- Update appearance of donation instructions. ([`8cb4d79`](https://github.com/uzh/ddm/commit/8cb4d79), [`0b90ea2`](https://github.com/uzh/ddm/commit/0b90ea2))
- Limit the number of times an error with the same code is posted in an upload attempt from the participation interface to the server to 5. ([`56d30ff`](https://github.com/uzh/ddm/commit/56d30ff))
- Display extraction rules ordered according to the execution order (instead of their IDs). ([`776b384`](https://github.com/uzh/ddm/commit/776b384))
- Improve clarity of administration interface by adding collapsibles for additional information. ([`6a851d2`](https://github.com/uzh/ddm/commit/6a851d2), [`0745f6c`](https://github.com/uzh/ddm/commit/0745f6c))
- Change `DonationProject.date_created` to readonly in admin view. ([`a851042`](https://github.com/uzh/ddm/commit/a851042))


### Added

- Add option for "all-in-one consent" to File Uploader. ([`e0b78c7`](https://github.com/uzh/ddm/commit/e0b78c7))
- Add description of extraction operators to documentation. ([`a4810c1`](https://github.com/uzh/ddm/commit/a4810c1))
- Add three new types of extraction errors related to regex extraction operators. ([`4b6152e`](https://github.com/uzh/ddm/commit/4b6152e))
- Add tests for vue extraction functions. ([`4bad2c7`](https://github.com/uzh/ddm/commit/4bad2c7),[`eb0de44`](https://github.com/uzh/ddm/commit/eb0de44))

### Removed

- Remove the `get_simple_bar_plot` template tag and bokeh dependency. ([`57696d6`](https://github.com/uzh/ddm/commit/57696d6))

### Fixed

- Change type of `EventLogEntry.description` from CharField to TextField to allow the posting of longer event descriptions. ([`d0d1c7d`](https://github.com/uzh/ddm/commit/d0d1c7d))
- Start data entry count from 1 instead of 0 in the data donation feedback navigation. ([`88e9295`](https://github.com/uzh/ddm/commit/88e9295)) 
- Fix bug that has limited the number of extraction rules to 10 and remove this limitation. ([`d9ef58c`](https://github.com/uzh/ddm/commit/d9ef58c))
