# DDM Uploader

## Application Overview

The DDM Uploader is a Vue-based web application designed for structured data extraction and donation. 
It allows users to upload files containing data (JSON, CSV, or ZIP archives), processes them according 
to predefined blueprints, and submits the extracted data with proper consent management.

Although it is designed to be used with the DDM backend (available as django-ddm on pip) it can also be used 
independently.

## Core Functionality

### File Processing
- Handles single file uploads (JSON/CSV) and ZIP archives containing multiple files
- Supports matching files in ZIP archives using regex patterns
- Validates file types and formats before processing

### Data Extraction
- Processes content based on predefined blueprint configurations
- Extracts data using field mappings and rule-based transformations
- Supports various comparison operations (equality, numeric comparisons, date comparisons)
- Provides regex-based text transformations (deletion, replacement)

### Consent Management
- Tracks user consent for each blueprint's extracted data
- Supports both individual consent per blueprint and combined consent
- Validates consent status before submission

### Validation and Error Handling
- Comprehensive error tracking and categorization
- Detailed validation of uploader states and consent provisions
- Multi-level error reporting (critical, warning, info)

### User Interface
- Multi-step process with clear visual feedback
- Extraction results overview with expandable details
- Interactive consent toggles and data visualization
- Validation modals for incomplete steps

### Internationalization
- Full i18n support for all user-facing text
- Multi-language error messages and UI elements

## Technical Architecture

The application follows a component-based architecture using Vue 3 with the Composition API:

- **Core Components**: UploaderApp, UploaderWrapper, ExtractionOverview, FileDrop, ConsentQuestion
- **Utility Components**: ExtractionTable, IssueModal, SubmittingModal
- **Composables**: File processing, extraction state tracking, data submission, consent management
- **Utility Functions**: Value comparison, regex operations, error handling

The system is designed to be extensible, allowing for new blueprint types, extraction rules, and file formats 
to be added with minimal changes to the core architecture.

## Usage Flow

1. Application initializes by reading configuration from DOM data attributes
2. User uploads a file through drag-and-drop or file selection
3. System processes the file according to blueprint configurations
4. Extraction results are displayed with details about success, partial success, or failure
5. User provides consent for data donation
6. Validation ensures all required steps are completed
7. Data is submitted to the configured endpoint

This application provides a flexible, user-friendly interface for structured data extraction and submission with 
proper consent management and comprehensive error handling.


## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).


## Testing

To execute the tests run:
```
npx vitest run
```
