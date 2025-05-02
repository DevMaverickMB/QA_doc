# 1365 QA Document

**Table of Contents**
1.  [Application Overview](#1-application-overview)
    *   [Purpose and Functionality](#purpose-and-functionality)
    *   [Technology Stack](#technology-stack)
2.  [Component Action Mapping Documentation](#2-component-action-mapping-documentation)
    *   [Requestor Form (#form1)](#requestor-form-form1)
    *   [Requestor Grid (#grid)](#requestor-grid-grid)
3.  [Acceptance Criteria and Test Cases](#3-acceptance-criteria-and-test-cases)
    *   [Acceptance Criteria: Requestor Form (#form1)](#acceptance-criteria-requestor-form-form1)
    *   [Test Cases: Requestor Form (#form1)](#test-cases-requestor-form-form1)
    *   [Acceptance Criteria: Requestor Grid (#grid)](#acceptance-criteria-requestor-grid-grid)
    *   [Test Cases: Requestor Grid (#grid)](#test-cases-requestor-grid-grid)
4.  [Testing Strategy and Requirements](#4-testing-strategy-and-requirements)
    *   [Testing Types](#testing-types)
    *   [Business Requirements Validation](#business-requirements-validation)
    *   [Risk-Based Prioritization](#risk-based-prioritization)
    *   [Special Considerations](#special-considerations)
5.  [Error Handling and Edge Cases](#5-error-handling-and-edge-cases)
    *   [Client-Side Validation Errors (Parsley.js)](#client-side-validation-errors-parsleyjs)
    *   [Server-Side Duplicate Entry](#server-side-duplicate-entry)
    *   [Data Fetching/Loading Errors (AJAX/Server)](#data-fetchingloading-errors-ajaxserver)
    *   [Record Not Found (Edit/Delete)](#record-not-found-editdelete)
    *   [Database Errors](#database-errors)

---

## 1. Application Overview

### Purpose and Functionality
Project 1365 is a web application designed for managing "Requestor" or "Dispatcher" contact information. Its primary function is to provide users with the ability to Create, Read, Update, and Delete (CRUD) requestor records associated with specific customers or companies. The application features a user-friendly interface consisting of a data entry form for adding or editing requestor details (Customer/Company, First Name, Last Name, Email) and a data grid for viewing, sorting, filtering, and managing the list of existing requestors.

### Technology Stack
The application utilizes the following technologies and frameworks:

*   **Backend:** C# (ASP.NET Web Forms - inferred from WebMethods and code-behind), .NET Framework
*   **Frontend:** HTML, JavaScript, jQuery (likely)
*   **UI Components:** Kendo UI for jQuery (Data Grid), Standard HTML form elements
*   **Client-Side Validation:** Parsley.js
*   **Client-Side Notifications:** SweetAlert (likely for confirmation dialogs and status messages)
*   **Data Communication:** AJAX (Asynchronous JavaScript and XML) for client-server interaction
*   **Database:** Microsoft SQL Server (inferred from Stored Procedure `SP_formdataPRIDDispatcherMaster`)
*   **Database Access:** ADO.NET (likely, interacting with Stored Procedures)

---

## 2. Component Action Mapping Documentation

This section details the interactions, behaviors, and expected outcomes for the primary UI components.

### Requestor Form (#form1)
This component encompasses the input fields (`#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`), action buttons (`#save`, `#clear`), and the hidden field (`#recordId`).

| Trigger/Event             | Action                                      | Target/Effect                                                                                                | Data Elements                                                                                                 | Validation Rules                                                                    | Error Scenarios                                                                        | Test Priority | Expected Performance                     |
| :------------------------ | :------------------------------------------ | :----------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :------------ | :--------------------------------------- |
| Page Load                 | `LoadCompany()` JS Function                 | Populates `#ddlCompany` dropdown with customer/company data fetched via `GetCompany` WebMethod (AJAX).         | Company List (ID, Name)                                                                                       | None directly on load.                                                              | AJAX error fetching companies, Server error in `GetCompany`, DB connection error.      | High          | Dropdown populated within 1-2 seconds.   |
| User selects Company      | Standard `<select>` change event            | Updates the selected value for `#ddlCompany`.                                                                | `#ddlCompany` value                                                                                           | None on selection.                                                                  | N/A                                                                                    | Medium        | Immediate UI update.                     |
| User inputs text          | Standard `input` event                      | Updates the value of `#txtfirstname`, `#txtlastname`, `#txtemail`.                                           | Input field values                                                                                            | Basic character restrictions (inferred, JS), HTML5 email format (`#txtemail`).        | N/A (part of Save) | Immediate visual feedback.               |
| Click `#clear` Button     | `clear` button JS click handler             | Resets `#form1` fields to default, clears Parsley validation errors, resets `#recordId` to '0', resets `#save` button text to 'Save', calls `LoadCompany()` (to ensure dropdown state). | `#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`, `#recordId`, `#save` text | None.                                                                               | Unlikely.                                                                              | Medium        | Form cleared instantly.                  |
| Click `#save` Button (New Record: `#recordId` = '0') | `#save` button JS click handler             | 1. Triggers Parsley validation. 2. If valid, sends form data via AJAX to `insert` WebMethod. 3. On success: shows notification, calls `clear` handler, refreshes `#grid`. | `#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`, `#recordId` ('0')       | Parsley: All fields required, `#txtemail` valid email format. Server: Duplicate check. | Validation fails (Parsley), Duplicate record found (Server), AJAX error, Server error. | High          | Validation immediate. Save < 3 seconds.  |
| Click `#save` Button (Update Record: `#recordId` != '0') | `#save` button JS click handler (Button text is 'Update') | 1. Triggers Parsley validation. 2. If valid, sends form data + `#recordId` via AJAX to `insert` WebMethod. 3. On success: shows notification, calls `clear` handler, refreshes `#grid`. | `#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`, `#recordId` (> 0)      | Parsley: All fields required, `#txtemail` valid email format. Server: Duplicate check. | Validation fails (Parsley), Duplicate record found (Server), AJAX error, Server error. | High          | Validation immediate. Update < 3 seconds. |

### Requestor Grid (#grid)
This component is the Kendo UI Grid responsible for displaying and managing requestor records.

| Trigger/Event            | Action                                         | Target/Effect                                                                                             | Data Elements                                                                    | Validation Rules | Error Scenarios                                                                                                  | Test Priority | Expected Performance                           |
| :----------------------- | :--------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------- | :--------------- | :--------------------------------------------------------------------------------------------------------------- | :------------ | :------------------------------------------- |
| Page Load                | `LoadGrid()` JS Function                       | Initializes Kendo Grid, triggers initial data load via AJAX call to `GetData` endpoint.                     | Requestor List (Company, Name, Email, ID)                                        | N/A              | AJAX error fetching data, Server error generating data, DB connection error, Empty result set (not an error).      | High          | Grid populated within 2-5 seconds (depends on data). |
| Grid Refresh (Manual/Auto) | `kendoGrid.dataSource.read()`                  | Re-fetches data from `GetData` endpoint via AJAX and updates the grid display.                            | Requestor List (Company, Name, Email, ID)                                        | N/A              | AJAX error fetching data, Server error generating data, DB connection error.                                   | High          | Grid updated within 2-5 seconds.             |
| Click 'Edit' button (row) | `Edit(recordid)` JS Function                   | 1. Calls `Edit` WebMethod via AJAX to fetch record data. 2. Populates `#form1` with fetched data. 3. Calls `LoadCompany(companyId)` to select correct company. 4. Sets `#recordId`. 5. Changes `#save` button text to 'Update'. | Single Requestor Record (ID, CompanyID, FirstName, LastName, Email), `#recordId` | N/A              | Record not found, AJAX error, Server error in `Edit` WebMethod, Error populating form.                         | High          | Form populated < 2 seconds after click.    |
| Click 'Delete' button (row) | `Delete(recordid)` JS Function                 | 1. Shows SweetAlert confirmation. 2. If confirmed, calls `Delete` WebMethod via AJAX. 3. On success: shows notification, refreshes grid (`dataSource.read()`). | `recordid`                                                                       | User Confirmation | Record not found, AJAX error, Server error in `Delete` WebMethod, DB error during update (FlagActive=0).        | High          | Confirmation immediate. Deletion < 3 seconds. |
| Sort Column              | Kendo Grid internal sort mechanism             | Sends sort parameters via AJAX to `GetData`, re-fetches sorted data, updates grid display.                  | Sort field, Sort direction                                                       | N/A              | AJAX error, Server error during sorting/data retrieval.                                                          | Medium        | Grid updated < 3 seconds.                    |
| Filter Column            | Kendo Grid internal filter mechanism           | Sends filter parameters via AJAX to `GetData`, re-fetches filtered data, updates grid display.              | Filter field, Filter operator, Filter value                                      | N/A              | AJAX error, Server error during filtering/data retrieval.                                                        | Medium        | Grid updated < 3 seconds.                    |
| Change Page              | Kendo Grid internal paging mechanism           | Sends paging parameters (page number, page size) via AJAX to `GetData`, fetches data for the specific page. | Page number, Page size                                                           | N/A              | AJAX error, Server error during paging/data retrieval.                                                           | Medium        | Grid updated < 3 seconds.                    |
| Click 'Export to Excel' | Kendo Grid internal export mechanism (if enabled) | Generates and downloads an Excel file containing the currently displayed (or all) grid data.             | Grid data                                                                        | N/A              | Error during file generation (client or server side), browser blocking download.                               | Medium        | Download starts within 5 seconds.            |
| Search (if enabled)      | Kendo Grid internal search mechanism           | Sends search term via AJAX to `GetData`, re-fetches filtered data, updates grid display.                    | Search term                                                                      | N/A              | AJAX error, Server error during searching/data retrieval.                                                        | Medium        | Grid updated < 3 seconds.                    |

---

## 3. Acceptance Criteria and Test Cases

### Acceptance Criteria: Requestor Form (#form1)

*   The Company dropdown (`#ddlCompany`) must be populated with a list of active companies/customers on page load.
*   All input fields (`#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`) must be validated as required before saving.
*   The Email field (`#txtemail`) must be validated for a correct email format (client-side).
*   Clicking the 'Save' button with valid data for a new record (`#recordId`='0') must successfully add a new requestor to the system, display a success message, clear the form, and refresh the Requestor Grid (#grid) to show the new entry.
*   Attempting to save a new record that results in a server-side duplicate check failure must prevent the save, display an appropriate 'Duplicate' error message, and leave the form data intact for correction.
*   Clicking the 'Edit' button on a grid row must populate the form fields with the correct data for that requestor, set the `#recordId`, select the correct Company in the dropdown, and change the 'Save' button text to 'Update'.
*   Clicking the 'Update' button (formerly 'Save') with valid data for an existing record (`#recordId` > 0) must successfully update the requestor in the system, display a success message, clear the form (resetting button text), and refresh the Requestor Grid (#grid) to show the updated entry.
*   Attempting to update a record that results in a server-side duplicate check failure must prevent the update, display an appropriate 'Duplicate' error message, and leave the form data intact for correction.
*   Clicking the 'Clear' button must reset all form fields to their default empty/initial state, clear any validation messages, reset `#recordId` to '0', and reset the 'Save' button text to 'Save'.

### Test Cases: Requestor Form (#form1)

| Test ID        | Preconditions                                     | Steps to Execute                                                                                                                                                                                                                                                         | Expected Final Result                                                                                                                                                                                                                                 | Severity/Priority |
| :------------- | :------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| **FORM_ADD_01** | Page loaded, form is empty, `#recordId` is '0'.   | 1. Select a company from `#ddlCompany`. <br> 2. Enter valid text in `#txtfirstname`. <br> 3. Enter valid text in `#txtlastname`. <br> 4. Enter a valid email in `#txtemail`. <br> 5. Click `#save` button.                                                                        | Requestor is saved successfully. Success notification shown. Form fields are cleared. `#recordId` is '0'. `#save` button text is 'Save'. Grid is refreshed and shows the newly added requestor.                                                        | High              |
| **FORM_ADD_02** | Page loaded, form is empty.                       | 1. Click `#save` button without entering any data.                                                                                                                                                                                                                         | Parsley validation errors appear for all required fields (`#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`). Form is not submitted. No AJAX call made.                                                                                 | High              |
| **FORM_ADD_03** | Page loaded, form is empty.                       | 1. Select a company. <br> 2. Enter first name. <br> 3. Enter last name. <br> 4. Enter an invalid email format (e.g., "test@test") in `#txtemail`. <br> 5. Click `#save`.                                                                                                      | Parsley validation error appears for `#txtemail` field indicating invalid format. Form is not submitted.                                                                                                                                               | High              |
| **FORM_ADD_04** | A requestor with specific Company/Name/Email exists. | 1. Select the same company as the existing requestor. <br> 2. Enter the same first name. <br> 3. Enter the same last name. <br> 4. Enter the same email. <br> 5. Click `#save`.                                                                                             | Form validation passes. AJAX call is made. Server returns a 'Duplicate' error message. Error notification shown. Form fields remain populated. Grid is not refreshed with a new entry.                                                            | High              |
| **FORM_EDIT_01** | Grid contains at least one requestor record.      | 1. Click the 'Edit' button on a grid row.                                                                                                                                                                                                                                | Form fields (`#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`) are populated with the data from the selected row. `#recordId` contains the ID of the edited record. `#save` button text changes to 'Update'. The correct company is selected. | High              |
| **FORM_EDIT_02** | Form is populated for editing (via FORM_EDIT_01). | 1. Modify the value in `#txtfirstname`. <br> 2. Click the 'Update' button (`#save`).                                                                                                                                                                                     | Requestor is updated successfully. Success notification shown. Form fields are cleared. `#recordId` is '0'. `#save` button text is 'Save'. Grid is refreshed and shows the updated first name for the requestor.                                        | High              |
| **FORM_EDIT_03** | Form is populated for editing.                    | 1. Clear the value in `#txtlastname`. <br> 2. Click the 'Update' button (`#save`).                                                                                                                                                                                       | Parsley validation error appears for `#txtlastname` (required). Form is not submitted. Data remains in the form.                                                                                                                                      | High              |
| **FORM_EDIT_04** | Form populated for editing. Another record exists with details "CompX,FNameY,LNameY,EmailY". | 1. Change form data to match the *other* existing record: Company='CompX', First Name='FNameY', Last Name='LNameY', Email='EmailY'. <br> 2. Click 'Update'.                                                                                   | Form validation passes. AJAX call is made. Server returns 'Duplicate' error. Error notification shown. Form fields remain populated with the conflicting data. Grid is not updated.                                                              | High              |
| **FORM_CLEAR_01**| Form fields are populated (new or edit mode).   | 1. Click `#clear` button.                                                                                                                                                                                                                                                | All form fields (`#ddlCompany`, `#txtfirstname`, `#txtlastname`, `#txtemail`) are reset/cleared. `#recordId` is set to '0'. `#save` button text is 'Save'. Parsley validation errors (if any) are removed.                                          | Medium            |
| **FORM_VALID_01**| Page loaded, form is empty.                       | 1. Enter text in all fields except `#ddlCompany`. <br> 2. Click `#save`.                                                                                                                                                                                                 | Validation error on `#ddlCompany`.                                                                                                                                                                                                                  | High              |
| **FORM_VALID_02**| Page loaded, form is empty.                       | 1. Select company, enter first/last name, leave `#txtemail` empty. <br> 2. Click `#save`.                                                                                                                                                                                | Validation error on `#txtemail`.                                                                                                                                                                                                                    | High              |
| **FORM_VALID_03**| Page loaded, form is empty.                       | 1. Enter very long strings in text fields (boundary test). <br> 2. Enter email with unusual valid characters (e.g., `+`, `.`, `-`). <br> 3. Click `#save`.                                                                                                             | If length limits exist, they should be enforced (implicitly or explicitly). Valid email formats should pass Parsley validation. Save should proceed if data is valid according to rules. Check DB for truncation if limits apply.                 | Medium            |

### Acceptance Criteria: Requestor Grid (#grid)

*   The grid must load and display the list of active requestor records when the page is accessed.
*   The grid must display the correct data in the defined columns (e.g., Company, First Name, Last Name, Email, Actions).
*   Grid data must be retrieved asynchronously without full page reloads.
*   Users must be able to sort the data by clicking on column headers (ascending/descending).
*   Users must be able to filter the data using the grid's filtering controls.
*   If the data spans multiple pages, users must be able to navigate between pages using the grid's pagination controls.
*   Each row must contain functional 'Edit' and 'Delete' buttons/links.
*   Clicking the 'Delete' button must prompt the user for confirmation before proceeding.
*   After a successful Delete operation, the corresponding row must be removed from the grid view upon refresh.
*   The grid must refresh automatically after successful Add, Update, or Delete operations initiated from the form or grid actions.
*   If enabled, the 'Export to Excel' functionality must correctly generate and download an Excel file containing the grid data.

### Test Cases: Requestor Grid (#grid)

| Test ID        | Preconditions                                                       | Steps to Execute                                                                                                                                                  | Expected Final Result                                                                                                                                                              | Severity/Priority |
| :------------- | :------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| **GRID_LOAD_01** | Application deployed, Database contains requestor records.        | 1. Navigate to the Requestor management page.                                                                                                                     | The Kendo UI grid (`#grid`) loads and displays the list of requestors fetched from the database. Columns (Company, Name, Email, Actions) are visible and populated correctly.         | High              |
| **GRID_LOAD_02** | Database contains no requestor records.                             | 1. Navigate to the Requestor management page.                                                                                                                     | The grid loads but displays a "No records found" (or similar) message.                                                                                                               | Medium            |
| **GRID_SORT_01** | Grid is loaded with multiple records with different First Names. | 1. Click the header for the 'First Name' column. <br> 2. Click the header for the 'First Name' column again.                                                      | 1. Grid data is sorted alphabetically (A-Z) by First Name. <br> 2. Grid data is sorted reverse alphabetically (Z-A) by First Name.                                                  | Medium            |
| **GRID_FILTER_01**| Grid is loaded with multiple records, some with Company 'ABC'.   | 1. Use the grid's filter control for the 'Company' column. <br> 2. Enter 'ABC' and apply the filter (e.g., 'Contains' or 'Equals').                               | Only rows where the Company is 'ABC' are displayed in the grid.                                                                                                                    | Medium            |
| **GRID_PAGE_01** | Grid is configured for pagination (e.g., 10 items/page), DB has >10 records. | 1. Observe the pagination controls (e.g., page numbers, next/prev buttons). <br> 2. Click the 'Next' page button or page number '2'.                        | 1. Pagination controls are visible and indicate multiple pages. <br> 2. The grid displays the second page of records (e.g., records 11-20).                                        | Medium            |
| **GRID_DELETE_01**| Grid is loaded with records.                                      | 1. Click the 'Delete' button on a specific row. <br> 2. Confirm the action in the SweetAlert dialog.                                                               | A confirmation dialog appears. After confirmation, a success message is shown. The grid refreshes, and the deleted row is no longer visible.                                       | High              |
| **GRID_DELETE_02**| Grid is loaded with records.                                      | 1. Click the 'Delete' button on a specific row. <br> 2. Cancel the action in the SweetAlert dialog (click 'Cancel' or equivalent).                                  | The confirmation dialog appears. After cancellation, no server action occurs. The grid remains unchanged. No success/error message is shown.                                        | Medium            |
| **GRID_EDIT_01**  | Grid is loaded with records.                                      | 1. Click the 'Edit' button on a specific row.                                                                                                                     | The Requestor Form (`#form1`) is populated with the data corresponding to the selected row. (See FORM_EDIT_01 for details).                                                            | High              |
| **GRID_REFRESH_01**| Grid is loaded. A new requestor is added via the form.         | 1. Complete the steps in FORM_ADD_01.                                                                                                                             | After the success notification and form clear, the grid automatically refreshes to display the newly added requestor without manual intervention.                               | High              |
| **GRID_EXPORT_01**| Grid is loaded with records. Export to Excel is enabled.        | 1. Click the 'Export to Excel' button provided by the Kendo Grid.                                                                                                   | An Excel file (.xlsx) download is initiated. The file contains the data currently displayed in the grid (respecting filters, if applied).                                        | Medium            |

---

## 4. Testing Strategy and Requirements

### Testing Types

A comprehensive testing strategy for Project 1365 will include the following types:

1.  **Functional Testing:** Verify all CRUD operations (Add, Edit, Delete, View) for requestors work as expected according to defined behaviors and acceptance criteria. Test form submissions, data binding, and interactions between the form and the grid.
2.  **UI/UX Testing:** Ensure the user interface is intuitive, elements are correctly aligned, and the Kendo Grid and form controls behave as expected across supported browsers (specify target browsers). Verify dropdown population, button states, and grid responsiveness.
3.  **Validation Testing:**
    *   **Client-Side:** Test Parsley.js rules (required fields, email format) exhaustively using valid, invalid, and boundary inputs.
    *   **Server-Side:** Test the duplicate requestor check logic by attempting to create/update records that violate uniqueness constraints (based on Company, Names, Email as defined in `SP_formdataPRIDDispatcherMaster`).
4.  **Integration Testing:** Verify the interaction between different components:
    *   Client-Side JS <=> Server-Side API (WebMethods via AJAX).
    *   Server-Side API <=> Database Stored Procedure (`SP_formdataPRIDDispatcherMaster`).
    *   Form actions <=> Grid updates.
    *   Company Lookup (`GetCompany`) <=> Form Dropdown (`#ddlCompany`).
5.  **Database Testing:** Verify data integrity. Check that data is correctly inserted, updated (including `FlagActive=0` for deletes), and retrieved. Validate data types and constraints directly in the database if necessary, especially after complex operations or suspected issues. Ensure the audit log (`prcAuditProcess_V3`) is triggered correctly (if requirements specify auditing).
6.  **Negative Testing:** Test how the application handles invalid inputs, unexpected user actions, and potential error conditions (e.g., trying to edit/delete a non-existent record, network interruptions during AJAX calls).
7.  **Performance Testing (Basic):** Measure response times for critical actions like grid loading, saving/updating records, and applying filters/sorts, especially with a larger dataset (e.g., 1000+ requestors). Ensure times remain within acceptable limits (e.g., < 3-5 seconds for most operations).
8.  **Security Testing (Basic):** Check for common vulnerabilities like Cross-Site Scripting (XSS) by entering script tags into input fields. Verify that server-side validation prevents bypassing client-side checks. Ensure only intended operations are possible (e.g., cannot delete arbitrary records by manipulating IDs).
9.  **Regression Testing:** After any bug fixes or feature enhancements, re-run a subset of test cases (especially high-priority ones) to ensure no existing functionality has been broken.

### Business Requirements Validation

Testing must validate the core business requirement: efficiently and accurately managing requestor contact information linked to customers/companies.

*   **Requirement:** Maintain a central list of requestors.
    *   **Validation:** Test grid loading, display, sorting, filtering, paging.
*   **Requirement:** Add new requestors with associated company, names, and email.
    *   **Validation:** Test the 'Add New Requestor' behavior, including all validation rules.
*   **Requirement:** Modify existing requestor details.
    *   **Validation:** Test the 'Edit Existing Requestor' behavior, including data loading into the form and successful updates.
*   **Requirement:** Remove obsolete requestors from active view.
    *   **Validation:** Test the 'Delete Requestor' behavior, ensuring confirmation and soft-delete (`FlagActive=0`).
*   **Requirement:** Ensure data accuracy and prevent duplicates.
    *   **Validation:** Test client-side (format, required) and server-side (duplicate checks) validation rules.
*   **Requirement:** Associate requestors with predefined customers/companies.
    *   **Validation:** Test the population and selection functionality of the `#ddlCompany` dropdown.
*   **Requirement:** Provide a user-friendly interface for these tasks.
    *   **Validation:** Assessed through UI/UX testing, focusing on the form and grid interactions.

### Risk-Based Prioritization

Testing efforts will be prioritized based on risk and impact:

1.  **High Priority:**
    *   Core CRUD Functionality (Add, Edit, Delete, View).
    *   Client-Side and Server-Side Validation (Data Integrity).
    *   Grid Loading and Refreshing (Core Data Visibility).
    *   Company Dropdown Population and Selection (Critical Association).
2.  **Medium Priority:**
    *   Grid Sorting, Filtering, Paging (Usability Features).
    *   Form 'Clear' Functionality.
    *   Confirmation Dialogs (e.g., Delete).
    *   Error Handling and Messaging (User Feedback).
    *   Basic Performance (Responsiveness).
3.  **Low Priority:**
    *   Grid 'Export to Excel' (Auxiliary Feature).
    *   Advanced UI/UX details (minor cosmetic issues).
    *   Edge case scenarios with very low probability of occurrence.

### Special Considerations

*   **Dependencies:** Testing requires access to a properly configured database instance with the `SP_formdataPRIDDispatcherMaster` stored procedure and relevant tables (`FormDataPRIDDispatcherMaster`, `FormDataPRIDCableCompanyCustomer`). Ensure test data reflects realistic scenarios, including potential duplicates and various company associations.
*   **Kendo UI Grid:** Familiarity with Kendo UI Grid behavior is beneficial for testing its features (sorting, filtering, paging, export) effectively. Test potential issues related to Kendo UI data binding or AJAX handling.
*   **Parsley.js:** Understand the specific validation rules configured for Parsley to test them thoroughly. Check for inconsistencies between client-side and server-side validation logic.
*   **AJAX Communication:** Use browser developer tools (Network tab) to monitor AJAX requests and responses during testing, helping diagnose issues related to client-server communication. Check for correct parameters being sent and expected JSON/status codes being returned.
*   **State Management:** Pay attention to the state managed by `#recordId` and the 'Save'/'Update' button text, ensuring it correctly reflects whether the form is in 'Add' or 'Edit' mode.

---

## 5. Error Handling and Edge Cases

This section catalogs potential error conditions and expected system behaviors.

### Client-Side Validation Errors (Parsley.js)

*   **Condition:** User clicks 'Save'/'Update' with one or more required fields empty, or the email format is invalid.
*   **Reproduction:** Leave a required field blank or enter malformed email (e.g., "test@", "test.com") and click 'Save'.
*   **Expected Behavior:**
    *   Parsley.js intercepts the submission *before* the AJAX call.
    *   Visual cues (e.g., red borders, icons) appear next to invalid fields.
    *   Error messages specific to the violation (e.g., "This value is required.", "This value should be a valid email.") are displayed near the fields.
    *   The AJAX call to the `insert` WebMethod is **not** made.
*   **Recovery:** User must correct the invalid input according to the error messages. Validation errors should disappear dynamically as fields become valid (if configured) or upon the next save attempt.
*   **Verification:** Check that error messages are clear, correctly indicate the problematic field(s), and that the form cannot be submitted until all client-side validation rules pass.

### Server-Side Duplicate Entry

*   **Condition:** User attempts to Save (Insert or Update) a requestor record that violates the uniqueness constraint defined in `SP_formdataPRIDDispatcherMaster` (likely a combination of Company, First Name, Last Name, Email).
*   **Reproduction:**
    *   Add a requestor (e.g., CompA, John, Doe, john.doe@email.com).
    *   Attempt to add the *exact same* requestor again.
    *   OR: Edit an existing different requestor and change their details to match the first one.
*   **Expected Behavior:**
    *   Client-side validation passes.
    *   AJAX call to the `insert` WebMethod is made.
    *   The `DataOperations` method calls `SP_formdataPRIDDispatcherMaster` with 'Insert' or 'Update'.
    *   The Stored Procedure's `IF NOT EXISTS(...)` check fails.
    *   The SP returns a specific status indicating a duplicate (e.g., the string "Duplicate").
    *   The `insert` WebMethod receives this status and returns an appropriate error message (e.g., "Duplicate Requestor found.") to the client via the AJAX response.
    *   The client-side JavaScript receives the error message and displays it to the user using a notification (e.g., `showErrorToasterNotification`).
    *   The form fields remain populated with the attempted data.
    *   The grid is **not** updated or refreshed with the duplicate data.
*   **Recovery:** User must modify the conflicting fields (e.g., change the name, email, or company) to ensure uniqueness and attempt to save again.
*   **Verification:** Confirm that the specific 'Duplicate' error message is shown, the database state remains unchanged (no duplicate inserted/updated), and the form retains the data for correction.

### Data Fetching/Loading Errors (AJAX/Server)

*   **Condition:** An error occurs during an AJAX call to fetch data (e.g., `LoadGrid`, `LoadCompany`, `Edit` record fetch). This could be due to network issues, server errors (500 Internal Server Error), invalid endpoint, or database unavailability.
*   **Reproduction:** Simulate network failure (using browser dev tools), introduce a bug in a WebMethod, stop the database service, or stop the web server application pool.
*   **Expected Behavior:**
    *   The AJAX call fails (e.g., enters the `error` callback in jQuery AJAX).
    *   A user-friendly error notification should be displayed (e.g., "Error loading companies. Please try again later." or "Failed to retrieve requestor list."). Specific technical details should ideally be logged server-side but not exposed directly to the end-user.
    *   The target UI element (grid, dropdown) should ideally indicate a failed state (e.g., grid shows an error message instead of data, dropdown remains empty or shows an error item).
    *   The application should remain functional where possible (e.g., if loading companies fails, maybe the rest of the form still works, although saving might be blocked).
*   **Recovery:** User might need to refresh the page or try the action again later. If the error persists, it indicates a backend issue requiring investigation.
*   **Verification:** Check that AJAX errors are caught, appropriate user feedback is provided, and the application doesn't crash or enter an unusable state. Monitor browser console and server logs for detailed error information.

### Record Not Found (Edit/Delete)

*   **Condition:** User attempts to Edit or Delete a record that no longer exists in the database (e.g., deleted by another user between grid load and button click).
*   **Reproduction:**
    *   Load the grid with two browser windows/sessions.
    *   In session 1, delete Requestor X.
    *   In session 2 (without refreshing the grid), attempt to Edit or Delete Requestor X.
*   **Expected Behavior:**
    *   The `Edit(recordid)` or `Delete(recordid)` JS function calls the corresponding WebMethod (`Edit` or `Delete`) via AJAX.
    *   The WebMethod calls `DataOperations`, which calls `SP_formdataPRIDDispatcherMaster` with 'Edit' or 'Delete' and the `recordid`.
    *   The SP attempts to find the record by ID but fails (returns empty result set for 'Edit', or affects 0 rows for 'Delete').
    *   The `DataOperations` method and subsequently the WebMethod should detect that the record was not found (e.g., empty DataSet, row count 0).
    *   The WebMethod returns an appropriate status/message to the client (e.g., "Record not found.", or simply returns null/empty for Edit).
    *   The client-side JS (in the AJAX success/complete callback) handles this response:
        *   For Edit: Display an error notification ("Record not found, it may have been deleted.") and do not populate the form.
        *   For Delete: Display an error notification ("Record not found or already deleted."). Refresh the grid to remove the stale row.
*   **Recovery:** User action is typically just acknowledging the message. The grid refresh (especially after delete attempt) corrects the UI state.
*   **Verification:** Ensure appropriate "Not Found" messages are shown, the form is not populated on Edit failure, and the grid is refreshed correctly after a failed Delete attempt on a non-existent record.

### Database Errors

*   **Condition:** The database server encounters an issue while executing `SP_formdataPRIDDispatcherMaster` (e.g., connection lost mid-transaction, constraint violation not caught by specific checks, deadlock, permission issue, log file full).
*   **Reproduction:** Difficult to reproduce consistently. May require simulating DB load, specific data conflicts, or manipulating DB state/permissions.
*   **Expected Behavior:**
    *   The error occurs during the execution of the Stored Procedure.
    *   An exception is thrown within the C# `DataOperations` method (or deeper in ADO.NET).
    *   This exception should be caught by error handling logic in the C# code (ideally logging the detailed SQL error).
    *   The WebMethod should return a generic server error status/message to the client (e.g., "An unexpected error occurred. Please contact support."). Specific SQL errors should NOT be sent to the client for security reasons.
    *   The client-side AJAX call receives the error status.
    *   An appropriate error notification is displayed to the user.
    *   The application should attempt to remain in a stable state. The grid or form might not update as expected.
*   **Recovery:** Usually requires administrator intervention to resolve the underlying database issue. The user may need to retry the operation later.
*   **Verification:** Check that database exceptions are caught server-side, detailed errors are logged (not exposed to UI), a generic error message is shown to the user, and the application does not expose sensitive information or crash.