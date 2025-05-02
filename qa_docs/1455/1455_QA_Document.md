# 1455 QA Document

## Table of Contents
1.  [Application Overview](#1-application-overview)
    *   [Purpose and Functionality](#purpose-and-functionality)
    *   [Technology Stack](#technology-stack)
2.  [Component Action Mapping Documentation](#2-component-action-mapping-documentation)
    *   [Job Summary Grid (`grid`)](#job-summary-grid-grid)
    *   [Date Filters (`txtfromdate`, `txttodate`, Buttons, Arrows)](#date-filters-txtfromdate-txttodate-buttons-arrows)
    *   [Dropdown Filters (`ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront`)](#dropdown-filters-ddlstatus-ddloperationarea-ddlcategory-ddlservicetype-ddlclientfront)
    *   [Child Task Items Modal (`#childTaskItems`) / Child Job Grid (`grid2`)](#child-task-items-modal-childtaskitems--child-job-grid-grid2)
    *   [Field Ticket Items Table (`#tblselectDetails`)](#field-ticket-items-table-tblselectdetails)
    *   [Approval Control (Switch/Checkbox)](#approval-control-switchcheckbox)
    *   [Action Menu (Dots)](#action-menu-dots)
    *   [Send Email Modal (`#SendEmaill`)](#send-email-modal-sendemaill)
    *   [Comment Modal (`#commentDialog`)](#comment-modal-commentdialog)
    *   [Deployment Time Modal (`#divDeploymentTimeWindowDialog`)](#deployment-time-modal-divdeploymenttimewindowdialog)
    *   [Push Child Job Modal (`#divPushChildJobWindowDialog`)](#push-child-job-modal-divpushchildjobwindowdialog)
3.  [Acceptance Criteria and Test Cases](#3-acceptance-criteria-and-test-cases)
    *   [Job Summary Grid (`grid`)](#acceptance-criteria-job-summary-grid-grid)
    *   [Date Filters (`txtfromdate`, `txttodate`, Buttons, Arrows)](#acceptance-criteria-date-filters-txtfromdate-txttodate-buttons-arrows)
    *   [Dropdown Filters (`ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront`)](#acceptance-criteria-dropdown-filters-ddlstatus-ddloperationarea-ddlcategory-ddlservicetype-ddlclientfront)
    *   [Child Task Items Modal (`#childTaskItems`) / Child Job Grid (`grid2`)](#acceptance-criteria-child-task-items-modal-childtaskitems--child-job-grid-grid2)
    *   [Field Ticket Items Table (`#tblselectDetails`)](#acceptance-criteria-field-ticket-items-table-tblselectdetails)
    *   [Approval Control (Switch/Checkbox)](#acceptance-criteria-approval-control-switchcheckbox)
    *   [Action Menu (Dots)](#acceptance-criteria-action-menu-dots)
    *   [Send Email Modal (`#SendEmaill`)](#acceptance-criteria-send-email-modal-sendemaill)
    *   [Comment Modal (`#commentDialog`)](#acceptance-criteria-comment-modal-commentdialog)
    *   [Deployment Time Modal (`#divDeploymentTimeWindowDialog`)](#acceptance-criteria-deployment-time-modal-divdeploymenttimewindowdialog)
    *   [Push Child Job Modal (`#divPushChildJobWindowDialog`)](#acceptance-criteria-push-child-job-modal-divpushchildjobwindowdialog)
4.  [Testing Strategy and Requirements](#4-testing-strategy-and-requirements)
    *   [Testing Types](#testing-types)
    *   [Key Business Requirements Validation](#key-business-requirements-validation)
    *   [Risk-Based Prioritization](#risk-based-prioritization)
    *   [Special Considerations](#special-considerations)
5.  [Error Handling and Edge Cases](#5-error-handling-and-edge-cases)
    *   [AJAX Communication Failures](#ajax-communication-failures)
    *   [Stored Procedure / Database Errors](#stored-procedure--database-errors)
    *   [Client-Side Validation Errors](#client-side-validation-errors)
    *   [Server-Side Validation / Logic Errors](#server-side-validation--logic-errors)
    *   [Permission Denied Errors](#permission-denied-errors)
    *   [Data Integrity Issues](#data-integrity-issues)

# 1. Application Overview

## Purpose and Functionality
Project "1455" is a web-based application designed for managing job summaries. Its primary purpose is to provide users, likely dispatchers or operations managers, with a centralized interface to view, filter, and manage operational jobs and their associated tasks (child jobs).

Key functionalities include:
*   Displaying a comprehensive list of jobs in a filterable, sortable, and paginated grid (`Job Summary Grid`).
*   Filtering jobs based on date ranges, customer, status, operational area, category, and service type.
*   Viewing detailed information about individual jobs, including child jobs/tasks, within a modal dialog.
*   Performing actions on jobs and child jobs, such as approving/unapproving, generating PDFs, sending email notifications, deleting, editing Field Ticket Items (FTI), managing deployment times, and rescheduling (pushing) tasks.
*   Viewing job comments and managing email communications.
*   Displaying summary totals and statistics based on the current filter criteria.

The application facilitates efficient job tracking, status management, and operational workflow execution.

## Technology Stack
Based on the provided context, the application utilizes the following technologies:
*   **Frontend UI:** HTML, Kendo UI Grid, Bootstrap Select (Dropdowns), JavaScript (including jQuery for AJAX and DOM manipulation).
*   **Backend Logic:** ASP.NET (C#) Code-Behind, ASP.NET WebMethods.
*   **Database:** SQL Server (interacting via Stored Procedures, specifically `SP_FormDataPRIDEJobSummaryReport` and `SP_FormDataOPRSJobSummaryReportUpdateDispatcheTicketParentChild`).
*   **Communication:** AJAX for dynamic client-server interaction without full page reloads.
*   **Other:** Potentially uses SweetAlert for confirmation dialogs.

# 2. Component Action Mapping Documentation

This section details the actions triggered by user interactions with specific components, the resulting effects, and related technical details.

## Job Summary Grid (`grid`)
*Component Abstraction: Abstraction 0 (Job Summary Grid)*
*UI Element: `grid`*

| Trigger/Event                   | Action                                           | Target/Effect                                                                                             | Data Elements                                          | Validation Rules                               | Error Scenarios                                            | Test Priority | Expected Performance             |
| :------------------------------ | :----------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- | :--------------------------------------------- | :--------------------------------------------------------- | :------------ | :------------------------------- |
| Initial Page Load             | Kendo Grid Initialization & Data Load          | Grid (`#grid`) displays the initial set of job summaries based on default filters. Totalizers updated.    | Job Summary Fields (various), Filter Parameters | Default filters applied correctly.             | Data load failure (AJAX error, SP error).                  | High          | Load within 3-5 seconds.         |
| Column Header Click             | Kendo Grid Sort                                  | Grid data is re-sorted based on the clicked column. Sort indicators appear.                                 | Sorted Column Data                             | N/A                                            | Sort operation fails.                                      | Medium        | Sort completes within 1-2 seconds. |
| Pager Control Click           | Kendo Grid Paging                                | Grid displays the requested page of data.                                                                   | Paginated Job Summary Data                     | N/A                                            | Paging fails (AJAX error).                               | High          | Page loads within 1-2 seconds.  |
| Double-Click Grid Row         | `onDataBound` handler -> Initialize `#grid2`     | Opens `#childTaskItems` modal displaying child jobs in `#grid2` for the selected parent job.                | Parent Job ID, Child Job Data                  | N/A                                            | Modal fails to open, Child data load fails.              | High          | Modal opens within 2 seconds.    |
| Click Approve Switch/Checkbox | `SetAllChildApprove` (via `.selectAllCheckbox`)  | Toggles approval status for the parent job (and potentially children) in UI and DB. Grid refreshes.     | Parent Job ID, Approval Status (0/1)           | Checks for child job resource requirements (server-side). | Update fails (AJAX/SP error), Resource validation failure. | High          | Update completes within 2 seconds. |
| Click Action Menu Item        | Various JS functions (`JobSummary_SendEmail`, etc.) | Executes the selected action (PDF, Email, Delete, Comments, etc.) for the parent job. See specific actions. | Parent Job ID, Action Type                     | Permission checks (server-side, e.g., `actionPerform`). | Action fails (AJAX/SP error), Permission denied.         | High          | Action initiates within 1 second. |
| Grid DataBound Event          | `onDataBound`, `bindTotalizerData`             | Restores expanded rows (from localStorage), sets up dbl-click. Updates totalizer section.                 | localStorage keys, Totalizer data              | N/A                                            | localStorage read fails, Totalizer update fails (AJAX/SP). | Medium        | Executes quickly post-load.    |

## Date Filters (`txtfromdate`, `txttodate`, Buttons, Arrows)
*Component Abstraction: Abstraction 4 (UI Controls & Filtering)*
*UI Elements: `txtfromdate`, `txttodate`, `btnPastWeek`, `btnPastMonth`, `btnCalendarMonth`, `btnOperatingMonth`, Previous/Next Arrows*

| Trigger/Event                   | Action                                                       | Target/Effect                                                                                         | Data Elements                                                       | Validation Rules                       | Error Scenarios                                  | Test Priority | Expected Performance       |
| :------------------------------ | :----------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------ | :------------------------------------- | :----------------------------------------------- | :------------ | :----------------------- |
| Change Date in `txtfromdate`    | `submitDate`                                                 | Updates start date filter, calls `setSubmitDates` WebMethod, refreshes `grid`.                            | `txtfromdate` value, other filter values                            | Valid date format.                     | Invalid date entry, AJAX call failure.         | High          | Grid refresh < 3 seconds. |
| Change Date in `txttodate`      | `submitDate`                                                 | Updates end date filter, calls `setSubmitDates` WebMethod, refreshes `grid`.                              | `txttodate` value, other filter values                              | Valid date format, End Date >= Start Date. | Invalid date entry, AJAX call failure.         | High          | Grid refresh < 3 seconds. |
| Click `btnPastWeek`             | `submitDate` (after setting dates)                           | Sets date pickers to last 7 days, calls `setSubmitDates`, refreshes `grid`.                             | Calculated date range, other filter values                          | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |
| Click `btnPastMonth`            | `submitDate` (after setting dates)                           | Sets date pickers to last 30 days, calls `setSubmitDates`, refreshes `grid`.                            | Calculated date range, other filter values                          | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |
| Click `btnCalendarMonth`        | `submitDate` (after setting dates)                           | Sets date pickers to current calendar month, calls `setSubmitDates`, refreshes `grid`.                  | Calculated date range, other filter values                          | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |
| Click `btnOperatingMonth`       | `submitDate` (after setting dates)                           | Sets date pickers to defined operating month (e.g., 20th-19th), calls `setSubmitDates`, refreshes `grid`. | Calculated date range, other filter values                          | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |
| Click Previous Date Arrow       | `setPreviousDate`                                            | Calculates previous range, calls `setPrevDates` WebMethod, updates date pickers, refreshes `grid`.        | Current date range, range type, other filter values                 | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |
| Click Next Date Arrow           | `setNextDate`                                                | Calculates next range, calls `setNextDates` WebMethod, updates date pickers, refreshes `grid`.          | Current date range, range type, other filter values                 | N/A                                    | Date calculation error, AJAX call failure.     | Medium        | Grid refresh < 3 seconds. |

## Dropdown Filters (`ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront`)
*Component Abstraction: Abstraction 4 (UI Controls & Filtering)*
*UI Elements: `ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront` (Bootstrap Select)*

| Trigger/Event             | Action                   | Target/Effect                                                                      | Data Elements                                | Validation Rules | Error Scenarios               | Test Priority | Expected Performance       |
| :------------------------ | :----------------------- | :--------------------------------------------------------------------------------- | :------------------------------------------- | :--------------- | :---------------------------- | :------------ | :----------------------- |
| Change Selection(s) in Dropdown | `submitDate` (likely triggered by change event on Bootstrap Select) | Updates corresponding filter, calls `setSubmitDates` WebMethod, refreshes `grid`. | Selected dropdown value(s), other filter values | N/A              | AJAX call failure.            | High          | Grid refresh < 3 seconds. |
| Initial Page Load       | Server-Side Logic        | Dropdowns are populated with available options (Status, Area, Category, etc.). | Filter option data (from DB via C#)        | N/A              | Failed to load dropdown options. | High          | Populated on page load.  |

## Child Task Items Modal (`#childTaskItems`) / Child Job Grid (`grid2`)
*Component Abstraction: Abstraction 5 (Modal Dialog Management), Abstraction 0 (Kendo UI Grid)*
*UI Elements: `#childTaskItems`, `grid2`*

| Trigger/Event                       | Action                                               | Target/Effect                                                                                                  | Data Elements                                                       | Validation Rules                               | Error Scenarios                                      | Test Priority | Expected Performance           |
| :---------------------------------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------ | :--------------------------------------------- | :------------------------------------------------- | :------------ | :----------------------------- |
| Double-Click Parent Row (`#grid`) | `onDataBound` handler                                | Shows modal (`#childTaskItems`), initializes and loads data into child grid (`#grid2`) for the parent job.     | Parent Job ID                                                       | N/A                                            | Modal fails to open, Child grid data load fails.     | High          | Modal + Grid load < 3 seconds. |
| Click Approve Switch/Checkbox     | `setChildAprove` (via `.chkchild`)                   | Toggles approval status for the child job in UI and DB. Refreshes child grid (`grid2`).                        | Child Job ID, Child Record ID, Approval Status (0/1)                | Resource requirement checks (server-side, implied). | Update fails (AJAX/SP error), Validation failure. | High          | Update completes < 2 seconds. |
| Expand Child Row                    | `detailInit1`                                        | Fetches Field Ticket Item details via AJAX (`SelectFieldTicketItemDetails`), populates `#tblselectDetails`. | Child Job ID                                                        | N/A                                            | FTI data load fails (AJAX/SP error).               | High          | FTI table loads < 2 seconds.   |
| Click Action Menu Item            | Various JS functions (`.pdfChild`, `#btnDeleteChild`, etc.) | Executes the selected action (PDF, Edit, Delete, Photos, Copy, Push, etc.) for the child job. See specific actions. | Child Job ID/Record ID, Action Type                                 | Permission checks, Status checks (e.g., 'New' for Push). | Action fails (AJAX/SP error), Permission denied. | High          | Action initiates < 1 second.   |
| Close Modal Button Click          | Bootstrap Modal JS                                   | Hides the modal (`#childTaskItems`).                                                                         | N/A                                                                 | N/A                                            | Modal fails to close.                            | Medium        | Modal closes instantly.        |

## Field Ticket Items Table (`#tblselectDetails`)
*Component Abstraction: Implicit within Child Job Details*
*UI Element: `#tblselectDetails` (inside `#grid2` detail template)*

| Trigger/Event               | Action                              | Target/Effect                                                                                  | Data Elements                                      | Validation Rules                    | Error Scenarios                     | Test Priority | Expected Performance     |
| :-------------------------- | :---------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------- | :---------------------------------- | :---------------------------------- | :------------ | :----------------------- |
| Expand Child Row in `#grid2`  | `detailInit1`                       | Table is populated with FTI data fetched via AJAX (`SelectFieldTicketItemDetails`).              | FTI Data (Item, SKU, Price, Qty)                 | N/A                                 | AJAX/SP error fetching data.        | High          | Load < 2 seconds.        |
| Modify Price Input          | User Input                          | Price value changes in the input field.                                                          | Item Price                                         | Numeric format (implied).           | N/A                                 | High          | Instantaneous.           |
| Modify Quantity Input       | User Input                          | Quantity value changes in the input field.                                                       | Item Quantity                                      | Numeric format (implied).           | N/A                                 | High          | Instantaneous.           |
| Click Save Button (`.btnSave`) | JS click handler -> `UpdateFieldTicketItemDetails` WebMethod | Saves all modified Price/Quantity values for all FTIs in the table via AJAX. Refreshes `#grid2`. | List of FTI updates (ID, Price, Qty, Total)    | Numeric validation (`checkTotal`).  | Validation fails, AJAX/SP error.    | High          | Save & Refresh < 3 seconds. |
| Click Reconfigure Button    | (Not specified in detail)           | Likely triggers a process to reset or recalculate FTI based on rules.                            | Child Job ID/FTI Data                              | (Depends on implementation)         | (Depends on implementation)         | Medium        | (Depends on implementation) |
| Click Delete Item Button    | (Not specified in detail)           | Deletes the specific FTI row via AJAX/SP call.                                                   | FTI ID                                             | Confirmation prompt?                | Delete fails (AJAX/SP error).     | Medium        | Delete < 2 seconds.      |
| Click Apply Quoted Qty Button | (Not specified in detail)           | Applies predefined quoted quantities to the FTIs via AJAX/SP call (`applyQuotedQuantities` param?). | Child Job ID/FTI Data                              | Quote must exist and be applicable. | Apply fails (AJAX/SP error).      | Medium        | Apply < 2 seconds.       |

## Approval Control (Switch/Checkbox)
*Component Abstraction: Abstraction 6 (Job Status & Actions)*
*UI Element: Approval Status Switch/Checkbox (in `#grid` and `#grid2`)*

| Trigger/Event                        | Action                               | Target/Effect                                                                       | Data Elements                               | Validation Rules                   | Error Scenarios                      | Test Priority | Expected Performance     |
| :----------------------------------- | :----------------------------------- | :---------------------------------------------------------------------------------- | :------------------------------------------ | :--------------------------------- | :----------------------------------- | :------------ | :----------------------- |
| Click Parent Approval Control      | `.selectAllCheckbox` -> `SetAllChildApprove` | Calls `UpdateAproveStatusOfAllChild` WebMethod. Updates DB, refreshes `#grid`.       | Parent Job ID, Approve Flag (0/1)         | Server-side resource checks for children. | Update fails (AJAX/SP error).        | High          | Update & Refresh < 3 seconds. |
| Click Child Approval Control       | `.chkchild` -> `setChildAprove`          | Calls `UpdateAproveStatusOfChild` WebMethod. Updates DB, refreshes `#grid2`.          | Child Job ID, Record ID, Approve Flag (0/1) | Server-side resource checks.       | Update fails (AJAX/SP error).        | High          | Update & Refresh < 2 seconds. |
| Grid Row Data Binding              | Kendo Grid rendering                 | Control visually reflects the current approval status fetched from the data source. | Approval Status (boolean/integer)         | N/A                                | Data source value incorrect.         | High          | Renders with grid row.   |

## Action Menu (Dots)
*Component Abstraction: Abstraction 6 (Job Status & Actions)*
*UI Element: Action Menu (Dots) (Dropdown Menu in `#grid` and `#grid2`)*

| Trigger/Event             | Action                                      | Target/Effect                                                                                                | Data Elements                      | Validation Rules                                      | Error Scenarios                                     | Test Priority | Expected Performance   |
| :------------------------ | :------------------------------------------ | :----------------------------------------------------------------------------------------------------------- | :--------------------------------- | :---------------------------------------------------- | :-------------------------------------------------- | :------------ | :--------------------- |
| Click Dots Icon           | UI Event Handler                          | Displays the dropdown menu with relevant actions based on job status and permissions.                        | Job Status, User Permissions       | N/A                                                   | Menu fails to display.                              | High          | Displays instantly.    |
| Click 'PDF' Item          | `.pdfParent` / `.pdfChild` JS handlers      | Opens new window/iframe pointing to `1523.aspx` to generate and stream PDF. May call `SavepdfParent` first. | Job ID, Report Type (`formId`)   | Job must exist. Permission to view report.            | PDF generation fails, `SavepdfParent` fails.        | High          | PDF starts generation < 2s. |
| Click 'Edit' Item         | (Not specified in detail, likely opens modal) | Opens an editing interface (potentially a modal) for the job/child job.                                    | Job/Child Job ID                   | Permission to edit. Job status allows editing.        | Edit interface fails to open.                       | High          | Edit UI opens < 2s.    |
| Click 'Email' Item (Parent) | `JobSummary_SendEmail`                        | Opens the `#SendEmaill` modal to compose and send an email for the parent job.                               | Parent Job ID                      | Job must be approved (implied). Permission to email.  | Modal fails to open, Recipient fetch fails.       | High          | Modal opens < 2s.      |
| Click 'Delete' Item (Parent)| `deleteParent`                                | Shows confirmation, calls `actionPerform` WebMethod (action='DELETEPARENT'). Refreshes `#grid`.            | Parent Job ID                      | Permission to delete.                               | Delete fails (AJAX/SP error), Permission denied.    | High          | Delete & Refresh < 3s. |
| Click 'Delete' Item (Child) | `#btnDeleteChild` -> `actionPerform`?         | Shows confirmation, calls `actionPerform` WebMethod (action='DELETECHILD'). Refreshes `#grid2`.            | Child Job Record ID              | Permission to delete.                               | Delete fails (AJAX/SP error), Permission denied.    | High          | Delete & Refresh < 3s. |
| Click 'Add Photos' Item   | (Not specified in detail)                   | Opens an interface (likely modal) to upload/manage photos associated with the job/child job.               | Job/Child Job ID                   | Permission to add photos.                           | Photo interface fails to open.                      | Medium        | UI opens < 2s.         |
| Click 'Copy' Item (Child)   | `CopyChildJob` -> `CopyChild` WebMethod     | Calls `CopyChild` WebMethod (via SP `...UpdateDispatcheTicketParentChild` action='COPYCHILD'). Refreshes `#grid2`. | Child Job Record ID              | Permission to copy.                                 | Copy fails (AJAX/SP error).                         | Medium        | Copy & Refresh < 3s.   |
| Click 'Push' Item (Child)   | (Not specified) -> Opens `#divPushChildJobWindowDialog` | Opens the Push Child Job modal for rescheduling.                                                           | Child Job ID, Status ('New'?)      | Job status must be 'New'. Permission to push.         | Modal fails to open.                                | Medium        | Modal opens < 2s.      |
| Click 'Pause' Item        | (Not specified) -> `actionPerform`?           | Calls `actionPerform` WebMethod (action='PAUSE'?). Updates status, refreshes grid.                         | Job/Child Job ID                   | Job must be in a pausable state. Permission.        | Pause fails (AJAX/SP error).                        | Medium        | Update & Refresh < 3s. |
| Click 'Resume' Item       | (Not specified) -> `actionPerform`?           | Calls `actionPerform` WebMethod (action='RESUME'?). Updates status, refreshes grid.                        | Job/Child Job ID                   | Job must be paused. Permission.                     | Resume fails (AJAX/SP error).                       | Medium        | Update & Refresh < 3s. |
| Click 'Deployment Time'   | (Not specified) -> Opens `#divDeploymentTimeWindowDialog` | Opens the Deployment Time modal.                                                                           | Child Job ID                       | Permission to set deployment time.                  | Modal fails to open.                                | Medium        | Modal opens < 2s.      |
| Click 'Activate' Item     | (Not specified) -> `actionPerform`?           | Calls `actionPerform` WebMethod (action='ACTIVATE'?). Updates status, refreshes grid.                      | Job/Child Job ID                   | Job must be in an activatable state. Permission.    | Activate fails (AJAX/SP error).                     | Medium        | Update & Refresh < 3s. |
| Click 'Recall' Item       | (Not specified) -> `actionPerform`?           | Calls `actionPerform` WebMethod (action='RECALL'?). Updates status, refreshes grid.                       | Job/Child Job ID                   | Job must be in a recallable state. Permission.      | Recall fails (AJAX/SP error).                       | Medium        | Update & Refresh < 3s. |

## Send Email Modal (`#SendEmaill`)
*Component Abstraction: Abstraction 5 (Modal Dialog Management)*
*UI Element: `SendEmaill`*

| Trigger/Event                      | Action                                       | Target/Effect                                                                                             | Data Elements                                          | Validation Rules                                  | Error Scenarios                                           | Test Priority | Expected Performance     |
| :--------------------------------- | :------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- | :------------------------------------------------ | :-------------------------------------------------------- | :------------ | :----------------------- |
| Click Email Icon (Parent Grid)   | `JobSummary_SendEmail`                       | Fetches recipients via AJAX (`GetEmailDetails`/`GetSendEmailDetails`), populates and shows the modal.     | Parent Job ID, IsEmailSend flag                        | N/A                                               | AJAX error fetching recipients, Modal fails to show.      | High          | Modal populated < 2s.    |
| Input Manual Email Address       | User Input                                   | Adds email to recipient list in UI.                                                                         | Email address                                          | Valid email format (client-side JS likely).       | Invalid format entered.                                   | Medium        | Instantaneous.           |
| Input Custom Message             | User Input                                   | Updates the custom message text area.                                                                       | Custom message text                                    | Character limits? Escaping handled by `processEscapeCharacters`. | N/A                                                       | Medium        | Instantaneous.           |
| Click Send Button (`#btnSendEmail`) | `sendEmsils`                                 | Gathers emails/message, calls `SendEmailDetails` WebMethod via AJAX. Closes modal, refreshes parent grid. | Selected/Manual Emails, Custom Message, Parent Job ID | At least one recipient required? Message required? | AJAX/SP error sending email, Email queueing fails.      | High          | Send & Close < 3 seconds. |
| Click Close/Cancel Button        | Bootstrap Modal JS                           | Hides the modal (`#SendEmaill`).                                                                            | N/A                                                    | N/A                                               | Modal fails to close.                                   | Medium        | Modal closes instantly.  |

## Comment Modal (`#commentDialog`)
*Component Abstraction: Abstraction 5 (Modal Dialog Management)*
*UI Element: `commentDialog`*

| Trigger/Event                 | Action                                       | Target/Effect                                                                       | Data Elements   | Validation Rules | Error Scenarios                                       | Test Priority | Expected Performance   |
| :---------------------------- | :------------------------------------------- | :---------------------------------------------------------------------------------- | :-------------- | :--------------- | :---------------------------------------------------- | :------------ | :--------------------- |
| Click Comment Icon (Parent Grid) | `openCommentBox` -> `openCommentPopup`       | Opens modal (`#commentDialog`), loads `1714.aspx?val=<parent_job_id>` into an iframe. | Parent Job ID | N/A              | Modal fails to show, Iframe fails to load `1714.aspx`. | Medium        | Modal opens < 2s.      |
| Interact within Iframe        | Actions within `1714.aspx`                 | Comments are viewed/added/edited as per `1714.aspx` functionality.                  | Comment Data    | (Defined within `1714.aspx`) | (Defined within `1714.aspx`)                          | Medium        | (Depends on `1714.aspx`) |
| Click Close/Cancel Button     | Bootstrap Modal JS / `openCommentPopup` logic | Hides the modal (`#commentDialog`).                                                   | N/A             | N/A              | Modal fails to close.                               | Medium        | Modal closes instantly. |

## Deployment Time Modal (`#divDeploymentTimeWindowDialog`)
*Component Abstraction: Abstraction 5 (Modal Dialog Management)*
*UI Element: `divDeploymentTimeWindowDialog`*

| Trigger/Event                     | Action                                     | Target/Effect                                                                                              | Data Elements                         | Validation Rules                          | Error Scenarios                      | Test Priority | Expected Performance   |
| :-------------------------------- | :----------------------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------ | :---------------------------------------- | :----------------------------------- | :------------ | :--------------------- |
| Click 'Deployment Time' (Action Menu) | JS handler (not named)                     | Opens the modal (`#divDeploymentTimeWindowDialog`).                                                          | Child Job ID                          | N/A                                       | Modal fails to open.                 | Medium        | Modal opens < 1s.      |
| Select Hour/Minute/AM/PM        | User Selection                             | Updates the time selection controls within the modal.                                                        | Hour, Minute, AM/PM                   | Valid time combinations.                  | N/A                                  | Medium        | Instantaneous.         |
| Click Submit/Save Button          | JS handler -> AJAX call (SP `departureTime`?) | Saves the selected deployment time via AJAX/SP call. Closes modal, potentially refreshes child grid (`#grid2`). | Child Job ID, Selected Time           | Valid time required.                      | AJAX/SP error saving time.         | Medium        | Save & Close < 2s.     |
| Click Close/Cancel Button         | Bootstrap Modal JS                         | Hides the modal (`#divDeploymentTimeWindowDialog`).                                                          | N/A                                   | N/A                                       | Modal fails to close.                | Medium        | Modal closes instantly. |

## Push Child Job Modal (`#divPushChildJobWindowDialog`)
*Component Abstraction: Abstraction 5 (Modal Dialog Management)*
*UI Element: `divPushChildJobWindowDialog`*

| Trigger/Event               | Action                             | Target/Effect                                                                                                        | Data Elements                                     | Validation Rules                              | Error Scenarios                                | Test Priority | Expected Performance   |
| :-------------------------- | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------ | :-------------------------------------------- | :--------------------------------------------- | :------------ | :--------------------- |
| Click 'Push' (Action Menu)  | JS handler (not named)             | Opens the modal (`#divPushChildJobWindowDialog`).                                                                      | Child Job ID                                      | Child Job status must be 'New'.             | Modal fails to open, Status check fails.       | Medium        | Modal opens < 1s.      |
| Change Start Date/Time      | User Input                         | Updates date/time pickers in the modal. May trigger resource conflict check.                                         | New Start Date, New Start Time                  | Valid date/time format.                     | Resource conflict detected and displayed.    | Medium        | Instantaneous/Check < 1s. |
| Check 'Copy Resources'      | User Input                         | Toggles the flag to copy resources to the rescheduled job.                                                             | Copy Resources Flag                               | N/A                                           | N/A                                            | Medium        | Instantaneous.         |
| Click Submit/Push Button    | JS handler -> AJAX call (SP `type`?) | Reschedules the child job (updates start date/time, potentially copies resources) via AJAX/SP. Closes modal, refreshes `#grid2`. | Child Job ID, New Date/Time, Copy Resources Flag | Valid date/time required. No blocking conflicts? | AJAX/SP error rescheduling. Cannot resolve conflict. | Medium        | Push & Close < 3s.     |
| Click Close/Cancel Button   | Bootstrap Modal JS                 | Hides the modal (`#divPushChildJobWindowDialog`).                                                                      | N/A                                               | N/A                                           | Modal fails to close.                          | Medium        | Modal closes instantly. |

# 3. Acceptance Criteria and Test Cases

## Acceptance Criteria: Job Summary Grid (`grid`)
*   The grid correctly displays job summary data retrieved from the backend based on applied filters.
*   Data is accurately presented in the defined columns.
*   Pagination controls allow navigation through large datasets.
*   Column sorting functions correctly for all sortable columns (ascending/descending).
*   Double-clicking a row successfully opens the Child Task Items modal (`#childTaskItems`) for that parent job.
*   The parent job approval switch accurately reflects and updates the job's approval status.
*   The action menu (dots) appears on hover/click and contains the correct actions based on job status and user permissions.
*   The grid refreshes automatically when filters are changed.
*   Expanded rows (if any) are maintained or correctly restored after data refreshes (`onDataBound` behavior).
*   The grid displays a user-friendly message when no data matches the filter criteria.
*   The grid handles data loading states gracefully (e.g., showing a loading indicator).

## Test Cases: Job Summary Grid (`grid`)
| Test ID        | Preconditions                                         | Steps to Execute                                                                                                                                                                | Expected Final Result                                                                                                                               | Severity/Priority |
| :------------- | :---------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| GRID_LOAD_001  | User has permission to view the page. Default filters set. | 1. Navigate to the page containing the Job Summary Grid.                                                                                                                        | The grid (`#grid`) loads and displays job data matching default filters. Pagination and totalizers are visible. Loading indicator shown and hidden.       | High              |
| GRID_SORT_001  | Grid is loaded with multiple rows of data.            | 1. Click the header of a sortable column (e.g., 'Job ID'). <br> 2. Click the same header again. <br> 3. Click the header of a different sortable column.                           | 1. Grid data sorts ascending by Job ID. Sort indicator appears. <br> 2. Grid data sorts descending by Job ID. <br> 3. Grid data sorts by the new column. | Medium            |
| GRID_PAGE_001  | Grid is loaded with more rows than the page size.     | 1. Click the 'Next' page button. <br> 2. Click a specific page number button. <br> 3. Click the 'Previous' page button. <br> 4. Click the 'Last' page button. <br> 5. Click the 'First' page button. | Grid displays the correct subset of data for each page navigation action. Pager reflects the current page.                                         | High              |
| GRID_DBLCLK_001 | Grid is loaded with data, including a job with child tasks. | 1. Double-click a row in the grid.                                                                                                                                              | The `#childTaskItems` modal appears, displaying the `#grid2` with child tasks for the double-clicked parent job.                                        | High              |
| GRID_NODATA_001 | Filters are set such that no jobs match the criteria. | 1. Apply filter combinations (dates, dropdowns) guaranteed to return no results. <br> 2. Observe the grid area.                                                                      | The grid displays a message indicating "No data found" or similar. Pagination might be hidden or disabled.                                       | Medium            |
| GRID_REFRESH_001| Grid is loaded.                                       | 1. Change a filter value (e.g., select a different customer).                                                                                                                 | The grid shows a loading indicator briefly and then refreshes, displaying data matching the new filter criteria.                                  | High              |

## Acceptance Criteria: Date Filters (`txtfromdate`, `txttodate`, Buttons, Arrows)
*   Date pickers (`txtfromdate`, `txttodate`) allow valid date selection.
*   Changing a date triggers a grid refresh (`submitDate` -> `setSubmitDates` -> grid read).
*   Date range buttons (`btnPastWeek`, `btnPastMonth`, etc.) correctly set the `txtfromdate` and `txttodate` values and trigger a grid refresh.
*   Previous/Next date arrows (`setPreviousDate`, `setNextDate`) correctly adjust the date range based on the current selection/button pressed and trigger a grid refresh.
*   Invalid date inputs are handled gracefully (e.g., prevented or ignored).
*   The server-side session/state correctly reflects the selected date filters (`setSubmitDates`, `setNextDates`, `setPrevDates`).

## Test Cases: Date Filters (`txtfromdate`, `txttodate`, Buttons, Arrows)
| Test ID         | Preconditions                     | Steps to Execute                                                                                                                                            | Expected Final Result                                                                                                                                                                                             | Severity/Priority |
| :-------------- | :-------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DATE_PICK_001   | Grid is loaded.                   | 1. Click `txtfromdate` and select a valid date. <br> 2. Click `txttodate` and select a valid date after the start date.                                        | 1. Grid refreshes with data starting from the selected date. <br> 2. Grid refreshes with data within the selected date range. Server state updated (`setSubmitDates` called).                                      | High              |
| DATE_PICK_002   | Grid is loaded.                   | 1. Attempt to manually type an invalid date (e.g., "abc", "32/01/2023") into `txtfromdate`. <br> 2. Select an end date earlier than the start date.              | 1. Input might be prevented, cleared, or ignored on grid refresh attempt. Grid does not refresh with invalid date. <br> 2. Validation message might appear, or the grid refresh might use the previous valid range. | Medium            |
| DATE_BTN_001    | Grid is loaded.                   | 1. Click `btnPastWeek`. <br> 2. Click `btnPastMonth`. <br> 3. Click `btnCalendarMonth`. <br> 4. Click `btnOperatingMonth`.                                     | Date pickers update to the corresponding range for each button click. Grid refreshes showing data for that range. Server state updated.                                                                            | High              |
| DATE_ARROW_001  | Grid is loaded. `btnPastWeek` active. | 1. Click the 'Next' date arrow. <br> 2. Click the 'Previous' date arrow twice.                                                                            | 1. Date range shifts forward by one week, grid refreshes. Server state updated (`setNextDates`). <br> 2. Date range shifts back by two weeks, grid refreshes. Server state updated (`setPrevDates`).                  | Medium            |

## Acceptance Criteria: Dropdown Filters (`ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront`)
*   Dropdowns are populated with the correct list of options on page load.
*   Dropdowns allow single or multiple selections as configured (Bootstrap Select likely allows multi-select).
*   Changing a selection in any dropdown triggers a grid refresh (`submitDate`).
*   The grid data accurately reflects the combination of all active filters (dropdowns and dates).
*   The server-side session/state correctly reflects the selected dropdown filters (`setSubmitDates`).
*   Clearing selections from a dropdown correctly updates the filter and refreshes the grid.

## Test Cases: Dropdown Filters (`ddlStatus`, `ddlOperationArea`, `ddlCategory`, `ddlServiceType`, `ddlClientFront`)
| Test ID         | Preconditions                         | Steps to Execute                                                                                                                                  | Expected Final Result                                                                                                                             | Severity/Priority |
| :-------------- | :------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------- |
| DDL_LOAD_001    | Page is loading.                      | 1. Observe the filter dropdowns (`ddlStatus`, `ddlClientFront`, etc.) as the page loads.                                                        | All dropdowns are populated with lists of options.                                                                                                  | High              |
| DDL_FILTER_001  | Grid is loaded with default filters. | 1. Select one specific customer from `ddlClientFront`. <br> 2. Select multiple statuses from `ddlStatus`. <br> 3. Clear the selection from `ddlClientFront`. | 1. Grid refreshes showing jobs only for the selected customer (and other active filters). <br> 2. Grid refreshes showing jobs matching any selected status. <br> 3. Grid refreshes showing jobs for all customers. | High              |
| DDL_COMBO_001   | Grid is loaded.                       | 1. Set a specific date range. <br> 2. Select a specific Customer. <br> 3. Select a specific Status. <br> 4. Select a specific Operation Area.             | Grid refreshes after each selection, showing data that matches the *combination* of all currently active filters. Server state reflects all selections. | High              |

## Acceptance Criteria: Child Task Items Modal (`#childTaskItems`) / Child Job Grid (`grid2`)
*   The modal (`#childTaskItems`) opens successfully when a parent row in `#grid` is double-clicked.
*   The child grid (`#grid2`) loads and displays the correct child jobs/tasks associated with the selected parent job.
*   Child grid (`#grid2`) supports pagination, sorting if configured.
*   The child job approval switch accurately reflects and updates the child job's approval status (`setChildAprove` -> `UpdateAproveStatusOfChild`).
*   Expanding a child row correctly displays the Field Ticket Items table (`#tblselectDetails`) via `detailInit1`.
*   The action menu (dots) in `#grid2` appears and contains the correct actions for the child job based on status/permissions.
*   Actions performed within the modal (e.g., approve, delete, edit FTI) correctly update the child job data and refresh `#grid2`.
*   The modal can be closed using standard close mechanisms (X button, Esc key, Cancel button).

## Test Cases: Child Task Items Modal (`#childTaskItems`) / Child Job Grid (`grid2`)
| Test ID         | Preconditions                                             | Steps to Execute                                                                                                                                                     | Expected Final Result                                                                                                                                                               | Severity/Priority |
| :-------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| MODAL_OPEN_001  | Parent grid (`#grid`) loaded with a job having child tasks. | 1. Double-click the parent job row.                                                                                                                                  | `#childTaskItems` modal opens. `#grid2` loads and displays the correct child tasks. Loading indicator shown/hidden.                                                                   | High              |
| MODAL_CLOSE_001 | `#childTaskItems` modal is open.                            | 1. Click the 'X' button in the modal header. <br> 2. Re-open the modal. <br> 3. Press the 'Escape' key. <br> 4. Re-open the modal. <br> 5. Click a 'Cancel' or 'Close' button if available. | Modal closes after each action.                                                                                                                                                   | Medium            |
| CGRID_SORT_001 | `#grid2` loaded with multiple child tasks.                | 1. Click a sortable column header in `#grid2`. <br> 2. Click again.                                                                                                    | Child grid sorts correctly by the column (ascending, then descending).                                                                                                              | Medium            |
| CGRID_EXPAND_001| `#grid2` loaded with a child task having FTIs.              | 1. Click the expand icon (+) for a child task row.                                                                                                                   | The row expands, and the `#tblselectDetails` table is displayed, populated with FTI data fetched via `detailInit1`.                                                                 | High              |
| CGRID_ACTION_001| `#grid2` loaded. A child task action menu is available.     | 1. Click the action menu (dots) for a child task. <br> 2. Select an action (e.g., 'PDF', 'Delete' - follow subsequent prompts).                                        | 1. Action menu appears. <br> 2. The selected action is initiated (PDF generated, Delete confirmation shown, etc.). See specific action test cases.                                      | High              |
| CGRID_REFRESH_001| `#grid2` loaded. Perform an action that updates a child job (e.g., Approve). | 1. Click the approval switch for a child job. <br> 2. Observe `#grid2`.                                                                                   | The approval switch changes state visually. An AJAX call (`setChildAprove`) is made. `#grid2` refreshes (`refreshGridWithoutCollapsing`), showing the updated status. Expanded rows might remain expanded. | High              |

## Acceptance Criteria: Field Ticket Items Table (`#tblselectDetails`)
*   The table (`#tblselectDetails`) correctly loads and displays Field Ticket Item details when a child row in `#grid2` is expanded (`detailInit1`).
*   Price and Quantity fields are editable inputs.
*   Changing Price or Quantity values updates the UI fields.
*   Clicking the Save button (`.btnSave`) triggers the `UpdateFieldTicketItemDetails` WebMethod, successfully saving all changes for all items in the table.
*   Validation (`checkTotal`) prevents saving invalid numeric data.
*   The child grid (`#grid2`) refreshes after a successful save, potentially reflecting updated totals.
*   Other actions (Reconfigure, Delete, Apply Quoted Quantities) function as expected (detailed behavior TBD).

## Test Cases: Field Ticket Items Table (`#tblselectDetails`)
| Test ID         | Preconditions                                                       | Steps to Execute                                                                                                                                                                     | Expected Final Result                                                                                                                                                                 | Severity/Priority |
| :-------------- | :------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------- |
| FTI_LOAD_001    | `#grid2` loaded, child row with FTIs exists.                        | 1. Expand the child job row in `#grid2`.                                                                                                                                             | The `#tblselectDetails` table appears and is populated with the correct FTI data (Item, SKU, Price, Qty) via `detailInit1`.                                                             | High              |
| FTI_EDIT_001    | `#tblselectDetails` is visible and populated.                     | 1. Modify the value in a 'Price' input field. <br> 2. Modify the value in a 'Quantity' input field for the same or different item.                                                      | 1. The Price input field reflects the new value. <br> 2. The Quantity input field reflects the new value.                                                                           | High              |
| FTI_SAVE_001    | `#tblselectDetails` is visible, Price/Quantity values modified.     | 1. Click the 'Save' button (`.btnSave`).                                                                                                                                             | AJAX call to `UpdateFieldTicketItemDetails` is made successfully. Data is saved in the DB (via SP `UpdateFTINew`). `#grid2` refreshes. Success message may appear.                    | High              |
| FTI_SAVE_002    | `#tblselectDetails` is visible.                                     | 1. Enter non-numeric text into a 'Price' input. <br> 2. Enter a negative number into 'Quantity'. <br> 3. Click 'Save'.                                                               | Validation (`checkTotal`) triggers. An error message is displayed. AJAX call to save is *not* made, or if made, returns an error. Invalid data is not saved.                            | Medium            |
| FTI_DELETE_001  | `#tblselectDetails` is visible with multiple items.                 | 1. Click the 'Delete' button for a specific FTI row (if available). <br> 2. Confirm deletion if prompted.                                                                            | The row is removed from the UI. An AJAX/SP call is made to delete the item from the database. `#grid2` might refresh.                                                                 | Medium            |
| FTI_APPLYQ_001  | `#tblselectDetails` visible. Quoted quantities exist for the job. | 1. Click the 'Apply Quoted Quantities' button (if available).                                                                                                                      | Quantity fields update to match the quoted quantities. An AJAX/SP call (using `applyQuotedQuantities` param?) is made. User might need to click 'Save' afterwards, or it might auto-save. | Medium            |

## Acceptance Criteria: Approval Control (Switch/Checkbox)
*   The control's visual state (on/off, checked/unchecked) accurately reflects the approval status from the data source for both parent (`#grid`) and child (`#grid2`) jobs.
*   Clicking the control for a parent job triggers `SetAllChildApprove` -> `UpdateAproveStatusOfAllChild` WebMethod.
*   Clicking the control for a child job triggers `setChildAprove` -> `UpdateAproveStatusOfChild` WebMethod.
*   The database status is correctly updated upon successful completion of the WebMethod call (via the Stored Procedure).
*   The relevant grid (`#grid` or `#grid2`) refreshes to show the updated status.
*   Any server-side validation (e.g., resource requirements for child approval) prevents approval if conditions are not met, and provides appropriate feedback.

## Test Cases: Approval Control (Switch/Checkbox)
| Test ID         | Preconditions                                                               | Steps to Execute                                                                                                                                         | Expected Final Result                                                                                                                                                                                              | Severity/Priority |
| :-------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| APPROVE_P_001   | Parent job row visible in `#grid`, job is unapproved.                       | 1. Click the approval switch for the parent job row to the 'Approved' state.                                                                             | `SetAllChildApprove` called with approve=1. AJAX call to `UpdateAproveStatusOfAllChild` succeeds. DB updated. `#grid` refreshes, showing the parent job as approved. Eligible child jobs may also be approved.      | High              |
| APPROVE_P_002   | Parent job row visible in `#grid`, job is approved.                         | 1. Click the approval switch for the parent job row to the 'Unapproved' state.                                                                           | `SetAllChildApprove` called with approve=0. AJAX call to `UpdateAproveStatusOfAllChild` succeeds. DB updated. `#grid` refreshes, showing the parent job as unapproved. Child jobs might also be unapproved.   | High              |
| APPROVE_C_001   | Child job row visible in `#grid2`, job is unapproved. Resource reqs met.    | 1. Click the approval switch for the child job row to the 'Approved' state.                                                                              | `setChildAprove` called with approve=1. AJAX call to `UpdateAproveStatusOfChild` succeeds. DB updated. `#grid2` refreshes (`refreshGridWithoutCollapsing`), showing the child job as approved.                 | High              |
| APPROVE_C_002   | Child job row visible in `#grid2`, job is approved.                         | 1. Click the approval switch for the child job row to the 'Unapproved' state.                                                                            | `setChildAprove` called with approve=0. AJAX call to `UpdateAproveStatusOfChild` succeeds. DB updated. `#grid2` refreshes, showing the child job as unapproved.                                                | High              |
| APPROVE_C_003   | Child job row visible in `#grid2`, job is unapproved. Resource reqs NOT met. | 1. Click the approval switch for the child job row to the 'Approved' state.                                                                              | `setChildAprove` called. AJAX call to `UpdateAproveStatusOfChild` is made. Server-side validation fails. DB status is NOT updated. An error message is displayed to the user. Switch reverts to 'Unapproved'. | High              |

## Acceptance Criteria: Action Menu (Dots)
*   The menu appears when the dots icon is clicked/hovered in a grid row (`#grid` or `#grid2`).
*   The menu contains the correct list of actions relevant to the specific job (parent/child) and its current status.
*   Actions are enabled/disabled based on user permissions and job status.
*   Clicking a menu item triggers the corresponding JavaScript function (e.g., `JobSummary_SendEmail`, `deleteParent`, `.pdfChild`).
*   Each action behaves as expected (opens modal, generates file, performs update).

## Test Cases: Action Menu (Dots)
| Test ID         | Preconditions                                                                 | Steps to Execute                                                                                                                                                      | Expected Final Result                                                                                                                                                                 | Severity/Priority |
| :-------------- | :---------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------- |
| ACTION_MENU_001 | Grid row visible in `#grid` or `#grid2`.                                        | 1. Click the action menu (dots) icon for the row.                                                                                                                     | The action menu dropdown appears next to the icon.                                                                                                                                      | High              |
| ACTION_MENU_002 | Grid row visible. Job is in a specific status (e.g., Approved). User has perms. | 1. Click the action menu (dots). <br> 2. Verify available actions.                                                                                                    | Menu shows relevant actions for an Approved job (e.g., PDF, Email might be enabled; Delete might be disabled).                                                                        | Medium            |
| ACTION_MENU_003 | Grid row visible. Job is in a different status (e.g., New). User has perms.   | 1. Click the action menu (dots). <br> 2. Verify available actions.                                                                                                    | Menu shows relevant actions for a New job (e.g., Push might be enabled; Email might be disabled).                                                                                   | Medium            |
| ACTION_PDF_001  | Parent grid row visible. User has permissions.                                | 1. Click action menu. <br> 2. Click 'PDF'.                                                                                                                          | `SavepdfParent` (optional) and `.pdfParent` called. New window/iframe opens targeting `1523.aspx`. PDF report for the parent job is generated and displayed/downloaded.                 | High              |
| ACTION_PDF_002  | Child grid row visible in `#grid2`. User has permissions.                     | 1. Click action menu. <br> 2. Click 'PDF'.                                                                                                                          | `.pdfChild` called. New window/iframe opens targeting `1523.aspx`. PDF report for the child job is generated and displayed/downloaded.                                                 | High              |
| ACTION_EMAIL_001| Parent grid row visible, job is Approved. User has permissions.               | 1. Click action menu. <br> 2. Click 'Email'.                                                                                                                        | `JobSummary_SendEmail` called. `#SendEmaill` modal opens, populated with recipient details.                                                                                         | High              |
| ACTION_DEL_P_001| Parent grid row visible. User has delete permissions.                         | 1. Click action menu. <br> 2. Click 'Delete'. <br> 3. Confirm the action in the SweetAlert dialog.                                                                    | `deleteParent` called. Confirmation shown. If confirmed, `actionPerform` WebMethod (DELETEPARENT) called. Job deleted in DB. `#grid` refreshes, job is gone. Success message shown. | High              |
| ACTION_DEL_C_001| Child grid row visible in `#grid2`. User has delete permissions.                | 1. Click action menu. <br> 2. Click 'Delete'. <br> 3. Confirm the action in the dialog.                                                                               | `#btnDeleteChild` handler called. Confirmation shown. If confirmed, `actionPerform` WebMethod (DELETECHILD) called. Child job deleted/inactivated in DB. `#grid2` refreshes.           | High              |
| ACTION_COPY_C_001| Child grid row visible in `#grid2`. User has permissions.                     | 1. Click action menu. <br> 2. Click 'Copy'.                                                                                                                         | `CopyChildJob` JS called. `CopyChild` WebMethod called. SP action 'COPYCHILD' executed. `#grid2` refreshes, showing the duplicated child job.                                         | Medium            |
| ACTION_PUSH_C_001| Child grid row visible in `#grid2`, status is 'New'. User has permissions.    | 1. Click action menu. <br> 2. Click 'Push'.                                                                                                                         | `#divPushChildJobWindowDialog` modal opens.                                                                                                                                         | Medium            |
| ACTION_DEPLOY_C_001| Child grid row visible in `#grid2`. User has permissions.                     | 1. Click action menu. <br> 2. Click 'Deployment Time'.                                                                                                              | `#divDeploymentTimeWindowDialog` modal opens.                                                                                                                                       | Medium            |

## Acceptance Criteria: Send Email Modal (`#SendEmaill`)
*   Modal opens successfully when triggered from the parent grid action menu (`JobSummary_SendEmail`).
*   Recipient list is correctly pre-populated based on job data and whether email was previously sent (`GetEmailDetails`/`GetSendEmailDetails`).
*   Email history (if applicable) is displayed correctly.
*   Users can add manual email recipients. Input validation ensures valid email format.
*   Users can enter a custom message. Special characters are handled (`processEscapeCharacters`).
*   Clicking 'Send' triggers the `sendEmsils` function, which calls the `SendEmailDetails` WebMethod.
*   The email details are logged in the database (via SP `SendEmails`).
*   The email is successfully queued or sent by the backend process (potentially `WebServiceV5BackgroundJob.CreateJob`).
*   Modal closes and parent grid refreshes after sending.

## Test Cases: Send Email Modal (`#SendEmaill`)
| Test ID         | Preconditions                                                                    | Steps to Execute                                                                                                                                                                                        | Expected Final Result                                                                                                                                                                                                 | Severity/Priority |
| :-------------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| EMAIL_OPEN_001  | Parent job approved, visible in `#grid`. Email not sent before. User has perms.  | 1. Click Action Menu -> Email.                                                                                                                                                                          | `JobSummary_SendEmail` calls `GetEmailDetails`. `#SendEmaill` modal opens, pre-populated with default recipients. Email history section might be empty or hidden.                                                | High              |
| EMAIL_OPEN_002  | Parent job approved, visible in `#grid`. Email *was* sent before. User has perms. | 1. Click Action Menu -> Email.                                                                                                                                                                          | `JobSummary_SendEmail` calls `GetSendEmailDetails`. `#SendEmaill` modal opens, pre-populated with previous recipients. Email history section shows previous send details.                                         | High              |
| EMAIL_ADD_001   | `#SendEmaill` modal is open.                                                      | 1. Enter a valid email address in the manual entry field. <br> 2. Add the email to the list. <br> 3. Enter an invalid email address. <br> 4. Attempt to add it.                                         | 1. Email entered. <br> 2. Email appears in the recipient list. <br> 3. Invalid email entered. <br> 4. An error message is shown, or the invalid email is not added to the list.                                 | Medium            |
| EMAIL_SEND_001  | `#SendEmaill` modal is open. Valid recipients selected/entered. Custom message typed. | 1. Click the 'Send' button (`#btnSendEmail`).                                                                                                                                                           | `sendEmsils` called. AJAX call to `SendEmailDetails` succeeds. SP `SendEmails` logs details. Email is queued/sent. Modal closes. Parent grid (`#grid`) refreshes. Success message shown.                             | High              |
| EMAIL_SEND_002  | `#SendEmaill` modal is open. No recipients selected/entered.                      | 1. Click the 'Send' button.                                                                                                                                                                             | Validation might prevent sending. An error message "Please select recipients" or similar should appear. AJAX call is not made.                                                                                 | Medium            |

## Acceptance Criteria: Comment Modal (`#commentDialog`)
*   Modal opens successfully when the comment icon is clicked on a parent grid row (`openCommentBox`).
*   The modal contains an iframe.
*   The iframe successfully loads the `1714.aspx` page, passing the correct parent job ID as a parameter (`val`).
*   Interaction with comments (viewing, adding) is handled correctly within the loaded `1714.aspx` page.
*   The modal can be closed.

## Test Cases: Comment Modal (`#commentDialog`)
| Test ID         | Preconditions                                     | Steps to Execute                                               | Expected Final Result                                                                                                                    | Severity/Priority |
| :-------------- | :------------------------------------------------ | :------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| COMMENT_OPEN_001| Parent grid row visible, has comment icon.        | 1. Click the comment icon for the parent job row.              | `openCommentBox` called. `#commentDialog` modal opens. Iframe inside loads `1714.aspx?val=<parent_job_id>`. Comments are visible inside iframe. | Medium            |
| COMMENT_CLOSE_001| `#commentDialog` modal is open.                 | 1. Click the 'X' button or a 'Close' button in the modal.      | Modal closes successfully.                                                                                                                 | Medium            |
| COMMENT_INTERACT_001 | `#commentDialog` modal open, `1714.aspx` loaded. | 1. Perform actions within the iframe (e.g., add a comment).    | Actions within `1714.aspx` succeed according to its own specifications. (Requires separate testing of 1714.aspx).                           | Medium            |

## Acceptance Criteria: Deployment Time Modal (`#divDeploymentTimeWindowDialog`)
*   Modal opens successfully when 'Deployment Time' action is selected from child action menu.
*   Hour, Minute, and AM/PM selectors are functional.
*   Submitting the modal saves the selected time to the correct child job via an AJAX call/SP update (using `departureTime` parameter?).
*   Modal closes after successful submission.
*   Child grid may refresh to reflect the change.

## Test Cases: Deployment Time Modal (`#divDeploymentTimeWindowDialog`)
| Test ID         | Preconditions                                                       | Steps to Execute                                                                                                      | Expected Final Result                                                                                                                                       | Severity/Priority |
| :-------------- | :------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| DEPLOY_OPEN_001 | Child row visible in `#grid2`. Action menu available.             | 1. Click Action Menu -> Deployment Time.                                                                              | `#divDeploymentTimeWindowDialog` modal opens.                                                                                                             | Medium            |
| DEPLOY_SET_001  | `#divDeploymentTimeWindowDialog` modal is open.                     | 1. Select a specific Hour, Minute, and AM/PM. <br> 2. Click the Submit/Save button.                                    | AJAX call made to update deployment time. SP updates `departureTime`. Modal closes. `#grid2` may refresh showing the updated time. Success message shown. | Medium            |
| DEPLOY_CLOSE_001| `#divDeploymentTimeWindowDialog` modal is open.                     | 1. Click the 'X' or 'Cancel' button.                                                                                  | Modal closes without saving any changes.                                                                                                                  | Medium            |

## Acceptance Criteria: Push Child Job Modal (`#divPushChildJobWindowDialog`)
*   Modal opens successfully when 'Push' action is selected for a 'New' status child job.
*   Date and time pickers allow selection of a new start date/time.
*   'Copy Resources' checkbox functions correctly.
*   Potential resource conflicts for the new date/time are checked and displayed to the user.
*   Submitting the modal successfully reschedules the job via AJAX/SP call (using `type` parameter?), optionally copying resources.
*   Modal closes upon successful submission.
*   Child grid (`#grid2`) refreshes, showing the updated start date/time for the pushed job.
*   Push action is prevented if the job status is not 'New'.

## Test Cases: Push Child Job Modal (`#divPushChildJobWindowDialog`)
| Test ID        | Preconditions                                                                   | Steps to Execute                                                                                                                                                  | Expected Final Result                                                                                                                                                                            | Severity/Priority |
| :------------- | :------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| PUSH_OPEN_001  | Child row visible in `#grid2`, status is 'New'. Action menu available.          | 1. Click Action Menu -> Push.                                                                                                                                     | `#divPushChildJobWindowDialog` modal opens. Date/time pickers are visible.                                                                                                                     | Medium            |
| PUSH_OPEN_002  | Child row visible in `#grid2`, status is *not* 'New'. Action menu available.    | 1. Click Action Menu.                                                                                                                                             | 'Push' action should ideally be disabled or hidden. If clickable, clicking it should result in no action or an informative message, and the modal should not open.                                | Medium            |
| PUSH_SET_001   | `#divPushChildJobWindowDialog` modal is open.                                   | 1. Select a new future date and time. <br> 2. Check the 'Copy Resources' checkbox. <br> 3. Click the Submit/Push button.                                          | Resource conflicts checked (assume none). AJAX/SP call made to reschedule the job and copy resources. Modal closes. `#grid2` refreshes, showing the updated start date/time. Success message shown. | Medium            |
| PUSH_CONFLICT_001| `#divPushChildJobWindowDialog` modal is open. Selected new time has conflicts. | 1. Select a new date and time known to cause resource conflicts. <br> 2. Observe the modal.                                                                       | A message or indicator appears in the modal showing the potential resource conflicts. Submit button might be disabled, or submission might fail with a specific error.                        | Medium            |
| PUSH_CLOSE_001 | `#divPushChildJobWindowDialog` modal is open.                                   | 1. Click the 'X' or 'Cancel' button.                                                                                                                              | Modal closes without rescheduling the job.                                                                                                                                                     | Medium            |

# 4. Testing Strategy and Requirements

## Testing Types
A comprehensive testing strategy for Application 1455 should include:
1.  **Component Testing:** Verify individual UI elements (grids, date pickers, dropdowns, modals) and their client-side JavaScript logic in isolation where feasible.
2.  **Integration Testing:** Focus on the interaction points between components:
    *   Client-Side JS <-> ASP.NET WebMethods (AJAX calls like `submitDate` -> `setSubmitDates`, `setChildAprove` -> `UpdateAproveStatusOfChild`).
    *   ASP.NET WebMethods <-> SQL Stored Procedures (e.g., `UpdateAproveStatusOfChild` calling `SP_FormDataPRIDEJobSummaryReport`).
    *   UI Controls -> Grid Refresh (Filters triggering Kendo Grid `dataSource.read()`).
    *   Parent Grid -> Child Modal/Grid (Double-click interaction).
    *   Child Grid Actions -> Child Grid Refresh/Modal Updates.
3.  **System Testing:** Test the application end-to-end, simulating real user workflows like filtering jobs, viewing details, approving tasks, editing FTIs, and generating outputs (PDF, Email).
4.  **UI/UX Testing:** Ensure the interface is intuitive, responsive, and consistent. Check Kendo UI grid usability (sorting, paging, expanding), modal interactions, and filter control behavior.
5.  **Database Testing:** Verify the Stored Procedures (`SP_FormDataPRIDEJobSummaryReport`, `SP_FormDataOPRSJobSummaryReportUpdateDispatcheTicketParentChild`) directly with sample inputs to ensure they return correct data sets, perform updates/deletes accurately, and handle different parameters (@value1 flags) correctly. Validate data integrity constraints.
6.  **Regression Testing:** Execute a subset of test cases after bug fixes or new feature implementations to ensure existing functionality remains unaffected. Automation is highly recommended here.
7.  **Performance Testing:** Assess the load times for the main grid and child grid, the responsiveness of filtering and actions, especially with large datasets. Monitor AJAX call durations and SP execution times under load.
8.  **Security Testing:** Verify that actions (especially Delete, Approve, Edit) are properly restricted based on user permissions (as hinted by `actionPerform` checks). Check for potential vulnerabilities related to data passed between client and server.

## Key Business Requirements Validation
Based on the context, key requirements include:
*   **Accurate Job Visibility:** Users must see the correct jobs based on applied filters. (Validated via Filter test cases, Grid load tests).
*   **Detailed Task Management:** Users must be able to view and manage child tasks for a parent job. (Validated via Modal/Child Grid tests, FTI tests).
*   **Workflow State Management:** Users must be able to track and update job/task status (e.g., Approved, New). (Validated via Approval tests, Action Menu tests like Push, Pause, Resume).
*   **Data Modification:** Users must be able to accurately edit relevant job/task details (e.g., FTI Price/Qty, Deployment Time). (Validated via FTI tests, Deployment Time modal tests).
*   **Communication & Reporting:** Users must be able to generate outputs like PDFs and send email notifications. (Validated via PDF generation tests, Email modal tests).
*   **Data Integrity:** Actions like Delete, Approve, Edit must update the database correctly and consistently. (Validated via Action tests, DB testing, Integration testing).

## Risk-Based Prioritization
Testing efforts should prioritize areas with higher risk or impact:
1.  **High Priority:**
    *   Core data display and filtering (Main Grid, Date/Dropdown Filters). Data accuracy is paramount.
    *   Job/Task Approval workflow (Approval controls, SP logic). Critical for business process.
    *   Data modification impacting billing or operations (FTI Editing). High financial/operational impact if incorrect.
    *   Key actions: Delete (data loss risk), PDF/Email (external communication).
    *   Child Job display and interaction (Modal, Child Grid). Core to detailed management.
2.  **Medium Priority:**
    *   Less frequent actions (Copy, Push, Pause, Resume, Activate, Recall, Deployment Time).
    *   Secondary UI features (Totalizers, Date range buttons/arrows).
    *   Comment viewing functionality.
    *   Performance under typical load.
3.  **Low Priority:**
    *   Minor UI/UX issues not affecting functionality.
    *   Performance under extreme load (unless specifically required).
    *   Edge case error handling unlikely to be encountered frequently.

## Special Considerations
*   **Kendo UI Dependency:** Testers should be familiar with Kendo UI Grid behavior (data binding, events like `onDataBound`, `detailInit`, API like `dataSource.read()`). Specific Kendo UI testing techniques might be applicable.
*   **Stored Procedure Complexity:** The reliance on large stored procedures (`SP_FormDataPRIDEJobSummaryReport` with `@value1` parameter) means that changes in one part of the application might have unintended consequences elsewhere if the SP logic is affected. Thorough regression testing and potentially dedicated SP testing are crucial.
*   **AJAX Interactions:** Heavy use of AJAX means testers need tools (browser dev tools) to monitor network requests/responses and diagnose issues between client-side JS and server-side WebMethods. Timing issues or race conditions might occur.
*   **Modal Dialogs:** Extensive use of modals requires testing their lifecycle (opening, closing, data loading within modals, interactions between modals if possible).
*   **State Management:** Filters and grid state (expanded rows via localStorage) need careful testing, especially across refreshes and browser sessions.
*   **Permissions:** The context mentions permission checks (`actionPerform`). Testing different user roles (if applicable) is necessary to ensure actions are appropriately restricted.

# 5. Error Handling and Edge Cases

This section catalogs potential errors and defines expected behaviors.

## AJAX Communication Failures
*   **Scenario:** Network interruption, server unavailable, WebMethod error (e.g., 500 Internal Server Error) during calls like `submitDate`, `setChildAprove`, `UpdateFieldTicketItemDetails`.
*   **Reproduction:** Use browser developer tools to simulate network offline status or use tools like Fiddler to intercept and modify responses to return error codes. Trigger actions that make AJAX calls.
*   **Expected Behavior:**
    *   A user-friendly error message should be displayed (e.g., "Failed to update data. Please check your connection and try again.", "An error occurred on the server."). Avoid showing raw stack traces.
    *   Loading indicators (if shown) should be hidden.
    *   The UI should remain in a consistent state (e.g., if an approval failed, the switch should revert to its original state).
    *   The application should remain functional for other operations not requiring the failed call.
*   **Recovery:** User might need to retry the action after the connection is restored or the server issue is fixed. A page refresh might be necessary in some cases.
*   **Verification:** Verify the error message appears, the UI state is consistent, and subsequent actions (where possible) still function.

## Stored Procedure / Database Errors
*   **Scenario:** SP fails due to data integrity issues (e.g., constraint violation), logical errors within the SP, deadlocks, permission issues for the service account, invalid parameters passed from C#.
*   **Reproduction:** Difficult without direct DB access. Can sometimes be simulated by providing input known to violate constraints (e.g., saving duplicate unique keys if validation is only in SP). Review specific SP logic for potential failure points (e.g., division by zero, invalid type casting).
*   **Expected Behavior:**
    *   The error should be caught by the ASP.NET WebMethod.
    *   A generic but informative error message should be propagated back to the client via the AJAX response (e.g., "Database operation failed.", "Failed to save changes."). Specific DB errors should generally not be shown to the end-user.
    *   The UI should handle the AJAX error gracefully (see above).
    *   Data should not be partially updated; transactions should ensure atomicity.
*   **Recovery:** User retries the action. If persistent, requires investigation by developers/DBAs.
*   **Verification:** Verify appropriate error message is shown on UI, check application logs for detailed DB errors, confirm data was not corrupted or partially updated.

## Client-Side Validation Errors
*   **Scenario:** User enters invalid data into fields with client-side validation (e.g., non-numeric input in FTI Price/Qty via `checkTotal`, invalid email format in Send Email modal).
*   **Reproduction:** Enter invalid data formats into the relevant input fields.
*   **Expected Behavior:**
    *   Validation rule triggers immediately or upon attempting to submit/save.
    *   A clear, user-friendly validation message appears near the problematic field (e.g., "Please enter a valid number.", "Invalid email address format.").
    *   The action (e.g., saving FTI, adding email) is prevented until the validation passes.
    *   Focus might be set to the invalid field.
*   **Recovery:** User corrects the invalid input.
*   **Verification:** Verify the validation message appears, the action is blocked, and the action proceeds once valid data is entered.

## Server-Side Validation / Logic Errors
*   **Scenario:** Data passes client-side validation but fails server-side business rules (e.g., attempting to approve a child job without required resources - `UpdateAproveStatusOfAllChild` / `UpdateAproveStatusOfChild`, attempting to push a job not in 'New' status, attempting to apply quoted quantities when none exist).
*   **Reproduction:** Set up data conditions that violate server-side rules (e.g., remove required resources from a child job, change status) and then attempt the action.
*   **Expected Behavior:**
    *   The WebMethod performs the validation check.
    *   The AJAX call returns a specific error/status indicating the validation failure.
    *   A user-friendly message explaining the reason for failure is displayed (e.g., "Cannot approve job: Missing required resources.", "Job status must be 'New' to push.").
    *   The intended data change does not occur in the database.
    *   The UI state remains consistent or reverts (e.g., approval switch stays off).
*   **Recovery:** User must rectify the underlying condition (e.g., assign resources, wait for status change) before retrying.
*   **Verification:** Verify the specific error message is shown, check the database to confirm the status/data was not updated, verify UI consistency.

## Permission Denied Errors
*   **Scenario:** A user without sufficient privileges attempts to perform a restricted action (e.g., Delete Parent/Child job - checked in `actionPerform`).
*   **Reproduction:** Log in as a user with restricted permissions (requires user role setup) and attempt actions like Delete.
*   **Expected Behavior:**
    *   Ideally, the UI control for the action (e.g., Delete button in action menu) should be disabled or hidden for users without permission.
    *   If the control is clickable, the server-side check (`actionPerform` returning 2) should prevent the action.
    *   An appropriate message should be displayed (e.g., "You do not have permission to perform this action.").
    *   No changes are made to the database.
*   **Recovery:** User needs appropriate permissions granted by an administrator.
*   **Verification:** Verify UI controls are disabled/hidden OR verify the permission error message is shown and the action is blocked.

## Data Integrity Issues
*   **Scenario:** Race conditions where two users attempt conflicting updates simultaneously. Orphaned data if delete operations are incomplete. Incorrect calculations in totalizers or FTI totals. Inconsistent state between parent and child jobs.
*   **Reproduction:** Requires specific timing or complex setups. Simulate simultaneous edits, interrupt delete processes, carefully review calculations involving SP logic and client-side updates (`bindTotalizerData`, FTI Save).
*   **Expected Behavior:**
    *   Database constraints and transactions should prevent most data corruption.
    *   Pessimistic or optimistic locking might be implemented (context doesn't specify) to handle concurrent updates, potentially resulting in errors/retries for one user.
    *   Totalizers should accurately reflect the data shown in the grid after filtering/updates.
    *   Parent/child relationships should remain consistent.
*   **Recovery:** May require manual data correction if inconsistencies occur. Application logic should aim to prevent this.
*   **Verification:** Perform concurrent actions. Thoroughly verify data consistency between grids, modals, database, and totalizers after various operations. Use test data designed to expose potential calculation or relationship errors.