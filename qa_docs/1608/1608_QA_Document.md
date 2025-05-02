# 1608 QA Document

**Table of Contents**

1.  [Application Overview](#1-application-overview)
    *   [Purpose and Functionality](#purpose-and-functionality)
    *   [Technology Stack](#technology-stack)
2.  [Component Action Mapping Documentation](#2-component-action-mapping-documentation)
    *   [User Privilege Grid (#grid)](#user-privilege-grid-grid)
    *   [User Privilege Form (#form1)](#user-privilege-form-form1)
    *   [User Dropdown (ddlusers)](#user-dropdown-ddlusers)
    *   [Authorized Entity Dropdowns (ddlCustomer, ddlOperationArea, etc.)](#authorized-entity-dropdowns-ddlcustomer-ddloperationarea-etc)
    *   [Default Entity Dropdowns (ddlDefaultOperationArea, ddlDefaultJobType, etc.)](#default-entity-dropdowns-ddldefaultoperationarea-ddldefaultjobtype-etc)
    *   [Permission Group Dropdowns (ddlGlobal, ddlPlanner)](#permission-group-dropdowns-ddlglobal-ddlplanner)
    *   [Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)](#sensitive-docs-checkbox-txtallowtoviewsensitivedocs)
    *   [Save Button (#btnSave)](#save-button-btnsave)
    *   [Update Button (#update)](#update-button-update)
    *   [Clear Button (#btnClear)](#clear-button-btnclear)
    *   [Edit Button (in grid)](#edit-button-in-grid)
    *   [Delete Button (in grid)](#delete-button-in-grid)
3.  [Acceptance Criteria and Test Cases](#3-acceptance-criteria-and-test-cases)
    *   [User Privilege Grid (#grid)](#acceptance-criteria-user-privilege-grid-grid)
        *   [Test Cases: User Privilege Grid (#grid)](#test-cases-user-privilege-grid-grid)
    *   [User Privilege Form (#form1)](#acceptance-criteria-user-privilege-form-form1)
        *   [Test Cases: User Privilege Form (#form1)](#test-cases-user-privilege-form-form1)
    *   [User Dropdown (ddlusers)](#acceptance-criteria-user-dropdown-ddlusers)
        *   [Test Cases: User Dropdown (ddlusers)](#test-cases-user-dropdown-ddlusers)
    *   [Authorized Entity Dropdowns](#acceptance-criteria-authorized-entity-dropdowns)
        *   [Test Cases: Authorized Entity Dropdowns](#test-cases-authorized-entity-dropdowns)
    *   [Default Entity Dropdowns](#acceptance-criteria-default-entity-dropdowns)
        *   [Test Cases: Default Entity Dropdowns](#test-cases-default-entity-dropdowns)
    *   [Permission Group Dropdowns (ddlGlobal, ddlPlanner)](#acceptance-criteria-permission-group-dropdowns-ddlglobal-ddlplanner)
        *   [Test Cases: Permission Group Dropdowns (ddlGlobal, ddlPlanner)](#test-cases-permission-group-dropdowns-ddlglobal-ddlplanner)
    *   [Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)](#acceptance-criteria-sensitive-docs-checkbox-txtallowtoviewsensitivedocs)
        *   [Test Cases: Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)](#test-cases-sensitive-docs-checkbox-txtallowtoviewsensitivedocs)
    *   [Save Button (#btnSave)](#acceptance-criteria-save-button-btnsave)
        *   [Test Cases: Save Button (#btnSave)](#test-cases-save-button-btnsave)
    *   [Update Button (#update)](#acceptance-criteria-update-button-update)
        *   [Test Cases: Update Button (#update)](#test-cases-update-button-update)
    *   [Clear Button (#btnClear)](#acceptance-criteria-clear-button-btnclear)
        *   [Test Cases: Clear Button (#btnClear)](#test-cases-clear-button-btnclear)
    *   [Edit Button (in grid)](#acceptance-criteria-edit-button-in-grid)
        *   [Test Cases: Edit Button (in grid)](#test-cases-edit-button-in-grid)
    *   [Delete Button (in grid)](#acceptance-criteria-delete-button-in-grid)
        *   [Test Cases: Delete Button (in grid)](#test-cases-delete-button-in-grid)
4.  [Testing Strategy and Requirements](#4-testing-strategy-and-requirements)
    *   [Testing Types](#testing-types)
    *   [Key Business Requirements Validation](#key-business-requirements-validation)
    *   [Risk-Based Prioritization](#risk-based-prioritization)
    *   [Architectural Considerations](#architectural-considerations)
5.  [Error Handling and Edge Cases](#5-error-handling-and-edge-cases)
    *   [Validation Errors](#validation-errors)
    *   [Data Integrity Errors](#data-integrity-errors)
    *   [Server/Network Errors](#servernetwork-errors)
    *   [Concurrency Issues](#concurrency-issues)

# 1. Application Overview

## Purpose and Functionality

Project **1608** provides a dedicated interface for configuring detailed user privileges within a larger system. Its primary purpose is to allow administrators or authorized personnel to define precisely what actions specific users can perform and what data entities (like Customers, Areas, Facilities, Task Types, etc.) they are authorized to access or have defaulted in their views.

The core functionality revolves around:

*   **Viewing:** Displaying existing user privilege configurations in a searchable, sortable, and filterable grid.
*   **Creating:** Adding new privilege configurations for specific users, assigning permissions via checkboxes and dropdown selections.
*   **Editing:** Modifying existing privilege configurations.
*   **Deleting:** Removing privilege configurations.
*   **Data Management:** Defining authorized and default entities for various categories relevant to the main application's operations.

This module acts as the central control panel for user access rights related to operational data and actions.

## Technology Stack

Based on the provided context, the technology stack includes:

*   **Frontend:**
    *   HTML
    *   JavaScript (jQuery)
    *   Kendo UI (for Grid)
    *   Bootstrap Select (for Dropdowns)
    *   Parsley.js (for Form Validation)
    *   SweetAlert2 (for Confirmation Dialogs)
    *   AJAX (for communication with backend)
    *   CSS (Bootstrap likely for styling)
*   **Backend:**
    *   ASP.NET (Web Forms likely, based on `.aspx` and code-behind pattern)
    *   C# (for server-side logic and web methods)
*   **Database:**
    *   Microsoft SQL Server (implied by the use of Stored Procedures like `SP_FormDataPRIDUserPrivilegesSetup`)
*   **Architecture:**
    *   Multi-tier: UI Layer (JavaScript, Kendo, HTML) -> Backend Service Layer (C# Web Methods) -> Data Access Layer (C# `DataOperations`) -> Data Persistence Layer (SQL Stored Procedure).

# 2. Component Action Mapping Documentation

This section details the actions triggered by user interactions with specific UI components.

## User Privilege Grid (#grid)

| Trigger/Event        | Action                                       | Target/Effect                                                                 | Data Elements                                             | Validation Rules | Error Scenarios                     | Test Priority | Expected Performance         |
| :------------------- | :------------------------------------------- | :---------------------------------------------------------------------------- | :-------------------------------------------------------- | :--------------- | :---------------------------------- | :------------ | :--------------------------- |
| Page Load            | `$('#grid').kendoGrid` initialization        | Grid populated with initial data set via AJAX call to fetch grid data.        | User Privilege records (User, Permissions, Entities)      | None             | AJAX error fetching data.           | High          | Load within 3-5 secs (1st page) |
| Click Header Column  | Kendo Grid Internal Sort                     | Grid data re-sorted based on the clicked column; data source refreshed.       | Grid display data                                         | None             | Slow response on large datasets.    | Medium        | Sort < 2 secs                |
| Enter Text in Search | Kendo Grid Internal Filter / Server Filter | Grid data filtered based on search term; data source refreshed.             | Grid display data                                         | None             | Slow response on large datasets.    | Medium        | Filter < 2 secs              |
| Click Page Number    | Kendo Grid Internal Paging                   | Grid displays the requested page number; data source refreshed via AJAX call. | Grid display data                                         | None             | AJAX error fetching next page data. | Medium        | Page load < 2 secs           |
| Click Export Button  | Kendo Grid Export to Excel                   | Generates and initiates download of an Excel file containing grid data.     | Grid display data                                         | None             | Browser blocking download.          | Low           | Export generation < 10 secs  |
| Click Edit Button    | `edituserPrivileges(recordid)` (JS)          | Loads selected record data into #form1 for editing.                           | Record ID                                                 | None             | Record not found; AJAX error.     | High          | Form population < 2 secs     |
| Click Delete Button  | `deleteuserPrivileges(recordid)` (JS)        | Initiates deletion process for the selected record (shows confirmation).      | Record ID                                                 | None             | Deletion conflict; AJAX error.    | High          | Confirmation dialog < 1 sec  |
| Grid Data Bound      | `onDataBound` (Kendo Grid event)             | Potentially custom JS logic executed after grid data is loaded/updated.       | Grid display data                                         | N/A              | JS error in `onDataBound` handler.  | Medium        | Handler execution < 0.5 secs |

## User Privilege Form (#form1)

| Trigger/Event   | Action                                        | Target/Effect                                             | Data Elements                                | Validation Rules                      | Error Scenarios                             | Test Priority | Expected Performance |
| :-------------- | :-------------------------------------------- | :-------------------------------------------------------- | :------------------------------------------- | :------------------------------------ | :------------------------------------------ | :------------ | :------------------- |
| Submit (via Save/Update) | `$('#form1').parsley().validate()` (JS)     | Form fields validated according to Parsley rules.       | All input fields within the form           | Parsley rules (required, format, etc.) | Validation fails, prevents submission.    | High          | Validation < 0.5 secs |
| Field Change    | Parsley.js automatic validation (if configured) | Real-time validation feedback provided on the field.    | The specific field being changed             | Parsley rules for that field          | N/A                                         | Medium        | Instant feedback     |
| Clear Button Click | `$('form').parsley().reset()` (JS)          | Removes Parsley validation messages and state from form. | Parsley validation state for all form fields | None                                  | JS error if Parsley not initialized.      | Medium        | Reset < 0.5 secs      |

## User Dropdown (ddlusers)

| Trigger/Event | Action                        | Target/Effect                                                               | Data Elements | Validation Rules | Error Scenarios                                  | Test Priority | Expected Performance |
| :------------ | :---------------------------- | :-------------------------------------------------------------------------- | :------------ | :--------------- | :----------------------------------------------- | :------------ | :------------------- |
| Page Load     | Populate via `bindUsers` (C#) | Dropdown populated with a list of users fetched from the backend.           | User List     | None             | Error fetching user list from DB/backend.      | High          | Population < 2 secs  |
| Select User   | User Selection                | Stores the selected User ID for form submission.                            | Selected User | Required field   | N/A                                              | High          | Instant selection    |
| Type in Search | Bootstrap Select Search       | Filters the displayed user list based on typed characters.                  | User List     | None             | Performance issue with very large number of users. | Medium        | Filter < 1 sec       |

## Authorized Entity Dropdowns (ddlCustomer, ddlOperationArea, etc.)

| Trigger/Event        | Action                                         | Target/Effect                                                                         | Data Elements                      | Validation Rules     | Error Scenarios                               | Test Priority | Expected Performance |
| :------------------- | :--------------------------------------------- | :------------------------------------------------------------------------------------ | :--------------------------------- | :------------------- | :-------------------------------------------- | :------------ | :------------------- |
| Page Load            | Populate via C# methods (e.g., `GetCustomer`) | Dropdowns populated with respective entity lists fetched from backend.                | Entity Lists (Customers, Areas, etc.) | None                 | Error fetching lists from DB/backend.       | High          | Population < 2 secs  |
| Select/Deselect Item | User Selection / Bootstrap Select              | Updates the list of selected authorized entities. May trigger change handler.         | Selected Authorized Entities     | Required (Multi-select) | N/A                                           | High          | Instant selection    |
| Click 'Select All'   | Bootstrap Select Feature                       | Selects all available options in the dropdown. May trigger change handler.            | All Authorized Entities            | N/A                  | Performance issue with very large lists.    | Medium        | Selection < 1 sec    |
| Change Event         | Dropdown Change Handlers (JS)                  | Corresponding 'Default' dropdown is updated to reflect allowed authorized selections. | Selected Authorized Entities     | None                 | JS error in change handler.                 | High          | Default update < 1 sec |
| Type in Search       | Bootstrap Select Search                        | Filters the displayed entity list based on typed characters.                          | Entity List                      | None                 | Performance issue with very large entity lists. | Medium        | Filter < 1 sec       |

## Default Entity Dropdowns (ddlDefaultOperationArea, ddlDefaultJobType, etc.)

| Trigger/Event             | Action                               | Target/Effect                                                                                              | Data Elements                   | Validation Rules                               | Error Scenarios                                         | Test Priority | Expected Performance |
| :------------------------ | :----------------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------ | :--------------------------------------------- | :------------------------------------------------------ | :------------ | :------------------- |
| Page Load                 | Populate via C# methods              | Dropdowns populated with respective entity lists fetched from backend (may be initially empty or limited). | Entity Lists                  | None                                           | Error fetching lists from DB/backend.                 | High          | Population < 2 secs  |
| Authorized Dropdown Change | Dropdown Change Handlers (JS)      | Options enabled/disabled or list repopulated based on corresponding 'Authorized' selections.             | Corresponding Authorized List | Selections must be subset of Authorized list | JS error in change handler.                           | High          | Update < 1 sec       |
| Select/Deselect Item      | User Selection / Bootstrap Select    | Updates the list of selected default entities.                                                             | Selected Default Entities       | Selections must be subset of Authorized list | User attempts to select non-authorized item (UI logic) | High          | Instant selection    |
| Form Submit (Save/Update) | Custom Validation Logic (JS)         | Checks if all selected Default items are present in the corresponding Authorized dropdown.               | Selected Default & Authorized | Default items must exist in Authorized list  | Validation fails, prevents submission, shows error. | High          | Validation < 0.5 secs |

## Permission Group Dropdowns (ddlGlobal, ddlPlanner)

| Trigger/Event        | Action                            | Target/Effect                                                   | Data Elements        | Validation Rules     | Error Scenarios                    | Test Priority | Expected Performance |
| :------------------- | :-------------------------------- | :-------------------------------------------------------------- | :------------------- | :------------------- | :--------------------------------- | :------------ | :------------------- |
| Page Load            | Populate via C# methods/hardcoded | Dropdowns populated with available permission flags.            | Permission Flags     | None                 | Error fetching list (if dynamic). | High          | Population < 1 sec   |
| Select/Deselect Item | User Selection / Bootstrap Select | Updates the list of selected permissions for that group.      | Selected Permissions | Multi-select allowed | N/A                                | High          | Instant selection    |
| Click 'Select All'   | Bootstrap Select Feature          | Selects all available permission flags in the dropdown.       | All Permissions      | N/A                  | N/A                                | Medium        | Selection < 1 sec    |

## Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)

| Trigger/Event | Action          | Target/Effect                                | Data Elements                   | Validation Rules | Error Scenarios | Test Priority | Expected Performance |
| :------------ | :-------------- | :------------------------------------------- | :------------------------------ | :--------------- | :-------------- | :------------ | :------------------- |
| Click         | User Interaction | Toggles the boolean state of the permission. | `AllowToViewSensitiveDocs` flag | None             | N/A             | Medium        | Instant toggle       |

## Save Button (#btnSave)

| Trigger/Event | Action                                                         | Target/Effect                                                                                             | Data Elements                                           | Validation Rules                                       | Error Scenarios                                                                                                     | Test Priority | Expected Performance      |
| :------------ | :------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------------ | :----------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ | :------------ | :------------------------ |
| Click         | `$('#btnSave').on('click')` handler (JS)                       | Initiates the process to save a new user privilege configuration.                                         | All form data (`UserPrivilegesSetupobj`)              | Parsley validation; Default vs. Authorized validation | Validation failure; Duplicate user configuration; AJAX error; DB error during insert; SP error.                   | High          | Response < 3 secs         |
| Click         | Calls `$('#form1').parsley().isValid()`                          | Validates form fields based on Parsley rules.                                                             | All form fields                                         | Required fields, data formats.                         | Validation fails, stops processing, shows Parsley errors.                                                             | High          | < 0.5 secs                |
| Click         | Calls custom Default vs. Authorized validation                 | Validates that default selections are a subset of authorized selections.                                  | Selected Default & Authorized values                  | Default items must exist in Authorized list          | Validation fails, stops processing, shows error toast (`showErrorToasterNotification`).                               | High          | < 0.5 secs                |
| Click         | Calls `1608.aspx/Insert` (AJAX POST)                           | Sends the constructed `UserPrivilegesSetupobj` to the backend Insert web method.                          | `UserPrivilegesSetupobj`                                | Backend validation (e.g., duplicates)                  | AJAX fails (network, server error); Backend returns error (duplicate, DB issue); Timeout.                           | High          | Network dependent ( < 2s) |
| Click (Success) | AJAX Success Callback                                          | Clears form (`btnClear`), refreshes grid (`dataSource.read`), shows success toast (`showSuccessToasterNotification`). | Success Message                                         | N/A                                                    | JS error in callback.                                                                                               | High          | < 1 sec after server response |
| Click (Error)   | AJAX Error Callback or Backend Error                           | Shows error toast (`showErrorToasterNotification`).                                                         | Error Message                                           | N/A                                                    | JS error in callback.                                                                                               | High          | < 0.5 secs after error    |

## Update Button (#update)

*Note: Only visible after clicking Edit on a grid row.*

| Trigger/Event | Action                                                         | Target/Effect                                                                                                    | Data Elements                                           | Validation Rules                                       | Error Scenarios                                                                                                     | Test Priority | Expected Performance      |
| :------------ | :------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------ | :----------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ | :------------ | :------------------------ |
| Click         | `$('#update').on('click')` handler (JS)                       | Initiates the process to update the existing user privilege configuration.                                         | All form data + RecordId (`UserPrivilegesSetupobj`)     | Parsley validation; Default vs. Authorized validation | Validation failure; Record not found/modified concurrently; AJAX error; DB error during update; SP error.           | High          | Response < 3 secs         |
| Click         | Calls `$('#form1').parsley().isValid()`                          | Validates form fields based on Parsley rules.                                                                    | All form fields                                         | Required fields, data formats.                         | Validation fails, stops processing, shows Parsley errors.                                                             | High          | < 0.5 secs                |
| Click         | Calls custom Default vs. Authorized validation                 | Validates that default selections are a subset of authorized selections.                                         | Selected Default & Authorized values                  | Default items must exist in Authorized list          | Validation fails, stops processing, shows error toast (`showErrorToasterNotification`).                               | High          | < 0.5 secs                |
| Click         | Calls `1608.aspx/UpdateUserPrivileges` (AJAX POST)             | Sends the constructed `UserPrivilegesSetupobj` (including RecordId) to the backend UpdateUserPrivileges web method. | `UserPrivilegesSetupobj` (with RecordId)              | Backend validation (e.g., record exists)               | AJAX fails (network, server error); Backend returns error (record not found, DB issue); Timeout.                    | High          | Network dependent ( < 2s) |
| Click (Success) | AJAX Success Callback                                          | Clears form (`btnClear`), refreshes grid (`dataSource.read`), shows success toast (`showSuccessToasterNotification`), resets UI to Save mode. | Success Message                                         | N/A                                                    | JS error in callback.                                                                                               | High          | < 1 sec after server response |
| Click (Error)   | AJAX Error Callback or Backend Error                           | Shows error toast (`showErrorToasterNotification`).                                                                | Error Message                                           | N/A                                                    | JS error in callback.                                                                                               | High          | < 0.5 secs after error    |

## Clear Button (#btnClear)

| Trigger/Event | Action                                              | Target/Effect                                                                   | Data Elements   | Validation Rules | Error Scenarios        | Test Priority | Expected Performance |
| :------------ | :-------------------------------------------------- | :------------------------------------------------------------------------------ | :-------------- | :--------------- | :--------------------- | :------------ | :------------------- |
| Click         | `$('#btnClear').on('click')` handler (JS)           | Resets form fields, clears validation messages, and ensures UI is in Save mode. | Form field values | None             | JS errors during reset. | Medium        | < 0.5 secs           |
| Click         | Calls `$('form').parsley().reset()`                   | Clears all Parsley validation states and messages from the form.              | Validation state | None             | Parsley not loaded.  | Medium        | < 0.5 secs           |
| Click         | Calls `$('.selectpicker').selectpicker('val', null)` | Deselects all options in all Bootstrap Select dropdowns.                        | Dropdown values | None             | Bootstrap Select error. | Medium        | < 0.5 secs           |
| Click         | Hides `#update`, Shows `#btnSave`                     | Resets the form buttons to the initial 'Save' state.                            | Button visibility | None             | N/A                  | Medium        | Instant              |

## Edit Button (in grid)

| Trigger/Event | Action                                  | Target/Effect                                                                                                       | Data Elements                          | Validation Rules | Error Scenarios                                                        | Test Priority | Expected Performance |
| :------------ | :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------ | :------------------------------------- | :--------------- | :--------------------------------------------------------------------- | :------------ | :------------------- |
| Click         | `edituserPrivileges(recordid)` (JS)     | Initiates loading the selected record's data into the form.                                                         | `recordid`                             | None             | `recordid` is invalid/missing.                                         | High          | < 0.5 secs           |
| Click         | Calls `1608.aspx/Edit` (AJAX POST)      | Sends the `recordid` to the backend Edit web method to fetch the full privilege details.                            | `recordid`                             | Record must exist | AJAX fails; Backend error (record not found, DB error); Timeout.         | High          | Network dependent (<2s) |
| Click (Success) | AJAX Success Callback                   | Parses the returned JSON data and populates all form fields (#ddlusers, checkboxes, all selectpickers) accordingly. | Full User Privilege Data (JSON string) | None             | Invalid JSON returned; JS error populating fields; Selectpicker error. | High          | < 1 sec              |
| Click (Success) | Switches UI Mode                      | Hides `#btnSave`, Shows `#update`. Scrolls view to the form (likely).                                                 | Button visibility                      | None             | N/A                                                                    | High          | Instant              |
| Click (Error)   | AJAX Error Callback or Backend Error | Shows error toast (`showErrorToasterNotification`).                                                                   | Error Message                          | None             | JS error in callback.                                                  | High          | < 0.5 secs           |

## Delete Button (in grid)

| Trigger/Event       | Action                                         | Target/Effect                                                                                                  | Data Elements   | Validation Rules | Error Scenarios                                                              | Test Priority | Expected Performance      |
| :------------------ | :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------- | :-------------- | :--------------- | :--------------------------------------------------------------------------- | :------------ | :------------------------ |
| Click               | `deleteuserPrivileges(recordid)` (JS)          | Initiates the deletion process for the selected record.                                                        | `recordid`      | None             | `recordid` is invalid/missing.                                               | High          | < 0.5 secs           |
| Click               | Calls `Swal.fire` (SweetAlert2)                | Displays a confirmation dialog asking the user to confirm deletion.                                          | Confirmation text | User must confirm | User cancels deletion; JS error showing dialog.                            | High          | < 0.5 secs           |
| User Confirms       | Confirmation Callback                          | Proceeds with deletion if user confirms.                                                                       | Confirmation result | N/A              | N/A                                                                          | High          | N/A                       |
| User Confirms       | Calls `1608.aspx/deleteUserPrivileges` (AJAX POST) | Sends the `recordid` to the backend deleteUserPrivileges web method.                                         | `recordid`      | Record must exist | AJAX fails; Backend error (record not found, DB error, delete constraint); Timeout. | High          | Network dependent (<2s) |
| User Confirms (Success) | AJAX Success Callback                          | Refreshes grid (`dataSource.read`), shows success toast (`showSuccessToasterNotification`), potentially clears form (`btnClear`). | Success Message | N/A              | JS error in callback.                                                        | High          | < 1 sec after server response |
| User Confirms (Error) | AJAX Error Callback or Backend Error         | Shows error toast (`showErrorToasterNotification`).                                                              | Error Message   | N/A              | JS error in callback.                                                        | High          | < 0.5 secs after error    |

# 3. Acceptance Criteria and Test Cases

## Acceptance Criteria: User Privilege Grid (#grid)

*   The grid must load and display the first page of user privilege records within 5 seconds on initial page load.
*   All configured user privilege records must be viewable through paging.
*   Data displayed in the grid columns (User, Permissions summary, Key Entities) must accurately reflect the data stored in the database.
*   Sorting must work correctly (ascending/descending) for all sortable columns.
*   Searching/Filtering must correctly filter the grid data based on the input criteria across relevant fields.
*   Paging controls (Next, Previous, Page Numbers, Page Size) must function correctly and update the grid view.
*   The Export to Excel function must generate a downloadable Excel file containing all data currently displayed/filtered in the grid.
*   Each row must contain functional Edit and Delete buttons specific to that row's record ID.
*   The grid must refresh automatically after successful Save, Update, or Delete operations.

## Test Cases: User Privilege Grid (#grid)

| Test ID         | Preconditions                                                              | Steps to Execute                                                                                                                                                              | Expected Final Result                                                                                                 | Severity/Priority |
| :-------------- | :------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- | :---------------- |
| GRID\_LOAD\_01  | At least one user privilege record exists in the database.                   | 1. Navigate to the User Privileges page (1608.aspx).                                                                                                                            | The Kendo Grid (#grid) displays, populated with user privilege records. The first page of data is shown.                | High              |
| GRID\_LOAD\_02  | No user privilege records exist in the database.                             | 1. Navigate to the User Privileges page.                                                                                                                                      | The Kendo Grid displays with headers but shows a "No records found" message (or equivalent).                          | Medium            |
| GRID\_SORT\_01  | Grid is loaded with multiple records having different User names.            | 1. Click the header for the 'User' column. <br> 2. Click the header for the 'User' column again.                                                                               | 1. Grid data sorts ascending by User name. <br> 2. Grid data sorts descending by User name.                             | Medium            |
| GRID\_FILTER\_01 | Grid is loaded with multiple records. At least one record for 'User A'.    | 1. Enter 'User A' into the grid's search/filter input.                                                                                                                          | The grid updates to show only records associated with 'User A'.                                                       | Medium            |
| GRID\_FILTER\_02 | Grid is loaded with multiple records. No record matches 'XYZ123'.          | 1. Enter 'XYZ123' into the grid's search/filter input.                                                                                                                          | The grid updates to show "No records found".                                                                          | Low               |
| GRID\_PAGE\_01  | More records exist than the default page size. Grid displays page 1.         | 1. Click the 'Next' page button. <br> 2. Click the 'Previous' page button. <br> 3. Click a specific page number (e.g., '3').                                                     | 1. Grid displays the second page of records. <br> 2. Grid displays the first page. <br> 3. Grid displays page 3.        | Medium            |
| GRID\_EXPORT\_01 | Grid is loaded with data.                                                  | 1. Click the 'Export to Excel' button.                                                                                                                                      | An Excel file download should initiate. The file should contain the data currently visible in the grid.             | Low               |
| GRID\_REFRESH\_01| Grid is loaded. A new record is successfully saved via the form.           | 1. Fill and save a new valid user privilege record using #btnSave.                                                                                                            | The grid automatically refreshes, showing the newly added record (likely on the first page or appropriate sorted position). | High              |
| GRID\_REFRESH\_02| Grid is loaded. An existing record is successfully updated via the form.   | 1. Edit a record. <br> 2. Make a change. <br> 3. Click #update.                                                                                                              | The grid automatically refreshes, showing the updated data for the modified record.                                     | High              |
| GRID\_REFRESH\_03| Grid is loaded. An existing record is successfully deleted via a grid button. | 1. Click the Delete button for a record. <br> 2. Confirm deletion.                                                                                                            | The grid automatically refreshes, and the deleted record is no longer visible.                                          | High              |

## Acceptance Criteria: User Privilege Form (#form1)

*   The form must contain all necessary fields (dropdowns, checkboxes) for configuring user privileges as defined.
*   Parsley.js validation must trigger on relevant fields (e.g., required dropdowns) upon attempting to Save or Update.
*   Validation errors must prevent form submission.
*   Validation messages must clearly indicate which fields failed validation and why.
*   The form must be cleared correctly when the Clear button is clicked or after a successful Save/Update operation.

## Test Cases: User Privilege Form (#form1)

| Test ID         | Preconditions                               | Steps to Execute                                                                                                       | Expected Final Result                                                                                                         | Severity/Priority |
| :-------------- | :------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| FORM\_VALID\_01 | Form is displayed. #btnSave is visible.     | 1. Leave the required 'User' dropdown (ddlusers) empty. <br> 2. Click #btnSave.                                          | Form submission is prevented. A validation error message is displayed for the 'User' dropdown indicating it's required.     | High              |
| FORM\_VALID\_02 | Form is displayed. #btnSave is visible.     | 1. Leave a required 'Authorized' multi-select dropdown (e.g., ddlCustomer) empty. <br> 2. Click #btnSave.                 | Form submission is prevented. A validation error message is displayed for the empty dropdown indicating selection is required. | High              |
| FORM\_VALID\_03 | Form is displayed. #update is visible.      | 1. Select a required dropdown. <br> 2. Deselect all options from it. <br> 3. Click #update.                                | Form submission is prevented. A validation error message is displayed for the empty dropdown indicating selection is required. | High              |
| FORM\_CLEAR\_01 | Form fields are populated with some data. | 1. Click the #btnClear button.                                                                                         | All form fields (dropdowns, checkboxes) are reset to their default empty/unchecked state. Parsley validation messages are cleared. | Medium            |
| FORM\_MODE\_01  | Form is initially loaded.                 | 1. Observe the Save/Update buttons.                                                                                    | #btnSave is visible, #update is hidden.                                                                                       | High              |
| FORM\_MODE\_02  | User clicks Edit on a grid row.             | 1. Click the Edit button for any grid row.                                                                               | #btnSave is hidden, #update is visible. Form is populated with the selected record's data.                                  | High              |
| FORM\_MODE\_03  | User clicks Update successfully.            | 1. Edit a record. <br> 2. Make a valid change. <br> 3. Click #update. <br> 4. Observe buttons after success message.       | #btnSave is visible, #update is hidden. Form is cleared.                                                                      | High              |
| FORM\_MODE\_04  | User clicks Clear while in Edit mode.     | 1. Edit a record. <br> 2. Click #btnClear. <br> 3. Observe buttons.                                                      | #btnSave is visible, #update is hidden. Form is cleared.                                                                      | Medium            |

## Acceptance Criteria: User Dropdown (ddlusers)

*   The dropdown must be populated with a list of available users on page load.
*   The dropdown must be searchable/filterable.
*   Selecting a user must store the correct user ID for submission.
*   The dropdown must be marked as a required field for form submission.

## Test Cases: User Dropdown (ddlusers)

| Test ID         | Preconditions                     | Steps to Execute                                                                                                | Expected Final Result                                                                                             | Severity/Priority |
| :-------------- | :-------------------------------- | :-------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- | :---------------- |
| DDL\_USER\_LOAD\_01 | Users exist in the system.        | 1. Navigate to the User Privileges page. <br> 2. Click the 'User' dropdown (ddlusers).                           | The dropdown expands, showing a list of users.                                                                    | High              |
| DDL\_USER\_REQ\_01| Form is displayed.                | 1. Do not select a user from ddlusers. <br> 2. Fill all other required fields. <br> 3. Click #btnSave.              | Form submission fails. Validation error shown for ddlusers.                                                     | High              |
| DDL\_USER\_SEL\_01| Dropdown is populated with users. | 1. Select a specific user (e.g., 'TestUser1'). <br> 2. Fill other required fields. <br> 3. Click #btnSave.         | Form saves successfully (assuming other data is valid). The saved record is associated with 'TestUser1'.          | High              |
| DDL\_USER\_SRCH\_01| Dropdown populated, user 'John Doe' exists. | 1. Click the dropdown. <br> 2. Type 'john' into the search field.                                        | The list filters to show users containing 'john', including 'John Doe'.                                           | Medium            |

## Acceptance Criteria: Authorized Entity Dropdowns

*   Each 'Authorized' dropdown (Customer, Area, Job Type, etc.) must load its respective list of entities on page load.
*   The dropdowns must support multi-selection.
*   The dropdowns must support a 'Select All' option (if implemented).
*   The dropdowns must be searchable/filterable.
*   Selection changes must trigger updates in the corresponding 'Default' dropdown.
*   Each 'Authorized' dropdown must be marked as required for form submission.

## Test Cases: Authorized Entity Dropdowns

| Test ID          | Preconditions                                                   | Steps to Execute                                                                                                                                                              | Expected Final Result                                                                                                                                                            | Severity/Priority |
| :--------------- | :-------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DDL\_AUTH\_LOAD\_01 | Customers exist in the system.                                  | 1. Navigate to the page. <br> 2. Click the 'Authorized Customer' dropdown (ddlCustomer).                                                                                       | The dropdown expands, showing a list of available customers.                                                                                                                    | High              |
| DDL\_AUTH\_REQ\_01 | Form is displayed.                                              | 1. Fill all required fields except ddlCustomer. <br> 2. Click #btnSave.                                                                                                        | Form submission fails. Validation error shown for ddlCustomer.                                                                                                                  | High              |
| DDL\_AUTH\_MULTI\_01| ddlCustomer has options 'Cust A', 'Cust B', 'Cust C'.           | 1. Click ddlCustomer. <br> 2. Select 'Cust A'. <br> 3. Select 'Cust B'. <br> 4. Fill other required fields. <br> 5. Click #btnSave.                                                | Form saves successfully. The saved record authorizes 'Cust A' and 'Cust B'.                                                                                                     | High              |
| DDL\_AUTH\_ALL\_01 | ddlCustomer has multiple options and a 'Select All' mechanism. | 1. Click ddlCustomer. <br> 2. Click 'Select All'. <br> 3. Fill other required fields. <br> 4. Click #btnSave.                                                                    | Form saves successfully. The saved record authorizes all available customers.                                                                                                   | Medium            |
| DDL\_AUTH\_SRCH\_01| ddlOperationArea has options 'North Area', 'South Area'.        | 1. Click ddlOperationArea. <br> 2. Type 'north' into the search field.                                                                                                        | The list filters to show 'North Area'.                                                                                                                                          | Medium            |
| DDL\_AUTH\_CHG\_01 | ddlOperationArea has options 'Area 1', 'Area 2'.                | 1. Click ddlOperationArea. <br> 2. Select 'Area 1'. <br> 3. Observe ddlDefaultOperationArea. <br> 4. Deselect 'Area 1'. <br> 5. Select 'Area 2'. <br> 6. Observe ddlDefaultOperationArea. | 3. ddlDefaultOperationArea updates its available options/selection based on 'Area 1' being authorized. <br> 6. ddlDefaultOperationArea updates based on 'Area 2' being authorized. | High              |

## Acceptance Criteria: Default Entity Dropdowns

*   Each 'Default' dropdown must load its respective list of entities, potentially filtered by initial 'Authorized' selections or empty.
*   The options available/selectable in a 'Default' dropdown must be a subset of the items selected in the corresponding 'Authorized' dropdown.
*   Users should not be able to select a 'Default' item that is not selected in the 'Authorized' counterpart (UI should enforce or validation should catch).
*   The validation rule checking Default vs. Authorized must run before Save/Update and prevent submission if invalid.
*   The dropdowns must support multi-selection.

## Test Cases: Default Entity Dropdowns

| Test ID          | Preconditions                                                                                                      | Steps to Execute                                                                                                                                                                                                                            | Expected Final Result                                                                                                                                                                                                                                                               | Severity/Priority |
| :--------------- | :----------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DDL\_DEF\_LOAD\_01 | ddlOperationArea (Auth) is populated.                                                                              | 1. Navigate to page. <br> 2. Select 'Area 1' and 'Area 2' in ddlOperationArea. <br> 3. Click ddlDefaultOperationArea.                                                                                                                          | The ddlDefaultOperationArea dropdown shows 'Area 1' and 'Area 2' as available options (other areas might be hidden/disabled).                                                                                                                                                 | High              |
| DDL\_DEF\_SYNC\_01| Auth Area = {'A1', 'A2'}. Default Area = {'A1'}.                                                                  | 1. Deselect 'A1' from Auth Area (ddlOperationArea). <br> 2. Observe Default Area (ddlDefaultOperationArea).                                                                                                                                | Default Area dropdown should automatically deselect 'A1' or prevent saving if 'A1' remains selected but is no longer authorized.                                                                                                                                                | High              |
| DDL\_DEF\_VALID\_01| Auth Area = {'A1', 'A2'}.                                                                                          | 1. Select 'A1' in Default Area (ddlDefaultOperationArea). <br> 2. Fill other required fields. <br> 3. Click #btnSave.                                                                                                                          | Form saves successfully.                                                                                                                                                                                                                                                            | High              |
| DDL\_DEF\_VALID\_02| Auth Area = {'A1', 'A2'}.                                                                                          | 1. Select 'A1' in Auth Area. <br> 2. Select 'A2' in Default Area (even if UI prevents this, test the save). <br> 3. Fill other required fields. <br> 4. Click #btnSave.                                                                         | Form submission fails. An error message indicates that the Default Area selection ('A2') is not present in the Authorized Area selection ('A1'). The specific error toast `showErrorToasterNotification` should appear with a relevant message.                                   | High              |
| DDL\_DEF\_VALID\_03| Auth Area = {'A1', 'A2'}. Default Area = {'A1', 'A2'}.                                                             | 1. Deselect 'A2' from Auth Area. <br> 2. Leave 'A2' selected in Default Area. <br> 3. Click #btnSave or #update.                                                                                                                           | Form submission fails. Validation error for Default vs. Authorized mismatch.                                                                                                                                                                                                        | High              |
| DDL\_DEF\_MULTI\_01| Auth Area = {'A1', 'A2', 'A3'}.                                                                                   | 1. Select 'A1' and 'A2' in Default Area. <br> 2. Fill other required fields. <br> 3. Click #btnSave.                                                                                                                                        | Form saves successfully. The saved record defaults 'A1' and 'A2'.                                                                                                                                                                                                                 | High              |

## Acceptance Criteria: Permission Group Dropdowns (ddlGlobal, ddlPlanner)

*   The dropdowns must load the defined list of specific boolean permissions.
*   The dropdowns must support multi-selection of permissions.
*   Selected permissions must be correctly saved/updated for the user profile.

## Test Cases: Permission Group Dropdowns (ddlGlobal, ddlPlanner)

| Test ID            | Preconditions                                         | Steps to Execute                                                                                                                                                         | Expected Final Result                                                                                                                  | Severity/Priority |
| :----------------- | :---------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DDL\_PERM\_LOAD\_01| Permission flags are defined for ddlGlobal.           | 1. Navigate to page. <br> 2. Click ddlGlobal dropdown.                                                                                                                    | The dropdown expands showing the defined list of Global/Job Summary permissions.                                                         | High              |
| DDL\_PERM\_SEL\_01 | ddlGlobal has options 'Perm A', 'Perm B'.               | 1. Select 'Perm A' in ddlGlobal. <br> 2. Fill other required fields. <br> 3. Click #btnSave.                                                                                | Form saves successfully. The record grants 'Perm A'.                                                                                   | High              |
| DDL\_PERM\_MULTI\_01| ddlPlanner has options 'Plan X', 'Plan Y', 'Plan Z'. | 1. Select 'Plan X' and 'Plan Z' in ddlPlanner. <br> 2. Fill other required fields. <br> 3. Click #btnSave.                                                                  | Form saves successfully. The record grants 'Plan X' and 'Plan Z'.                                                                        | High              |
| DDL\_PERM\_ALL\_01 | ddlGlobal has options and 'Select All'.                 | 1. Click 'Select All' in ddlGlobal. <br> 2. Fill other required fields. <br> 3. Click #btnSave.                                                                             | Form saves successfully. The record grants all permissions listed in ddlGlobal.                                                        | Medium            |
| DDL\_PERM\_DESEL\_01| An existing record grants 'Perm A' in ddlGlobal.        | 1. Edit the record. <br> 2. Deselect 'Perm A' in ddlGlobal. <br> 3. Click #update. <br> 4. Re-edit the same record.                                                         | 3. Update is successful. <br> 4. 'Perm A' is no longer selected in ddlGlobal.                                                          | High              |

## Acceptance Criteria: Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)

*   The checkbox must correctly reflect the current state (checked/unchecked) when editing an existing record.
*   Toggling the checkbox must correctly update the boolean permission value upon Save/Update.

## Test Cases: Sensitive Docs Checkbox (txtAllowToViewSensitiveDocs)

| Test ID        | Preconditions                                             | Steps to Execute                                                                                                         | Expected Final Result                                                                                              | Severity/Priority |
| :------------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- | :---------------- |
| CB\_SENS\_SAVE\_01| Checkbox is unchecked by default.                         | 1. Fill all required fields. <br> 2. Check the 'Allow Sensitive Docs' checkbox. <br> 3. Click #btnSave. <br> 4. Edit the newly created record. | 3. Save is successful. <br> 4. The checkbox is checked when the record loads for editing.                       | Medium            |
| CB\_SENS\_SAVE\_02| Checkbox is unchecked by default.                         | 1. Fill all required fields. <br> 2. Leave the checkbox unchecked. <br> 3. Click #btnSave. <br> 4. Edit the newly created record.   | 3. Save is successful. <br> 4. The checkbox is unchecked when the record loads for editing.                     | Medium            |
| CB\_SENS\_EDIT\_01| Existing record has Sensitive Docs permission = false. | 1. Edit the record. <br> 2. Check the checkbox. <br> 3. Click #update. <br> 4. Re-edit the record.                           | 3. Update is successful. <br> 4. The checkbox is checked.                                                        | Medium            |
| CB\_SENS\_EDIT\_02| Existing record has Sensitive Docs permission = true.  | 1. Edit the record. <br> 2. Uncheck the checkbox. <br> 3. Click #update. <br> 4. Re-edit the record.                         | 3. Update is successful. <br> 4. The checkbox is unchecked.                                                      | Medium            |

## Acceptance Criteria: Save Button (#btnSave)

*   Clicking Save must trigger form validation (Parsley and custom Default/Authorized).
*   If validation fails, submission must be blocked, and appropriate error messages shown.
*   If validation passes, an AJAX request must be sent to the `Insert` web method with the correct payload (`UserPrivilegesSetupobj`).
*   On successful insertion via the backend:
    *   A success message (toast) must be displayed.
    *   The form must be cleared (#btnClear logic).
    *   The grid (#grid) must be refreshed to show the new record.
*   On failure (AJAX error, server error, duplicate record):
    *   An error message (toast) must be displayed.
    *   The form should retain its entered data (allowing correction).

## Test Cases: Save Button (#btnSave)

| Test ID         | Preconditions                                                                 | Steps to Execute                                                                                                                                                                                                 | Expected Final Result                                                                                                                                                              | Severity/Priority |
| :-------------- | :---------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| SAVE\_VALID\_01 | Required fields are empty or invalid.                                           | 1. Click #btnSave.                                                                                                                                                                                               | Submission blocked. Parsley validation errors shown next to invalid fields. No AJAX call made.                                                                                  | High              |
| SAVE\_VALID\_02 | Auth/Default dropdown selections are inconsistent.                              | 1. Select 'A1' in Auth Area. <br> 2. Select 'A2' in Default Area. <br> 3. Fill other required fields. <br> 4. Click #btnSave.                                                                                    | Submission blocked. Error toast shown regarding Default/Authorized mismatch. No AJAX call made.                                                                                  | High              |
| SAVE\_SUCCESS\_01| All required fields are filled correctly. Default selections match Authorized. | 1. Fill form with valid, unique data (user not previously configured). <br> 2. Click #btnSave.                                                                                                                  | Success toast displayed. AJAX call to `Insert` method is successful. Form is cleared. Grid refreshes, showing the new record.                                                     | High              |
| SAVE\_FAIL\_DUP\_01| A privilege record already exists for the selected user ('UserX').           | 1. Select 'UserX' in ddlusers. <br> 2. Fill form with valid data. <br> 3. Click #btnSave.                                                                                                                       | Error toast displayed (e.g., "User already has a privilege configuration"). Form data remains. Grid does not refresh with a duplicate. (Requires backend check)                    | High              |
| SAVE\_FAIL\_AJAX\_01| Network connection is interrupted.                                          | 1. Fill form with valid data. <br> 2. Simulate network error (e.g., using browser dev tools). <br> 3. Click #btnSave.                                                                                             | Error toast displayed (generic AJAX/network error). Form data remains.                                                                                                             | Medium            |
| SAVE\_FAIL\_SRV\_01 | Backend `Insert` method throws an unhandled exception.                        | 1. Fill form with valid data. <br> 2. (Requires mechanism to trigger backend error). <br> 3. Click #btnSave.                                                                                                    | Error toast displayed (server error message). Form data remains.                                                                                                                   | High              |

## Acceptance Criteria: Update Button (#update)

*   The Update button must only be visible after clicking Edit on a grid row.
*   Clicking Update must trigger form validation (Parsley and custom Default/Authorized).
*   If validation fails, submission must be blocked, and appropriate error messages shown.
*   If validation passes, an AJAX request must be sent to the `UpdateUserPrivileges` web method with the correct payload, including the `RecordId`.
*   On successful update via the backend:
    *   A success message (toast) must be displayed.
    *   The form must be cleared (#btnClear logic).
    *   The grid (#grid) must be refreshed to show the updated record.
    *   The UI must revert to 'Save' mode (#btnSave visible, #update hidden).
*   On failure (AJAX error, server error, record not found):
    *   An error message (toast) must be displayed.
    *   The form should retain its entered data (allowing correction).

## Test Cases: Update Button (#update)

| Test ID           | Preconditions                                                                 | Steps to Execute                                                                                                                                                                                                          | Expected Final Result                                                                                                                                                                        | Severity/Priority |
| :---------------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| UPDATE\_VALID\_01 | In Edit mode. Required fields are cleared or made invalid.                    | 1. Edit a record. <br> 2. Clear a required field (e.g., deselect all Customers). <br> 3. Click #update.                                                                                                                    | Submission blocked. Parsley validation errors shown. No AJAX call made.                                                                                                                      | High              |
| UPDATE\_VALID\_02 | In Edit mode. Auth/Default dropdown selections are made inconsistent.           | 1. Edit a record where Auth Area = {'A1', 'A2'}, Default Area = {'A1'}. <br> 2. Deselect 'A1' from Auth Area. <br> 3. Click #update.                                                                                       | Submission blocked. Error toast shown regarding Default/Authorized mismatch. No AJAX call made.                                                                                              | High              |
| UPDATE\_SUCCESS\_01| In Edit mode. Valid changes made. Default selections match Authorized.      | 1. Edit a record. <br> 2. Make a valid change (e.g., add an Authorized Customer). <br> 3. Click #update.                                                                                                                     | Success toast displayed. AJAX call to `UpdateUserPrivileges` is successful. Form is cleared. Grid refreshes, showing the updated record. UI reverts to Save mode (#btnSave visible, #update hidden). | High              |
| UPDATE\_FAIL\_NF\_01| In Edit mode. The record was deleted by another user concurrently.            | 1. Edit a record. <br> 2. (Requires mechanism to delete record from DB before update). <br> 3. Make a valid change. <br> 4. Click #update.                                                                                 | Error toast displayed (e.g., "Record not found" or update failed). Form data remains. (Requires backend check)                                                                               | Medium            |
| UPDATE\_FAIL\_AJAX\_01| In Edit mode. Network connection interrupted during update.                | 1. Edit a record. <br> 2. Make a valid change. <br> 3. Simulate network error. <br> 4. Click #update.                                                                                                                      | Error toast displayed (generic AJAX/network error). Form data remains.                                                                                                                       | Medium            |
| UPDATE\_FAIL\_SRV\_01 | In Edit mode. Backend `UpdateUserPrivileges` method throws an exception.      | 1. Edit a record. <br> 2. Make a valid change. <br> 3. (Requires mechanism to trigger backend error). <br> 4. Click #update.                                                                                              | Error toast displayed (server error message). Form data remains.                                                                                                                             | High              |

## Acceptance Criteria: Clear Button (#btnClear)

*   Clicking Clear must reset all form fields (dropdowns, checkboxes) to their initial state (empty/unchecked).
*   Clicking Clear must remove any Parsley validation messages from the form.
*   Clicking Clear must ensure the UI is in 'Save' mode (#btnSave visible, #update hidden).

## Test Cases: Clear Button (#btnClear)

| Test ID         | Preconditions                                                       | Steps to Execute                                                                                               | Expected Final Result                                                                                                         | Severity/Priority |
| :-------------- | :------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| CLEAR\_SAVE\_01 | Form is in Save mode. Some fields are populated.                  | 1. Enter data into several fields (e.g., select user, customers). <br> 2. Click #btnClear.                       | All form fields are cleared/deselected. Save button remains visible, Update button remains hidden.                              | Medium            |
| CLEAR\_EDIT\_01 | Form is in Edit mode (after clicking Edit). Form data is populated. | 1. Edit a record. <br> 2. Click #btnClear.                                                                     | All form fields are cleared/deselected. Update button is hidden, Save button becomes visible.                               | Medium            |
| CLEAR\_VALID\_01 | Form has validation errors displayed after attempting to Save.    | 1. Attempt to save with invalid data, triggering validation messages. <br> 2. Click #btnClear.                  | All form fields are cleared. All Parsley validation messages are removed. UI is in Save mode.                               | Medium            |

## Acceptance Criteria: Edit Button (in grid)

*   Clicking the Edit button on a grid row must trigger an AJAX call to the `Edit` web method with the correct `recordid`.
*   On successful data retrieval from the backend:
    *   The form (#form1) must be populated accurately with all the data for the selected record.
    *   All dropdowns (User, Authorized, Default, Permissions) and checkboxes must reflect the saved state.
    *   The UI must switch to 'Edit' mode (#btnSave hidden, #update visible).
    *   The `RecordId` must be stored internally for use when clicking Update.
*   On failure (AJAX error, server error, record not found):
    *   An error message (toast) must be displayed.
    *   The form should remain in its previous state (likely empty or showing previously edited data).

## Test Cases: Edit Button (in grid)

| Test ID         | Preconditions                                                                           | Steps to Execute                                                                                                                                                              | Expected Final Result                                                                                                                                                                                                        | Severity/Priority |
| :-------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| EDIT\_SUCCESS\_01| Grid displays a record with known data (User: U1, AuthCust: C1, DefArea: A1, SensDocs: true). | 1. Click the Edit button for the specific record.                                                                                                                             | AJAX call to `Edit` method succeeds. Form populates: ddlusers shows U1, ddlCustomer shows C1 selected, ddlDefaultOperationArea shows A1 selected, txtAllowToViewSensitiveDocs is checked. #update button is visible, #btnSave is hidden. | High              |
| EDIT\_FAIL\_NF\_01| Grid displays a record, but it has been deleted from the DB concurrently.                 | 1. (Requires deleting record from DB after grid load but before clicking Edit). <br> 2. Click the Edit button for the deleted record.                                        | Error toast displayed ("Record not found" or similar). Form remains empty or unchanged. #update button remains hidden.                                                                                                       | Medium            |
| EDIT\_FAIL\_AJAX\_01| Network connection interrupted.                                                         | 1. Simulate network error. <br> 2. Click the Edit button for any record.                                                                                                       | Error toast displayed (generic AJAX/network error). Form remains empty or unchanged.                                                                                                                                         | Medium            |
| EDIT\_FAIL\_SRV\_01 | Backend `Edit` method throws an exception.                                                | 1. (Requires mechanism to trigger backend error). <br> 2. Click the Edit button for any record.                                                                                | Error toast displayed (server error message). Form remains empty or unchanged.                                                                                                                                               | High              |
| EDIT\_DATA\_COMPLEX| Record has multiple selections in multi-select dropdowns (Auth/Default/Permissions).    | 1. Click Edit for the complex record.                                                                                                                                       | Form populates correctly, with all previously saved multi-select options selected in their respective dropdowns.                                                                                                             | High              |

## Acceptance Criteria: Delete Button (in grid)

*   Clicking the Delete button on a grid row must display a confirmation dialog (SweetAlert2).
*   If deletion is cancelled, no action is taken.
*   If deletion is confirmed, an AJAX request must be sent to the `deleteUserPrivileges` web method with the correct `recordid`.
*   On successful deletion via the backend:
    *   A success message (toast) must be displayed.
    *   The grid (#grid) must be refreshed, and the deleted record must no longer be visible.
*   On failure (AJAX error, server error, record not found, deletion constraint):
    *   An error message (toast) must be displayed.
    *   The grid should not change.

## Test Cases: Delete Button (in grid)

| Test ID           | Preconditions                                                   | Steps to Execute                                                                                                                                                   | Expected Final Result                                                                                                                                                      | Severity/Priority |
| :---------------- | :-------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DELETE\_CONFIRM\_01| Grid displays records.                                          | 1. Click the Delete button for a record. <br> 2. Observe the dialog.                                                                                               | A confirmation dialog (SweetAlert2) appears asking to confirm deletion.                                                                                                    | High              |
| DELETE\_CANCEL\_01 | Confirmation dialog is displayed after clicking Delete.         | 1. Click the 'Cancel' (or equivalent) button on the confirmation dialog.                                                                                         | The dialog closes. No AJAX call is made. The grid remains unchanged.                                                                                                       | Medium            |
| DELETE\_SUCCESS\_01| Confirmation dialog is displayed. Record exists.                | 1. Click the 'Confirm' (or equivalent) button on the dialog.                                                                                                     | Success toast displayed. AJAX call to `deleteUserPrivileges` is successful. Grid refreshes, and the deleted record is removed from the view.                                  | High              |
| DELETE\_FAIL\_NF\_01| Confirmation dialog is displayed. Record deleted concurrently. | 1. (Requires deleting record from DB after clicking Delete but before confirming). <br> 2. Click 'Confirm'.                                                        | Error toast displayed ("Record not found" or similar). Grid does not change (or may refresh but the record was already gone). (Requires backend check)                       | Medium            |
| DELETE\_FAIL\_AJAX\_01| Confirmation dialog is displayed. Network error occurs.        | 1. Simulate network error. <br> 2. Click 'Confirm'.                                                                                                              | Error toast displayed (generic AJAX/network error). Grid does not change.                                                                                                  | Medium            |
| DELETE\_FAIL\_SRV\_01 | Confirmation dialog is displayed. Backend `delete` fails.     | 1. (Requires mechanism to trigger backend error, e.g., DB constraint). <br> 2. Click 'Confirm'.                                                                    | Error toast displayed (server/database error message). Grid does not change.                                                                                               | High              |

# 4. Testing Strategy and Requirements

This strategy outlines the approach for ensuring the quality and correctness of the 1608 User Privileges application module.

## Testing Types

A multi-layered testing approach is recommended:

1.  **Component Testing (UI Focused):**
    *   Verify individual UI elements (#grid, #form1, dropdowns, buttons) function as expected in isolation (rendering, basic interaction).
    *   Test client-side validation (Parsley.js) for required fields and formats.
    *   Test specific JavaScript functions (`edituserPrivileges`, `deleteuserPrivileges`, dropdown handlers, validation logic).
2.  **Integration Testing:**
    *   **UI <-> Backend:** Test the interaction between client-side JavaScript (AJAX calls) and backend C# Web Methods (`Insert`, `Edit`, `UpdateUserPrivileges`, `deleteUserPrivileges`). Verify request payloads and response handling (success/error).
    *   **Backend <-> Database:** Test the interaction between C# methods (`DataOperations`) and the SQL Stored Procedure (`SP_FormDataPRIDUserPrivilegesSetup`). Verify correct parameters are passed and results (DataSets, messages) are handled appropriately. Focus on different `@value1` parameter calls to the SP.
    *   **End-to-End (E2E):** Test complete user workflows (Load -> View -> Edit -> Update -> Verify; Load -> Create -> Save -> Verify; Load -> Delete -> Verify).
3.  **System Testing:**
    *   Verify the module integrates correctly within the larger application context (if applicable). Specifically, how do the privileges set here affect other parts of the system? (This may require testing outside this specific module).
4.  **Data Validation Testing:**
    *   Focus heavily on the integrity of the `User Privilege Configuration Data`.
    *   Verify correct saving/retrieval of all permission flags and entity lists (Authorized/Default).
    *   Test the Default vs. Authorized validation logic thoroughly under various scenarios.
    *   Test edge cases like selecting 'All' vs. individual items and the interaction between Auth/Default pairs.
5.  **Regression Testing:**
    *   Execute a subset of high-priority test cases (especially around CRUD operations and core validation) after any code changes or bug fixes to ensure no existing functionality is broken.
6.  **Usability Testing:**
    *   Evaluate the ease of use for administrators configuring privileges. Are the dropdowns clear? Is the workflow intuitive? Is feedback (success/error messages) helpful?
7.  **Performance Testing (Basic):**
    *   Verify acceptable load times for the grid and dropdown population, especially with potentially large lists of users or entities.
    *   Verify acceptable response times for Save, Update, Delete operations under normal load.

## Key Business Requirements Validation

The test cases derived from the component analysis and behaviors directly validate the core business requirements:

*   **Manage User Privileges:** Validated by CRUD test cases (Save, Edit, Update, Delete) and grid display tests.
*   **Define Authorized Entities:** Validated by test cases focusing on selecting and saving/updating data in Authorized dropdowns.
*   **Define Default Entities:** Validated by test cases focusing on Default dropdowns and the critical Default vs. Authorized validation logic.
*   **Assign Specific Permissions:** Validated by test cases involving the Permission Group dropdowns and the Sensitive Docs checkbox.
*   **Data Integrity:** Validated by tests ensuring correct data persistence, validation rules enforcement, and error handling for duplicates or invalid states.
*   **Usability:** Assessed through general testing and specific usability checks.

## Risk-Based Prioritization

Testing efforts should be prioritized based on risk and criticality:

1.  **High Priority:**
    *   Core CRUD operations: Save, Edit, Update, Delete functionality.
    *   Data Integrity: Correctness of saved/retrieved data (especially permissions and entity lists).
    *   Validation Logic: Parsley rules and, critically, the Default vs. Authorized dropdown validation.
    *   Security: Ensuring only authorized administrators can access this page (Assumed, but critical). Ensuring privilege data isn't exposed incorrectly.
2.  **Medium Priority:**
    *   Grid Functionality: Sorting, Filtering, Paging. Accurate display of data.
    *   Dropdown Population and Interaction: Ensuring lists load correctly and Auth/Default synchronization works.
    *   Error Handling: Correct display of user-friendly error messages for common failures (validation, duplicates, server errors).
    *   Form Clearing and UI State Management (Save/Update modes).
3.  **Low Priority:**
    *   Grid Export to Excel.
    *   Minor UI/Layout issues (unless impacting usability significantly).
    *   Performance under extreme load (unless specific requirements exist).

## Architectural Considerations

*   **Tight Coupling (UI <-> Backend <-> SP):** The architecture relies heavily on specific web method calls and a single large stored procedure. Changes in one layer can easily break others. Integration testing is crucial.
*   **Client-Side Logic:** Significant logic exists in JavaScript (validation, UI updates, AJAX calls). Thorough testing in different browsers (if required) is important.
*   **Stored Procedure Complexity:** The `SP_FormDataPRIDUserPrivilegesSetup` handles multiple operations based on a parameter. Testing must cover all execution paths within the SP triggered by different UI actions. Direct SP testing (if possible) or careful analysis of its logic is beneficial.
*   **Data Structure:** The `User Privilege Configuration Data` is complex, involving multiple lists and flags. Test cases must cover various combinations of these settings.
*   **State Management:** Ensure the UI correctly reflects the application state (Save vs. Update mode, populated form vs. clear form).

# 5. Error Handling and Edge Cases

This section catalogs potential errors, expected behavior, and recovery steps.

## Validation Errors

| Error Condition                                  | How to Reproduce                                                                   | Expected Behavior                                                                              | Recovery Steps                       | Verification                                                                |
| :----------------------------------------------- | :--------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :----------------------------------- | :-------------------------------------------------------------------------- |
| Required Field Empty (Parsley)                   | Click Save/Update without selecting a user or required authorized entity.          | Submission prevented. Red border/icon and/or message appears next to the invalid field(s).     | Fill in the required field(s).     | Validation message disappears. Submission proceeds on next valid attempt. |
| Invalid Default vs. Authorized Selection       | Select an item in a Default dropdown that isn't selected in its Authorized pair. Click Save/Update. | Submission prevented. Error toast displayed (`showErrorToasterNotification`) with relevant message. | Correct the selections in Default and/or Authorized dropdowns. | Error toast does not appear. Submission proceeds on next valid attempt.   |
| Invalid Data Format (if applicable, e.g., dates) | Enter data in an incorrect format into a validated field.                           | Submission prevented. Parsley validation message shown.                                        | Correct the data format.           | Validation message disappears. Submission proceeds on next valid attempt. |

## Data Integrity Errors

| Error Condition                         | How to Reproduce                                                         | Expected Behavior                                                                                                | Recovery Steps                                                     | Verification                                                               |
| :-------------------------------------- | :----------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- | :------------------------------------------------------------------------- |
| Duplicate User Privilege (Save)         | Attempt to Save a new privilege configuration for a user who already has one. | Submission likely prevented by backend/SP check. Error toast displayed ("User already configured" or similar). | Clear the form or select a different user. Edit the existing record if needed. | Subsequent save attempt for a *different* user succeeds.                   |
| Record Not Found (Update/Delete/Edit) | Attempt to Update, Delete, or Edit a record that was deleted concurrently. | AJAX call fails or returns specific error. Error toast displayed ("Record not found" or similar).                | Refresh the grid to see the current state. Select a valid record. | Action succeeds on an existing record.                                     |
| Database Constraint Violation (Save/Update) | Trigger a DB constraint (e.g., foreign key issue if related data is missing). | AJAX call fails. Error toast displayed (potentially generic server error or specific DB error if passed through). | Correct the underlying data issue (may require admin action). Retry. | Action succeeds when data is valid.                                        |
| Stored Procedure Logic Error            | Provide input data that triggers a logical flaw within the SP.           | AJAX call may succeed but data is saved incorrectly, or SP returns an error message. Error toast may appear. | Requires code fix in SP. Report bug with reproducible steps.       | Data is saved/updated/deleted correctly after SP fix.                    |

## Server/Network Errors

| Error Condition                                    | How to Reproduce                                                                                             | Expected Behavior                                                                                   | Recovery Steps                                                                        | Verification                                                                       |
| :------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------- |
| AJAX Call Failure (Network Error, Timeout, 4xx/5xx) | Interrupt network connectivity during Save/Update/Delete/Edit/Grid Load. Server returns 500 error.             | Operation fails. Error toast displayed (generic network/server error message). Form data often retained. | Check network connection. Wait and retry the operation. Report persistent server errors. | Operation succeeds when network/server is stable.                                |
| Backend Web Method Exception (Unhandled)           | Trigger an unhandled C# exception in the `Insert`, `Edit`, `UpdateUserPrivileges`, or `deleteUserPrivileges` methods. | AJAX call fails. Error toast displayed (likely generic server error message). Form data often retained. | Report bug with reproducible steps. Requires code fix.                                | Operation succeeds after backend fix.                                            |
| Failure to Load Dropdown Data (Page Load)          | Simulate backend/DB error during the C# methods called in `Page_Load` to populate dropdowns.                     | Page may load partially, or dropdowns remain empty. Potential JS errors if code expects populated lists. | Refresh the page. Report persistent errors. Requires backend/DB fix.                  | Page loads correctly with all dropdowns populated when backend/DB is stable.     |
| Failure to Load Grid Data (Page Load/Refresh)      | Simulate backend/DB error during the `GetData` call for the Kendo Grid.                                      | Grid displays an error message or remains empty.                                                    | Refresh the page/grid. Report persistent errors. Requires backend/DB fix.           | Grid loads correctly when backend/DB is stable.                                  |

## Concurrency Issues

| Error Condition                                    | How to Reproduce                                                                                                       | Expected Behavior                                                                                                                      | Recovery Steps                                         | Verification                                                               |
| :------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- | :------------------------------------------------------------------------- |
| Editing Stale Data                                 | User A opens record X for editing. User B edits and saves record X. User A then clicks Update.                         | Update should ideally fail with a "record modified" error (optimistic concurrency check). If no check exists, User A's changes overwrite User B's. | Refresh data before editing. Implement concurrency checks. | Update fails gracefully, prompting user to reload data.                    |
| Deleting Record Being Edited                       | User A opens record X for editing. User B deletes record X. User A clicks Update.                                      | Update fails with "Record not found" error.                                                                                            | Refresh the grid. Inform user the record was deleted. | Update fails with appropriate message.                                     |
| Saving Duplicate Record Simultaneously (Race Condition) | Two users attempt to save a new configuration for the *same new user* at almost the exact same time.                     | Database constraint (unique key on User) should prevent one insert. One user gets success, the other gets a duplicate error.            | Inform user the record was just created. Refresh grid. | Only one record is created in the database. The second user gets an error. |