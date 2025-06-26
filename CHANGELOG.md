# Changelog

## 2.1.1

### Fixed

- **Filter Condition Edit Form Showing Unnecessary fields**: Explicitly exclude the filter target question and target item from the form to prevent occasional rendering of these fields.

## 2.1.0 - 2025-06-24

### Added

- **Questionnaire Filtering System**: Introduced comprehensive filtering functionality to show/hide questions and question items based on questionnaire responses, participation variables, and system variables. ([`c0fabd3`](https://github.com/uzh/ddm/commit/c0fabd3), [`d697df6`](https://github.com/uzh/ddm/commit/d697df6), [`7859df2`](https://github.com/uzh/ddm/commit/7859df2), [`2afba85`](https://github.com/uzh/ddm/commit/2afba85), [`4d6d455`](https://github.com/uzh/ddm/commit/4d6d455), [`dc3bfbc`](https://github.com/uzh/ddm/commit/dc3bfbc), [`5ad1da0`](https://github.com/uzh/ddm/commit/5ad1da0), [`1ce6cda`](https://github.com/uzh/ddm/commit/1ce6cda), [`6e4ee77`](https://github.com/uzh/ddm/commit/6e4ee77), [`e45d783`](https://github.com/uzh/ddm/commit/e45d783))
- **Custom Uploader Translations**: Added option to overwrite default uploader translations on a project basis. ([`97f8930`](https://github.com/uzh/ddm/commit/97f8930), [`d961806`](https://github.com/uzh/ddm/commit/d961806), [`da928f0`](https://github.com/uzh/ddm/commit/da928f0))
- **Blueprint Display Control**: Added option to control Blueprint display order in the participation interface. ([`7a16502`](https://github.com/uzh/ddm/commit/7a16502))
- **Enhanced Open Questions**: Added functionality for Open Questions to have multiple items with individual text inputs for each item. ([`0d6b47a`](https://github.com/uzh/ddm/commit/0d6b47a))
- **Matrix Question Improvements**: Added optional heading labels to matrix questions with improved design and responsiveness. ([`e40e817`](https://github.com/uzh/ddm/commit/e40e817))
- **Search Uploaded Data**: Added option for participants to search the data they have uploaded in DDMUploader.

### Changed

- **Uploader Frontend Refactor**: Completely refactored DDM Uploader frontend to improve documentation, reusability, maintainability, and adherence to modern Vue standards. ([`896086a`](https://github.com/uzh/ddm/commit/896086a), [`429a321`](https://github.com/uzh/ddm/commit/429a321), [`a2ea763`](https://github.com/uzh/ddm/commit/a2ea763), [`dd93b6f`](https://github.com/uzh/ddm/commit/dd93b6f))
- **Questionnaire Frontend Refactor**: Moved questionnaire frontend to separate application, updated dependencies, split large files into submodules, and refactored to TypeScript. ([`ba91828`](https://github.com/uzh/ddm/commit/ba91828), [`fea71d7`](https://github.com/uzh/ddm/commit/fea71d7), [`b395bcf`](https://github.com/uzh/ddm/commit/b395bcf), [`38d8c16`](https://github.com/uzh/ddm/commit/38d8c16))
- **Modern Questionnaire Design**: Restyled questionnaire interface with a more modern look and improved responsiveness. ([`19f7dfc`](https://github.com/uzh/ddm/commit/19f7dfc), [`2ce4d4a`](https://github.com/uzh/ddm/commit/2ce4d4a))
- **Enhanced Response Handling**: Updated response serializer to handle both new and old response structures for backward compatibility. ([`26f31ce`](https://github.com/uzh/ddm/commit/26f31ce))
- **Refactored Exception Logs**: Introduced new exception log specifications that contain more information and are more accessible/verbose than the previous exception logs ([`169aa80`](https://github.com/uzh/ddm/commit/169aa80)). 

### Fixed

- **API Token Management**: Fixed API token form to prevent accidentally overwriting existing tokens and resolved errors when deleting active tokens. ([`aca8cc6`](https://github.com/uzh/ddm/commit/aca8cc6))
- **Project Log Export Enhancement**: Fixed table export of project exception and event logs to include all entries and use meaningful filenames. ([`46eb4f2`](https://github.com/uzh/ddm/commit/46eb4f2))
- **Variable Name Validation**: Raise validation error for duplicated variable names to prevent database integrity errors. ([`ebfc2a7`](https://github.com/uzh/ddm/commit/ebfc2a7))
- **Adding First Formset Items**: Show extra form for ScalePoints or QuestionItems when none are displayed to enable adding the first item. ([`100f5c0`](https://github.com/uzh/ddm/commit/100f5c0))

### Improved

- **DDM Exception Logs**: Updated admin view with filter options and additional information. ([`84c0ccb`](https://github.com/uzh/ddm/commit/84c0ccb))
- **Response Export**: Sort columns in questionnaire response export according to current questionnaire order. ([`9d74b60`](https://github.com/uzh/ddm/commit/9d74b60))
- **Documentation**: Updated function docstrings and documentation screenshots. ([`9d2c0af`](https://github.com/uzh/ddm/commit/9d2c0af), [`4c261e6`](https://github.com/uzh/ddm/commit/4c261e6), [`077431b`](https://github.com/uzh/ddm/commit/077431b))
- **Improved Cross-Platform Compatibility**: Replaced Unicode characters with Bootstrap icons for better cross-browser and cross-OS compatibility. ([`b4f2fed`](https://github.com/uzh/ddm/commit/b4f2fed))

### Technical

- **Refactored Scale Points**: Renamed `ScalePoint.add_border` to `ScalePoint.secondary_point` for clarity. ([`eab82e0`](https://github.com/uzh/ddm/commit/eab82e0))
- **Updated Django Settings**: Django settings must be updated to integrate refactored frontend components ([`45105e6`](https://github.com/uzh/ddm/commit/45105e6))

### Migration Guide

To migrate to v2.1.0 from a previous version, the WEBPACK_LOADER configuration must be changed in the Django settings:

Previous:
```
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/vue/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/vue/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}
```

New:
```
WEBPACK_LOADER = {
    'DDM_UPLOADER': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/uploader/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/frontend/uploader/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    },
    'DDM_QUESTIONNAIRE': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/questionnaire/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/frontend/questionnaire/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}
```

Additionally, you will need to run `python manage.py migrate` to apply changes in the database models as well as 
`python manage.py collectstatic` to load newly added static files.


## 2.0.1 - 2025-03-11

### Fixed
- Resolve incorrect status updates causing data display issues when an upload contains failed, all-filtered-out, and successful blueprint extractions at the same time (participation data donation view). ([`6e539b7`](https://github.com/uzh/ddm/commit/6e539b7, [`013e69c`](https://github.com/uzh/ddm/commit/013e69c)
- Instead of adding extra forms to QuestionItem and ScalePoint edit formsets, add button to add extra forms with JavaScript if needed. This prevents validation errors on unneeded extra forms with prefilled values. ([`5ff8503`](https://github.com/uzh/ddm/commit/5ff8503).
- Fix typos in description of responses API. ([`5f51ba1`](https://github.com/uzh/ddm/commit/5f51ba1)

### Update Guide

Run `python manage.py collectstatic` after upgrading to DDM v2.0.1 from a previous version.


## 2.0.0 - 2025-02-27

This release marks a significant update, restructuring the codebase to enhance the maintainability and scalability of DDM. 
The application has been modularized into smaller sub-apps, each focused on a specific aspect of the application logic. 
Additionally, the update includes an improved user interface and user experience, making DDM more accessible to 
both researchers and participants. The accompanying documentation has also been extensively revamped.

**Important:** Due to the comprehensive restructuring, v2.0 introduces breaking changes. 
Upgrading from version 1.x to 2.x will result in the loss of configured questionnaires in existing projects and 
migrating requires several adjustments to the settings (see below and in the documentation). Furthermore, the API 
endpoints have been re-specified and return structures altered meaning that scripts drawing on endpoints from v1.x will 
have to be updated.

Below, the key updates are highlighted, including breaking changes, new features, and guidance for a seamless migration.

### Changed

- Divided DDM into several separate sub applications. ([`3e17a91`](https://github.com/uzh/ddm/commit/3e17a91), [`2b8adff`](https://github.com/uzh/ddm/commit/2b8adff), [`85e5a38`](https://github.com/uzh/ddm/commit/85e5a38), [`b01187c`](https://github.com/uzh/ddm/commit/b01187c), [`dacd594`](https://github.com/uzh/ddm/commit/dacd594), [`6f53783`](https://github.com/uzh/ddm/commit/6f53783), [`606c537`](https://github.com/uzh/ddm/commit/606c537), [`1508719`](https://github.com/uzh/ddm/commit/1508719), [`5b80959`](https://github.com/uzh/ddm/commit/5b80959), [`2e48261`](https://github.com/uzh/ddm/commit/2e48261), [`31182eb`](https://github.com/uzh/ddm/commit/31182eb), [`922fd10`](https://github.com/uzh/ddm/commit/922fd10), [`d10eb6a`](https://github.com/uzh/ddm/commit/d10eb6a), [`26805ba`](https://github.com/uzh/ddm/commit/26805ba), [`129e44d`](https://github.com/uzh/ddm/commit/129e44d), [`25984df`](https://github.com/uzh/ddm/commit/25984df), [`39d58b3`](https://github.com/uzh/ddm/commit/39d58b3), [`bd6d06e`](https://github.com/uzh/ddm/commit/bd6d06e), [`a6c9bbf`](https://github.com/uzh/ddm/commit/a6c9bbf), [`6c77175`](https://github.com/uzh/ddm/commit/6c77175))
- Reimplemented data download views and APIs. ([`331c2b2`](https://github.com/uzh/ddm/commit/331c2b2), [`39edfaa`](https://github.com/uzh/ddm/commit/39edfaa), [`9ba1106`](https://github.com/uzh/ddm/commit/9ba1106), [`dae58c7`](https://github.com/uzh/ddm/commit/dae58c7), [`5c5e657`](https://github.com/uzh/ddm/commit/5c5e657))
- Moved from Django 3.2 to 4.2. ([`48be17f`](https://github.com/uzh/ddm/commit/48be17f), [`347de4c`](https://github.com/uzh/ddm/commit/347de4c))
- Moved from deprecated django-ckeditor to django-ckeditor-5. ([`820cd55`](https://github.com/uzh/ddm/commit/820cd55), [`63c2d9b`](https://github.com/uzh/ddm/commit/63c2d9b))
- Reference DonationProjects in urls with newly introduced DonationProject.url_id instead of with primary key. ([`94fecce`](https://github.com/uzh/ddm/commit/94fecce))
- Moved all form validation logic from views to form models. ([`22b4f58`](https://github.com/uzh/ddm/commit/22b4f58))
- Updated and restyled documentation ([`bdc5688`](https://github.com/uzh/ddm/commit/bdc5688), [`5a0e3d9`](https://github.com/uzh/ddm/commit/5a0e3d9), [`860e4b0`](https://github.com/uzh/ddm/commit/860e4b0), [`6ac17a2`](https://github.com/uzh/ddm/commit/6ac17a2), [`638677c`](https://github.com/uzh/ddm/commit/638677c), [`47c52fa`](https://github.com/uzh/ddm/commit/47c52fa), [`a79952f`](https://github.com/uzh/ddm/commit/a79952f), [`5d3dc75`](https://github.com/uzh/ddm/commit/5d3dc75), [`0da99a3`](https://github.com/uzh/ddm/commit/0da99a3), [`2cd8c2b`](https://github.com/uzh/ddm/commit/2cd8c2b), [`c5abeff`](https://github.com/uzh/ddm/commit/c5abeff), [`1840857`](https://github.com/uzh/ddm/commit/1840857), [`385923d`](https://github.com/uzh/ddm/commit/385923d), [`3ecbf4a`](https://github.com/uzh/ddm/commit/3ecbf4a), [`3bb4ddf`](https://github.com/uzh/ddm/commit/3bb4ddf), [`0cf9beb`](https://github.com/uzh/ddm/commit/0cf9beb), [`8aa3a38`](https://github.com/uzh/ddm/commit/8aa3a38))
- Moved left-over inline style attributes to CSS file. ([`3d56b5d`](https://github.com/uzh/ddm/commit/3d56b5d))
- Refactored javascript code (e.g., replace jQuery parts, move code included in templates to separate .js files etc.) ([`3d56b5d`](https://github.com/uzh/ddm/commit/3d56b5d), [`e520fb0`](https://github.com/uzh/ddm/commit/e520fb0), [`5f085a4`](https://github.com/uzh/ddm/commit/5f085a4), [`ecf4fff`](https://github.com/uzh/ddm/commit/ecf4fff), [`89d06c7`](https://github.com/uzh/ddm/commit/89d06c7), [`b9a11fd`](https://github.com/uzh/ddm/commit/b9a11fd))
- Updated frontend from Vue v2 to v3. ([`eb9b878`](https://github.com/uzh/ddm/commit/eb9b878), [`85c4278`](https://github.com/uzh/ddm/commit/85c4278))
- Renamed DdmAuthMixin to DDMAuthMixin. ([`540afec`](https://github.com/uzh/ddm/commit/540afec))

### Added

- Option to set a project to active/inactive. ([`c81cd34`](https://github.com/uzh/ddm/commit/c81cd34))
- Option to add input restrictions (input type and maximum length) to Open Question. ([`cc8765a`](https://github.com/uzh/ddm/commit/cc8765a))
- Download function for questionnaire responses. ([`7a18831`](https://github.com/uzh/ddm/commit/7a18831), [`5c5e657`](https://github.com/uzh/ddm/commit/5c5e657))
- Custom template engine for researchers to customize text fields. ([`4ff7e77`](https://github.com/uzh/ddm/commit/4ff7e77))
- Improved file type checks before file extraction. ([`3da3feb`](https://github.com/uzh/ddm/commit/3da3feb))
- Utility function to create server error logs for users. ([`78302dd`](https://github.com/uzh/ddm/commit/78302dd))
- Extended test coverage for all apps. ([`7cd1734`](https://github.com/uzh/ddm/commit/7cd1734), [`ef5ee53`](https://github.com/uzh/ddm/commit/ef5ee53), [`83fbc56`](https://github.com/uzh/ddm/commit/83fbc56))

### Removed

- Removed deprecated function DonationBlueprint.get_instructions(). ([`438e04b`](https://github.com/uzh/ddm/commit/438e04b))
- Removed unused ResearchProfileConfirmationForm. ([`75d7bf3`](https://github.com/uzh/ddm/commit/75d7bf3))
- Removed unused template files. ([`2e48261`](https://github.com/uzh/ddm/commit/2e48261))
- Removed unused class DdmRegisterResearchProfileView including the corresponding html template. ([`df36816`](https://github.com/uzh/ddm/commit/df36816))

### UI/UX

- Optimized space usage on mobile devices. ([`9185941`](https://github.com/uzh/ddm/commit/9185941))
- Redesigned donation page to look sleaker and more modern ([`33b0e59`](https://github.com/uzh/ddm/commit/33b0e59), [`f9ff9e0`](https://github.com/uzh/ddm/commit/f9ff9e0))
- Restyled instruction carousel. ([`ce067a3`](https://github.com/uzh/ddm/commit/ce067a3))
- Update instruction title to 'how it works'. ([`6d15a10`](https://github.com/uzh/ddm/commit/6d15a10))
- Restructured the blueprint create form to look cleaner and align with the blueprint edit form. ([`43b7122`](https://github.com/uzh/ddm/commit/43b7122))
- Renamed 'label alt' to 'label right' for Semantic Differential questions and updated the semantic differential edit view. ([`ff955e7`](https://github.com/uzh/ddm/commit/ff955e7))
- Indeces in Question Item and Scale Points forms increase now automatically. ([`bad0611`](https://github.com/uzh/ddm/commit/bad0611))
- Various UI fixes and clarifications in the researcher admin interfaced. ([`16e7472`](https://github.com/uzh/ddm/commit/16e7472), [`402205d`](https://github.com/uzh/ddm/commit/402205d), [`46a63b5`](https://github.com/uzh/ddm/commit/46a63b5), [`6825704`](https://github.com/uzh/ddm/commit/6825704), [`8893439`](https://github.com/uzh/ddm/commit/8893439), [`b59b37b`](https://github.com/uzh/ddm/commit/b59b37b), [`3bb0e49`](https://github.com/uzh/ddm/commit/3bb0e49), [`aea17df`](https://github.com/uzh/ddm/commit/aea17df), [`dd065f2`](https://github.com/uzh/ddm/commit/dd065f2), [`dd065f2`](https://github.com/uzh/ddm/commit/dd065f2))
- Display general and blueprint-related questions in the same table and move extra information to collapsible. ([`4fdd6a2`](https://github.com/uzh/ddm/commit/4fdd6a2))

### Breaking Changes

- **Loss of Configured Questionnaires:** 
Upgrading from 1.x to 2.x will result in the loss of configured questionnaires in existing projects. 
This is due to migration challenges caused by the polymorphic structure of the QuestionBase model. 
To retain existing configurations, create a database backup and write a custom script to re-import the old questionnaire data. 
Since the structure of the models in the questionnaire app remains unchanged, re-creating objects based on the v1.x configurations should be feasible.
- **Deprecated Function:** 
The `ddm.auth.user_is_allowed` function has been removed in v2.0. Replace it with `ddm_auth.utils.user_has_project_access`.

### Migration Guide

To migrate from 1.x to 2.0, follow the installation steps outlined in the updated administrator documentation, 
particularly regarding included apps and template context processors.

If you have integrated DDM functionality into your own code, ensure the following updates are made:

- **Update Imports:** Functions and models have been moved to specific sub-apps.
- **Update URL References:** URL patterns have been renamed, and URL namespaces have been introduced for each sub-app.
- **Update Template and Static File Paths:** Templates and static files have been reorganized, with resources now 
housed in their respective sub-app directories instead of the top-level.

### Update Guide

Run `python manage.py migrate` and `python manage.py collectstatic` after upgrading to DDM v2.0.0 from a previous version.


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
