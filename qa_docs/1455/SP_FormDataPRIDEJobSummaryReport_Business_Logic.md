# SP_FormDataPRIDEJobSummaryReport Business Logic Analysis

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Domains and Relationships](#business-domains-and-relationships)
3. [Business Processes](#business-processes)
   1. [Other](#other)
4. [Business Rules](#business-rules)
5. [Data Flow](#data-flow)
6. [Business Entities](#business-entities)
7. [Test Cases](#test-cases)
   1. [Other Test Cases](#test-cases-other)

## Executive Summary

Okay, here is a focused analysis of the business logic implemented in the `SP_FormDataPRIDEJobSummaryReport` stored procedure based on the provided code.

## Business Logic Analysis: SP_FormDataPRIDEJobSummaryReport

**Project:** 1455
**File:** SP_FormDataPRIDEJobSummaryReport.sql

### 1. High-Level Overview

This stored procedure acts as a central hub for managing and reporting on "PRIDE" jobs, likely field service operations. It's a multi-purpose procedure controlled primarily by the `@value1` parameter, which dictates the specific action to be performed. Its functions range from complex data retrieval for reporting (job summaries, child job details, field ticket items, documents) and dashboard statistics (totalizers) to data modification actions like updating job statuses, managing approvals, editing field ticket line items, assigning resources, managing supporting documents (photos, PDFs), and handling email notifications related to job summaries. It heavily relies on other stored procedures and functions for tasks like auditing, recalculating totals, applying exception rules, and checking quote validity.

### 2. Business Domains

The procedure spans several core business domains:

*   **Field Service Management:** Tracking job dispatch, execution, status updates, resource assignment (personnel, vehicles, equipment).
*   **Job Costing & Billing Preparation:** Managing field ticket line items (materials, labor, mileage), applying pricing (standard vs. quoted), calculating totals, and flagging jobs for invoicing.
*   **Reporting & Analytics:** Generating detailed and summary reports, providing data for dashboards (totalizers), filtering and sorting job data based on various criteria.
*   **Customer Relationship Management (CRM):** Associating jobs with customers, applying customer-specific pricing/quotes, managing customer-related email notifications.
*   **Resource Management:** Assigning and tracking employees, trucks, and trailers to specific job tasks. Includes tracking employee weekly hours.
*   **Quote Management:** Integrating with quotes to apply specific pricing and item configurations.
*   **Document Management:** Attaching, viewing, and managing photos and PDF documents related to jobs.
*   **User Access Control & Permissions:** Filtering data and enabling/disabling actions based on user privileges.
*   **Workflow Management:** Handling job status progression (New -> Dispatched -> Completed -> Approved) and approval workflows.
*   **ERP Integration (Interface):** Handling Macola-specific data like Location Codes and Sales Order Numbers, indicating an interface with an ERP system.

### 3. Key Business Processes Implemented

*   **Job Summary Reporting:**
    *   Retrieving a paginated list of parent jobs based on extensive filtering criteria (date range, customer, service type, status, operational area, etc.) and sorting preferences.
    *   Displaying key job information (customer, location, dates, work ticket #, totals, status).
    *   Calculating derived information like `JobDateExpired`, aggregated ticket numbers/service types, and invoice status.
*   **Child Job (Task/Shift) Management:**
    *   Retrieving detailed information for all child jobs associated with a parent job.
    *   Displaying status, assigned resources, calculated totals (hours, mileage, items), approval status, and exception flags.
    *   Updating individual child job attributes: Employee, Truck, Trailer, Arrival/Departure Times, Status.
*   **Field Ticket Item (Line Item) Management:**
    *   Retrieving line items (PFT records) for a specific child job, including pricing, quantity, and notes.
    *   Adding/Updating field ticket line items, either individually or in bulk (using JSON).
    *   Applying pricing based on standard price lists or active quotes.
    *   Refreshing line items based on the latest price list/quote data, deactivating obsolete items and adding required ones.
    *   Deleting all field ticket items for a child job (effectively resetting it).
*   **Job Approval Workflow:**
    *   Updating the approval status for individual child jobs.
    *   Updating the approval status for all eligible child jobs under a parent job (bulk approval), potentially with resource validation checks.
    *   Triggering recalculation of parent job approval readiness based on child statuses.
*   **Document Handling:**
    *   Uploading and associating photos and PDF files with child jobs.
    *   Retrieving lists of associated photos/PDFs with metadata and access URLs.
    *   Updating metadata (names, sort order) for existing documents.
    *   Deleting document associations.
    *   Handling annotated photo updates.
*   **Email Notification:**
    *   Aggregating potential email recipients based on job data (techs, reps, customer defaults).
    *   Saving email sending details (recipients, custom message) and marking the job as having had an email sent.
    *   Retrieving current and historical email sending details.
    *   Providing necessary information (attachment name/URL) for the application layer to generate and send the email.
*   **Data Lookup & Filtering:**
    *   Providing lists of Customers, Service Types, Employees, Trucks, Trailers, Locations (including Macola Locations), Operators, Facilities, and Operational Areas for UI dropdowns or filtering, often respecting user privileges.
*   **Dashboard/Totalizer Data Generation:**
    *   Calculating counts and totals for jobs categorized by status (New, Dispatched, Hold, Flagged, Pending Approval, Approved) based on specified filters.

### 4. Business Rules Enforced

*   **User Access Control:** Data visibility (Customers, Operational Areas) is restricted based on `FormDataPRIDUserPrivileges`. UI actions (Edit Job, Approve Job, Delete Job) are enabled/disabled based on flags in `FormDataPRIDUserPrivileges`.
*   **Pricing Logic:** Field ticket items are priced either using the standard customer price list (`Regular Price`) or a specific quote (`Quote Price`) if a valid quote is applied to the job and service type.
*   **Quote Validity:** Checks (`UDF_PRIDCheckValidQuoteServiceType`, `UDF_PRIDCheckValidQuoteManualUnits`) determine if a quote is applicable to a specific service type and whether quantities should be automatically applied or manually entered.
*   **Dispatch Readiness:** A child job is considered `readyForDispatch` only if all resources (Employee, Truck, Trailer) required by its Service Type have been assigned.
*   **Approval Constraints:** Child jobs can typically only be approved if they are in a 'Completed' or 'Rolling' status. Bulk approval requires necessary resources (Employee, Truck, Trailer) to be assigned if the service type mandates them.
*   **Data Integrity & Recalculation:** Updates to child jobs or field ticket items trigger recalculations of totals (`SP_formDataPridDispatchTicketCaculateTotal`), parent/child approval statuses (`Sp_formdatapriddispatchticketapprovalupdate`), and exception rule checks (`SP_FormDataPridApplyExceptionRules`). Flags indicating data updates relevant to invoicing or email generation are set (`Sp_formdatapridisinvoicedataupdated`, `SP_FormdataPridIsEmailDataUpdated`, `SP_FormdataPridIsMasterFieldTicketDataUpdated`).
*   **Job Deletion Rules:** Parent job deletion appears controlled by the `DeleteEnabled` flag, calculated based on whether any child jobs have progressed beyond the 'New' status (ticketstatus != 1 for field service types). Child job (Field Ticket) deletion resets the child job status to 'New'.
*   **Auditing:** Most data modification actions trigger audit records via `Prcauditprocess` or `prcAuditProcess_v3`.
*   **Document Sort Order:** Photo sort order (`PhotoSortOrder`) should ideally be unique per job; the procedure includes a check to prevent duplicate sort orders during updates. If `PhotoSortOrder` is null, `ItemLevel` is used for ordering.
*   **Employee Hours:** Changing an employee assignment on a child job triggers recalculation of weekly hours for both the old and new employee (`SP_FormDataPridEmployeesWeeklyHoursCalculate`).
*   **Mandatory Items:** Field Ticket Items can be marked as mandatory (`mandatory` flag).

### 5. Data Flow

*   **Input:** Primarily through Stored Procedure parameters. `@value1` acts as the main command. Other parameters provide filtering criteria (`@fdate`, `@tdate`, `@value2`-`@value9`), identifiers (`@ChildJobId`, `@value2`, `@value3`), pagination/sorting info (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`), user context (`@userEmail`, `@UserID`), and data for updates (e.g., `@price`, `@quantity`, `@Notes`, `@AprovalStatusChild`, `@jobStatus`, `@PhotoType`, `@EmailDetailsList`, JSON in `@value2` for `UpdateFTINew`).
*   **Processing:**
    *   Extensive use of temporary tables (`#temp_...`) for intermediate results, filtering, and aggregation, especially in the `Paging` and `RefreshFieldTicketItemDetails` sections.
    *   Conditional logic (`IF @value1 = ...`) directs execution.
    *   Joins across multiple tables (`FormDataPRIDEDispatchTicket`, `...Child`, `...PFT`, `...Customer`, `...ServiceType`, `...Employee`, etc.) to gather related data.
    *   Calls to User-Defined Functions (UDFs) for specific checks (e.g., quote validity, settings).
    *   Calls to other Stored Procedures for complex operations (auditing, recalculations, approvals, exceptions, master PDF data insertion, weekly hours).
    *   Data aggregation (`STRING_AGG`, `SUM`, `COUNT`, `MAX`) for reporting and calculations.
    *   Direct `INSERT`, `UPDATE`, `DELETE` operations on persistent tables based on the requested action (`@value1`).
*   **Output:**
    *   Result sets containing data for reports, grids, or dropdown lists (e.g., job summary list, child job details, field ticket items, photos, PDFs, email history, lookup lists).
    *   Row counts or status messages ('Success', 'Error', specific error details like resource conflicts on bulk approve).
    *   Calculated values (e.g., `TotalCount` for pagination, attachment details for emails).
    *   Modification of data in the `FormDataPRID...` tables.

### 6. Business Entities and Their Relationships

*   **FormDataPRIDEDispatchTicket (Parent Job):** The main job record.
    *   *Relates to:* `FormDataPRIDCableCompanyCustomer` (1:1), `FormDataPridOperatorSetup` (1:1), `FormDataPridQuoteConfigurator` (1:1), `FormDataPRIDStates` (1:1), `FormDataPRIDCounties` (1:1), `FormDataPridMasterData` (Operational Area, 1:1).
    *   *Has many:* `FormDataPRIDEDispatchTicketChild`.
    *   *Has one:* `FormDataPRIDEDispatchTicketTotal` (Aggregated totals).
    *   *Has one:* `FormDataPridMasterFieldTicket` (Link for master PDF/Invoice data).
    *   *Has one:* `FormDataPridJobSummaryEmailsMaster` (Email tracking).
    *   *Can have one:* `FormDataPRIDInvoice`.
*   **FormDataPRIDEDispatchTicketChild (Child Job / Task / Shift):** Represents a specific task or shift within a Parent Job.
    *   *Belongs to:* `FormDataPRIDEDispatchTicket` (Many:1).
    *   *Relates to:* `FormDataPRIDServiceType` (1:1), `FormDataPRIDEmployee` (Assigned Employee, 1:1 nullable), `FormDataPRIDTruckMaster` (Assigned Truck, 1:1 nullable), `FormDataPRIDTrailerMaster` (Assigned Trailer, 1:1 nullable), `FormDataPRIDAddressSetup` (Yard, 1:1 nullable), `FormDataPRIDDispatcherMaster` (Dispatcher, 1:1 nullable), `FormDataPRIDDispatcher` (Service Tech legacy?, 1:1 nullable), `FormDataPridQuoteConfigurator` (1:1, inherited from parent or assigned).
    *   *Has many:* `FormDataPRIDPFT` (Field Ticket Line Items).
    *   *Has many:* `FormDataPRIDEDispatchTicketChildPdfFiles` (Attached PDFs).
    *   *Has one:* `FormDataPRIDEDispatchTicketChildTotal` (Aggregated totals for the child job).
*   **FormDataPRIDPFT (Field Ticket Line Item / Photo/PDF Record):** Represents line items (cost items), or serves as a container for photos/PDFs linked to a Child Job. ItemLevel=0 often holds header/summary info for the PFT.
    *   *Belongs to:* `FormDataPRIDEDispatchTicketChild` (Many:1 via `childJobId`).
    *   *Relates to:* `FormDataPRIDFieldTicketItem` (Master Item definition, 1:1 nullable via `fieldTicketItemId` or `fieldTicketItemIdM`).
    *   *Can relate to:* `FormDataPRIDEmployee` (Spooler/Employee override, 1:1 nullable), `FormDataPRIDTruckMaster` (Truck override, 1:1 nullable), `FormDataPRIDTrailerMaster` (Trailer override, 1:1 nullable).
*   **FormDataPRIDFieldTicketItem:** Master definition of a billable/trackable item.
    *   *Used by:* `FormDataPRIDPFT`.
    *   *Related via:* `formdatapridfieldticketitemsCustomerPriceList`.
*   **formdatapridfieldticketitemsCustomerPriceList:** Links Customers, Service Types, and Field Ticket Items, defining applicability, pricing (Regular/Quote), and relevance.
*   **FormDataPRIDUserPrivileges:** Defines user permissions.
    *   *Relates to:* `FormDataPRIDUserPrivilegesCustomer` (Many:Many via PrivilegeID), `FormDataPRIDUserPrivilegesOperationArea` (Many:Many via PrivilegeGUID).
*   **Supporting Entities:** `FormDataPRIDCableCompanyCustomer`, `FormDataPRIDServiceType`, `FormDataPRIDEmployee`, `FormDataPRIDTruckMaster`, `FormDataPRIDTrailerMaster`, `FormDataPRIDAddressSetup` (Yards/Facilities), `FormDataPridOperatorSetup`, `FormDataPRIDStates`, `FormDataPRIDCounties`, `FormDataPridMasterData`, `FormDataPridQuoteConfigurator`, `FormDataPRIDInvoice`.
*   **Email Tracking Entities:** `FormDataPridJobSummaryEmailsMaster`, `FormDataPridJobSummaryEmailsMasterDetails` (and their Audit tables).

## Business Domains and Relationships

The procedure spans several core 
*   **Field Service Management:** Tracking job dispatch, execution, status updates, resource assignment (personnel, vehicles, equipment).
*   **Job Costing & Billing Preparation:** Managing field ticket line items (materials, labor, mileage), applying pricing (standard vs. quoted), calculating totals, and flagging jobs for invoicing.
*   **Reporting & Analytics:** Generating detailed and summary reports, providing data for dashboards (totalizers), filtering and sorting job data based on various criteria.
*   **Customer Relationship Management (CRM):** Associating jobs with customers, applying customer-specific pricing/quotes, managing customer-related email notifications.
*   **Resource Management:** Assigning and tracking employees, trucks, and trailers to specific job tasks. Includes tracking employee weekly hours.
*   **Quote Management:** Integrating with quotes to apply specific pricing and item configurations.
*   **Document Management:** Attaching, viewing, and managing photos and PDF documents related to jobs.
*   **User Access Control & Permissions:** Filtering data and enabling/disabling actions based on user privileges.
*   **Workflow Management:** Handling job status progression (New -> Dispatched -> Completed -> Approved) and approval workflows.
*   **ERP Integration (Interface):** Handling Macola-specific data like Location Codes and Sales Order Numbers, indicating an interface with an ERP system.

## Business Processes

This section details the key business processes implemented in SP_FormDataPRIDEJobSummaryReport.

### Other

#### Process Overview

*Other* process handles the following business functions:

- **[dbo].[SP_FormDataPRIDEJobSummaryReport]**: Procedure [dbo].[SP_FormDataPRIDEJobSummaryReport] from SP_FormDataPRIDEJobSummaryReport

#### Database Entities Involved

No specific database entities identified for this process.

#### Process Inputs

No specific inputs identified for this process.

---

## Business Rules

*   **User Access Control:** Data visibility (Customers, Operational Areas) is restricted based on `FormDataPRIDUserPrivileges`. UI actions (Edit Job, Approve Job, Delete Job) are enabled/disabled based on flags in `FormDataPRIDUserPrivileges`.
*   **Pricing Logic:** Field ticket items are priced either using the standard customer price list (`Regular Price`) or a specific quote (`Quote Price`) if a valid quote is applied to the job and service type.
*   **Quote Validity:** Checks (`UDF_PRIDCheckValidQuoteServiceType`, `UDF_PRIDCheckValidQuoteManualUnits`) determine if a quote is applicable to a specific service type and whether quantities should be automatically applied or manually entered.
*   **Dispatch Readiness:** A child job is considered `readyForDispatch` only if all resources (Employee, Truck, Trailer) required by its Service Type have been assigned.
*   **Approval Constraints:** Child jobs can typically only be approved if they are in a 'Completed' or 'Rolling' status. Bulk approval requires necessary resources (Employee, Truck, Trailer) to be assigned if the service type mandates them.
*   **Data Integrity & Recalculation:** Updates to child jobs or field ticket items trigger recalculations of totals (`SP_formDataPridDispatchTicketCaculateTotal`), parent/child approval statuses (`Sp_formdatapriddispatchticketapprovalupdate`), and exception rule checks (`SP_FormDataPridApplyExceptionRules`). Flags indicating data updates relevant to invoicing or email generation are set (`Sp_formdatapridisinvoicedataupdated`, `SP_FormdataPridIsEmailDataUpdated`, `SP_FormdataPridIsMasterFieldTicketDataUpdated`).
*   **Job Deletion Rules:** Parent job deletion appears controlled by the `DeleteEnabled` flag, calculated based on whether any child jobs have progressed beyond the 'New' status (ticketstatus != 1 for field service types). Child job (Field Ticket) deletion resets the child job status to 'New'.
*   **Auditing:** Most data modification actions trigger audit records via `Prcauditprocess` or `prcAuditProcess_v3`.
*   **Document Sort Order:** Photo sort order (`PhotoSortOrder`) should ideally be unique per job; the procedure includes a check to prevent duplicate sort orders during updates. If `PhotoSortOrder` is null, `ItemLevel` is used for ordering.
*   **Employee Hours:** Changing an employee assignment on a child job triggers recalculation of weekly hours for both the old and new employee (`SP_FormDataPridEmployeesWeeklyHoursCalculate`).
*   **Mandatory Items:** Field Ticket Items can be marked as mandatory (`mandatory` flag).

## Data Flow

*   **Input:** Primarily through Stored Procedure parameters. `@value1` acts as the main command. Other parameters provide filtering criteria (`@fdate`, `@tdate`, `@value2`-`@value9`), identifiers (`@ChildJobId`, `@value2`, `@value3`), pagination/sorting info (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`), user context (`@userEmail`, `@UserID`), and data for updates (e.g., `@price`, `@quantity`, `@Notes`, `@AprovalStatusChild`, `@jobStatus`, `@PhotoType`, `@EmailDetailsList`, JSON in `@value2` for `UpdateFTINew`).
*   **Processing:**
    *   Extensive use of temporary tables (`#temp_...`) for intermediate results, filtering, and aggregation, especially in the `Paging` and `RefreshFieldTicketItemDetails` sections.
    *   Conditional logic (`IF @value1 = ...`) directs execution.
    *   Joins across multiple tables (`FormDataPRIDEDispatchTicket`, `...Child`, `...PFT`, `...Customer`, `...ServiceType`, `...Employee`, etc.) to gather related data.
    *   Calls to User-Defined Functions (UDFs) for specific checks (e.g., quote validity, settings).
    *   Calls to other Stored Procedures for complex operations (auditing, recalculations, approvals, exceptions, master PDF data insertion, weekly hours).
    *   Data aggregation (`STRING_AGG`, `SUM`, `COUNT`, `MAX`) for reporting and calculations.
    *   Direct `INSERT`, `UPDATE`, `DELETE` operations on persistent tables based on the requested action (`@value1`).
*   **Output:**
    *   Result sets containing data for reports, grids, or dropdown lists (e.g., job summary list, child job details, field ticket items, photos, PDFs, email history, lookup lists).
    *   Row counts or status messages ('Success', 'Error', specific error details like resource conflicts on bulk approve).
    *   Calculated values (e.g., `TotalCount` for pagination, attachment details for emails).
    *   Modification of data in the `FormDataPRID...` tables.

## Business Entities

*   **FormDataPRIDEDispatchTicket (Parent Job):** The main job record.
    *   *Relates to:* `FormDataPRIDCableCompanyCustomer` (1:1), `FormDataPridOperatorSetup` (1:1), `FormDataPridQuoteConfigurator` (1:1), `FormDataPRIDStates` (1:1), `FormDataPRIDCounties` (1:1), `FormDataPridMasterData` (Operational Area, 1:1).
    *   *Has many:* `FormDataPRIDEDispatchTicketChild`.
    *   *Has one:* `FormDataPRIDEDispatchTicketTotal` (Aggregated totals).
    *   *Has one:* `FormDataPridMasterFieldTicket` (Link for master PDF/Invoice data).
    *   *Has one:* `FormDataPridJobSummaryEmailsMaster` (Email tracking).
    *   *Can have one:* `FormDataPRIDInvoice`.
*   **FormDataPRIDEDispatchTicketChild (Child Job / Task / Shift):** Represents a specific task or shift within a Parent Job.
    *   *Belongs to:* `FormDataPRIDEDispatchTicket` (Many:1).
    *   *Relates to:* `FormDataPRIDServiceType` (1:1), `FormDataPRIDEmployee` (Assigned Employee, 1:1 nullable), `FormDataPRIDTruckMaster` (Assigned Truck, 1:1 nullable), `FormDataPRIDTrailerMaster` (Assigned Trailer, 1:1 nullable), `FormDataPRIDAddressSetup` (Yard, 1:1 nullable), `FormDataPRIDDispatcherMaster` (Dispatcher, 1:1 nullable), `FormDataPRIDDispatcher` (Service Tech legacy?, 1:1 nullable), `FormDataPridQuoteConfigurator` (1:1, inherited from parent or assigned).
    *   *Has many:* `FormDataPRIDPFT` (Field Ticket Line Items).
    *   *Has many:* `FormDataPRIDEDispatchTicketChildPdfFiles` (Attached PDFs).
    *   *Has one:* `FormDataPRIDEDispatchTicketChildTotal` (Aggregated totals for the child job).
*   **FormDataPRIDPFT (Field Ticket Line Item / Photo/PDF Record):** Represents line items (cost items), or serves as a container for photos/PDFs linked to a Child Job. ItemLevel=0 often holds header/summary info for the PFT.
    *   *Belongs to:* `FormDataPRIDEDispatchTicketChild` (Many:1 via `childJobId`).
    *   *Relates to:* `FormDataPRIDFieldTicketItem` (Master Item definition, 1:1 nullable via `fieldTicketItemId` or `fieldTicketItemIdM`).
    *   *Can relate to:* `FormDataPRIDEmployee` (Spooler/Employee override, 1:1 nullable), `FormDataPRIDTruckMaster` (Truck override, 1:1 nullable), `FormDataPRIDTrailerMaster` (Trailer override, 1:1 nullable).
*   **FormDataPRIDFieldTicketItem:** Master definition of a billable/trackable item.
    *   *Used by:* `FormDataPRIDPFT`.
    *   *Related via:* `formdatapridfieldticketitemsCustomerPriceList`.
*   **formdatapridfieldticketitemsCustomerPriceList:** Links Customers, Service Types, and Field Ticket Items, defining applicability, pricing (Regular/Quote), and relevance.
*   **FormDataPRIDUserPrivileges:** Defines user permissions.
    *   *Relates to:* `FormDataPRIDUserPrivilegesCustomer` (Many:Many via PrivilegeID), `FormDataPRIDUserPrivilegesOperationArea` (Many:Many via PrivilegeGUID).
*   **Supporting Entities:** `FormDataPRIDCableCompanyCustomer`, `FormDataPRIDServiceType`, `FormDataPRIDEmployee`, `FormDataPRIDTruckMaster`, `FormDataPRIDTrailerMaster`, `FormDataPRIDAddressSetup` (Yards/Facilities), `FormDataPridOperatorSetup`, `FormDataPRIDStates`, `FormDataPRIDCounties`, `FormDataPridMasterData`, `FormDataPridQuoteConfigurator`, `FormDataPRIDInvoice`.
*   **Email Tracking Entities:** `FormDataPridJobSummaryEmailsMaster`, `FormDataPridJobSummaryEmailsMasterDetails` (and their Audit tables).

## Test Cases

The following test cases validate the business logic implemented in SP_FormDataPRIDEJobSummaryReport.

### Other Test Cases

#### Other_TC001: Verify the report generation handles scenarios where no PRIDE jobs exist or match the implicit report criteria.

**Priority**: Medium

**Preconditions**:
No PRIDE jobs exist in the system, or none fall within the default/implicit date range or status criteria used by the stored procedure.

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Trigger the execution of the SP_FormDataPRIDEJobSummaryReport procedure (e.g., by accessing the relevant report screen or function). | The procedure executes without technical errors. |
| 2. Observe the output data structure or the rendered report. | The report/data indicates 'No data available', shows zero counts for all job categories, or displays an empty summary section as per design. |

**Expected Final Result**:
The PRIDE Job Summary Report structure is generated correctly, clearly indicating the absence of relevant job data, without any system failures.

---

#### Other_TC002: Verify the report generates successfully and displays summary information when valid PRIDE job data exists.

**Priority**: High

**Preconditions**:
Multiple PRIDE jobs exist with various statuses (e.g., 'New', 'In Progress', 'Completed', 'On Hold') that fall within the implicit criteria of the report.

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Trigger the execution of the SP_FormDataPRIDEJobSummaryReport procedure. | The procedure executes without technical errors. |
| 2. Observe the output data structure or the rendered report. | The report displays summary sections populated with non-zero counts or aggregated data corresponding to the existing jobs. |

**Expected Final Result**:
The PRIDE Job Summary Report is successfully generated, displaying relevant summary statistics based on the available job data.

---

#### Other_TC003: Verify basic accuracy of job counts presented in the summary report against known data.

**Priority**: High

**Preconditions**:
A known, small number of PRIDE jobs exist with specific statuses within the report's criteria (e.g., 3 'Completed', 2 'In Progress'). The exact counts are confirmed beforehand.

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Trigger the execution of the SP_FormDataPRIDEJobSummaryReport procedure. | The procedure executes without technical errors and the report is generated. |
| 2. Locate the summary count for 'Completed' jobs in the report/data. | The count displayed is exactly 3. |
| 3. Locate the summary count for 'In Progress' jobs in the report/data. | The count displayed is exactly 2. |

**Expected Final Result**:
The report accurately reflects the counts of jobs for at least key, verifiable statuses, confirming basic aggregation logic.

---

#### Other_TC004: Verify how jobs with a less common or non-terminal status (e.g., 'Pending Approval') are represented in the summary.

**Priority**: Medium

**Preconditions**:
At least one PRIDE job exists with the status 'Pending Approval' within the report's criteria. Other jobs with standard statuses also exist.

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Trigger the execution of the SP_FormDataPRIDEJobSummaryReport procedure. | The procedure executes without technical errors and the report is generated. |
| 2. Examine the report summary sections/categories. | Jobs with 'Pending Approval' status are consistently handled according to business rules: either displayed in a dedicated category, included in a broader 'Active'/'Not Completed' count, or explicitly excluded if defined so. |

**Expected Final Result**:
The report correctly accounts for jobs in the 'Pending Approval' state as per the defined reporting standards, ensuring consistent classification.

---

