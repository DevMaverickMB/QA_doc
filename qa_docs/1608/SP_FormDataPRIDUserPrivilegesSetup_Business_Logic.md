# SP_FormDataPRIDUserPrivilegesSetup Business Logic Analysis

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Domains and Relationships](#business-domains-and-relationships)
3. [Business Processes](#business-processes)
   1. [User Privilege Management / Application Access Control](#user-privilege-management---application-access-control)
4. [Business Rules](#business-rules)
5. [Data Flow](#data-flow)
6. [Business Entities](#business-entities)
7. [Test Cases](#test-cases)
   1. [User Privilege Management / Application Access Control Test Cases](#test-cases-user-privilege-management---application-access-control)

## Executive Summary

Okay, here is a focused analysis of the business logic within the `SP_FormDataPRIDUserPrivilegesSetup` stored procedure based on the provided code and metadata.

## Business Logic Analysis: SP_FormDataPRIDUserPrivilegesSetup

### 1. High-Level Overview

This stored procedure acts as a central orchestrator for managing user-specific privileges and application settings within the FormDataPRID system, specifically for the 'OPRS' client. It encapsulates the core Create, Read, Update, and Delete (CRUD) operations for user privilege profiles. It also provides lookup functions to retrieve necessary reference data (like job types, customers, facilities) often used to populate user interfaces. The procedure uses a primary parameter (`@value1`) to dispatch control flow to different functional blocks (e.g., insert, update, select list, select single, delete, get lookups). A key characteristic is its management of numerous detailed permissions and associations (like allowed customers, job types, facilities, roles, etc.) primarily through parsing and processing comma-separated strings passed as input parameters. Comprehensive auditing is implemented for delete and update operations.

### 2. Business Domain(s)

*   **User Privilege Management / Application Access Control:** This is the primary domain. The procedure defines *what* actions a user can perform and *what* data subsets (customers, facilities, divisions, job types, etc.) they can interact with.
*   **Configuration Management:** It manages user-specific application settings (e.g., default date, default job types, timezone).
*   **Master Data Management (Supporting Role):** It frequently retrieves data from master data tables (`FormDataPridMasterData`, `FormDataPRIDAddressSetup`, `FormDataPRIDCableCompanyCustomer`) to provide lists for selection and display descriptive text instead of just IDs.
*   **Auditing & Compliance:** The procedure explicitly logs changes (updates/deletes) to privilege settings into dedicated audit tables.

### 3. Key Business Processes Implemented

*   **Defining User Privilege Profiles:** Creating new sets of permissions and associated data scopes for a specific user (`InsertUserPrivileges`).
*   **Viewing/Querying User Privileges:**
    *   Listing all configured user privileges with sorting, filtering, and pagination (`SelectUsers`).
    *   Retrieving the detailed configuration for a single user for display or editing (`EditUserPrivileges`, `GetUserDetails`).
*   **Modifying User Privilege Profiles:** Updating existing privilege settings, flags, and associated data scopes (`UpdateUserPrivileges`).
*   **Revoking User Privilege Profiles:** Deleting a user's specific privilege configuration (`DeleteUserPrivileges`).
*   **Retrieving Reference Data for Configuration:** Providing lists of selectable options like Job Types, Customers, Facilities, Roles, etc., for the UI (`SelectJobType`, `SelectCustomer`, `SelectAssignFacility`, etc.).
*   **Auditing Privilege Modifications:** Recording before-images of data prior to updates and deletions (`UpdateUserPrivileges`, `DeleteUserPrivileges` logic inserting into `_audit` tables and calling `prcAuditProcess_V3`).

### 4. Business Rules Enforced

*   **User Privilege Uniqueness:** A specific username (`@Username`, linked to `clientuser.UserID`) can only have one active privilege record within the client (`@clientId`). Checked during `InsertUserPrivileges` and `UpdateUserPrivileges`.
*   **Client Context:** All operations are performed within the context of a specific client (`@clientId`), often hardcoded or validated as 'OPRS'.
*   **Granular Access Control:** Privileges are highly specific, controlling visibility (`IsShow...`), edit rights (`IsEdit...`), deletion rights (`IsAllow...`), approval rights (`IsAllowedToApproveJobs`), and access to specific functional areas (Cable Shop flags, Shipper/Receiver flags).
*   **Data Scoping:** User access can be restricted to specific:
    *   Customers
    *   Job Types / Default Job Types
    *   Job Statuses / Default Job Statuses
    *   Operational Areas / Default Operational Areas
    *   Assignable Facilities / Authorized Assignable Facilities
    *   Divisions (or "All")
    *   Pay Structures
    *   Service Type Categories / Default Service Type Categories
    *   Job Roles / Default Job Roles
    *   Vehicle Types / Default Vehicle Types
    *   Equipment Types / Default Equipment Types
*   **"All" Access Representation:** The system uses specific logic (e.g., checking for value '0' or absence of records in detail tables) to represent access to "All" Customers, "All" Facilities, etc., when displaying aggregated data (`SelectUsers`, `EditUserPrivileges`).
*   **Mandatory Auditing:** Deletions and updates trigger the logging of the previous state into corresponding `_audit` tables.
*   **Default Settings:** Users have configurable default settings for date views, job types, operation areas, etc.

### 5. Data Flow

*   **Input:** The procedure receives the action type (`@value1`), user identifiers (`@Username`, `@useremail`), client ID (`@clientId`), numerous boolean flags (`@Is...`), comma-separated lists of IDs (`@customer`, `@jobtype`, `@DivisionId`, etc.), and potentially pagination/filter/sort criteria (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`).
*   **Processing:**
    1.  **(Unconditional)** Executes `SP_FormDataPridAddDivisionToUserPrivilege`.
    2.  Based on `@value1`:
        *   **Lookups (`Select...`):** Reads from master/setup tables (`FormDataPridMasterData`, `FormDataPRIDAddressSetup`, etc.) usually filtered by `ClientId='OPRS'` and `flagactive=1`.
        *   **Create (`InsertUserPrivileges`):** Checks for username existence. Inserts a primary record into `FormDataPRIDUserPrivileges`. Parses comma-separated lists using `string_split` and inserts multiple records into various detail tables (e.g., `FormDataPRIDUserPrivilegesCustomer`, `FormDataPRIDUserPrivilegesJobType`, etc.) linking back via the new `PrivilegeID`.
        *   **Read List (`SelectUsers`):** Uses dynamic SQL to build a query selecting from `FormDataPRIDUserPrivileges`. Aggregates data from multiple detail tables using `STUFF` and `FOR XML PATH`. Applies filtering (`@SQLFilterString`) and sorting (`@SQLSortString`). Uses global temporary tables (`##tblMaster`, `##tblMasterFinal`) to handle pagination (`@FromNumber`, `@ToNumber`).
        *   **Read Single (`EditUserPrivileges`, `GetUserDetails`):** Selects a single record from `FormDataPRIDUserPrivileges` based on `@value2` (RecordId) or `@useremail`. May aggregate details using `STUFF/FOR XML PATH` similar to `SelectUsers`.
        *   **Update (`UpdateUserPrivileges`):**
            *   Audits: Inserts current state from detail tables into `_audit` tables. Calls `prcAuditProcess_V3` for the main table.
            *   Updates: Modifies the main record in `FormDataPRIDUserPrivileges`.
            *   Deletes: Removes *all* existing detail records associated with the `PrivilegeID` (`@value2`).
            *   Inserts: Parses *new* comma-separated lists and inserts new detail records (similar to Create).
        *   **Delete (`DeleteUserPrivileges`):**
            *   Audits: Inserts current state from detail tables into `_audit` tables. Calls `prcAuditProcess_V3` for the main table.
            *   Deletes: Removes records from all detail tables associated with the `PrivilegeID` (`@value2`). Deletes the main record from `FormDataPRIDUserPrivileges`.
*   **Output:** Returns result sets containing:
    *   Lists of reference data (for lookups).
    *   A paginated/filtered/sorted list of user privileges (`SelectUsers`) and a total count.
    *   Details of a single user's privileges (`EditUserPrivileges`, `GetUserDetails`).
    *   Status messages ('Saved', 'Present') or row counts (for Delete).

### 6. Business Entities and Their Relationships

*   **Core Entity:**
    *   `UserPrivilege`: Represents a specific configuration of permissions and settings for a user. (Mapped to `FormDataPRIDUserPrivileges` table).
*   **Primary Relationship:**
    *   `User` (from `clientuser` table) `1 <--> 1` `UserPrivilege` (within a specific ClientId). Linked via `UserName`/`UserID`.
*   **Supporting Entities & Relationships (1 UserPrivilege <--> * Many Detail Records):** The `UserPrivilege` entity has one-to-many relationships with numerous detail/linking tables, which in turn link to other business entities:
    *   `UserPrivilege` `1 --> *` `UserPrivilegesCustomer` `* --> 1` `Customer` (`FormDataPRIDCableCompanyCustomer`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobType` `* --> 1` `JobType` (`FormDataPridMasterData` where `GroupCode='OperationTypeCategory'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobType` `* --> 1` `JobType` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobStatus` `* --> 1` `JobStatus` (`FormDataPridMasterData` where `GroupCode='JobStatus'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobStatus` `* --> 1` `JobStatus` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesAssignFacility` `* --> 1` `Facility` (`FormDataPRIDAddressSetup`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesAuthAssignFacility` `* --> 1` `Facility` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesPayStructure` (Contains 'Hourly'/'Salary')
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDivision` `* --> 1` `Division` (`FormDataPRIDAddressSetup`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesServiceTypeCategory` `* --> 1` `ServiceTypeCategory` (`FormDataPridMasterData` where `GroupCode='ServiceTypeCategory'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultServiceTypeCategory` `* --> 1` `ServiceTypeCategory` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesOperationArea` `* --> 1` `OperationArea` (`FormDataPridMasterData` where `GroupCode='Operational Area'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultOperationArea` `* --> 1` `OperationArea` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobRole` `* --> 1` `JobRole` (`FormDataPridMasterData` where `GroupCode='JobRole'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobRole` `* --> 1` `JobRole` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesVehicleType` `* --> 1` `VehicleType` (`FormDataPridMasterData` where `GroupCode='TruckTypeSetup'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultVehicleType` `* --> 1` `VehicleType` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesEquipmentType` `* --> 1` `EquipmentType` (`FormDataPridMasterData` where `GroupCode='TrailerTypeSetup'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultEquipmentType` `* --> 1` `EquipmentType` (...)
*   **Audit Entities:** Each primary and detail table has a corresponding `_audit` table (e.g., `FormDataPRIDUserPrivileges_audit`, `FormDataPRIDUserPrivilegesCustomer_audit`) storing historical versions of the records.

## Business Domains and Relationships

*   **User Privilege Management / Application Access Control:** This is the primary *   **Configuration Management:** It manages user-specific application settings (e.g., default date, default job types, timezone).
*   **Master Data Management (Supporting Role):** It frequently retrieves data from master data tables (`FormDataPridMasterData`, `FormDataPRIDAddressSetup`, `FormDataPRIDCableCompanyCustomer`) to provide lists for selection and display descriptive text instead of just IDs.
*   **Auditing & Compliance:** The procedure explicitly logs changes (updates/deletes) to privilege settings into dedicated audit tables.

## Business Processes

This section details the key business processes implemented in SP_FormDataPRIDUserPrivilegesSetup.

### User Privilege Management / Application Access Control

#### Process Overview

*User Privilege Management / Application Access Control* process handles the following business functions:

- **SP_FormDataPRIDUserPrivilegesSetup**: This stored procedure manages user privilege configurations within the FormDataPRID system. It centralizes CRUD (Create, Read, Update, Delete) operations and lookups for user-specific settings and permissions.
Based on the `@value1` parameter, it performs different actions:
- **Lookups ('SelectJobType', 'SelectJobStatus', etc.):** Retrieves master data or setup lists (like customers, facilities, job roles) likely used to populate UI dropdowns. Uses hardcoded 'OPRS' ClientId extensively.
- **'GetUserDetails':** Fetches specific privilege settings for a single user.
- **'InsertUserPrivileges':** Creates a new user privilege record and associated detail records (customers, job types, facilities, roles, vehicle/equipment types, pay structure, divisions, etc.) based on comma-separated input strings parsed using `string_split` and temporary tables. Checks for existing usernames.
- **'SelectUsers':** Lists existing user privilege setups with aggregated detail data (using `STUFF` and `FOR XML PATH`). Implements dynamic sorting, filtering, and pagination using dynamic SQL and global temporary tables.
- **'EditUserPrivileges':** Retrieves a specific user privilege record and its associated aggregated details for editing purposes.
- **'DeleteUserPrivileges':** Deletes a user privilege record and all its associated detail records after first logging the deleted data into corresponding `_audit` tables. Uses `prcAuditProcess_V3` for main table auditing.
- **'UpdateUserPrivileges':** Updates an existing user privilege record. It audits the *previous* state of the main record and all detail records, updates the main record, deletes all *old* detail records, and then inserts the *new* set of detail records (parsed from comma-separated strings). Checks for username conflicts before updating. Uses `prcAuditProcess_V3` for main table auditing.
- It also unconditionally executes `SP_FormDataPridAddDivisionToUserPrivilege` at the start.
The procedure heavily relies on parsing comma-separated value strings for managing multi-value privilege assignments (e.g., multiple customers, job types). It includes a comprehensive auditing mechanism for modifications and deletions.


#### Database Entities Involved

This process interacts with the following database entities:

- FormDataPRIDAddressSetup (SELECT)
- FormDataPRIDCableCompanyCustomer (SELECT)
- FormDataPRIDUserPrivileges (SELECT/INSERT/UPDATE/DELETE)
- FormDataPRIDUserPrivilegesAssignFacility (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesAssignFacility_audit (INSERT)
- FormDataPRIDUserPrivilegesAuthAssignFacility (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesAuthAssignFacility_audit (INSERT)
- FormDataPRIDUserPrivilegesCustomer (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesCustomer_audit (INSERT)
- FormDataPRIDUserPrivilegesDefaultEquipmentType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultEquipmentType_audit (INSERT)
- FormDataPRIDUserPrivilegesDefaultJobRole (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultJobRole_audit (INSERT)
- FormDataPRIDUserPrivilegesDefaultJobStatus (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultJobType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultOperationArea (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultOperationArea_Audit (INSERT)
- FormDataPRIDUserPrivilegesDefaultServiceTypeCategory (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultServiceTypeCategory_Audit (INSERT)
- FormDataPRIDUserPrivilegesDefaultVehicleType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDefaultVehicleType_audit (INSERT)
- FormDataPRIDUserPrivilegesDivision (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesDivision_audit (INSERT)
- FormDataPRIDUserPrivilegesEquipmentType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesEquipmentType_audit (INSERT)
- FormDataPRIDUserPrivilegesJobRole (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesJobRole_audit (INSERT)
- FormDataPRIDUserPrivilegesJobStatus (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesJobStatus_audit (INSERT)
- FormDataPRIDUserPrivilegesJobType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesJobType_audit (INSERT)
- FormDataPRIDUserPrivilegesOperationArea (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesOperationArea_Audit (INSERT)
- FormDataPRIDUserPrivilegesPayStructure (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesPayStructure_audit (INSERT)
- FormDataPRIDUserPrivilegesServiceTypeCategory (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesServiceTypeCategory_Audit (INSERT)
- FormDataPRIDUserPrivilegesVehicleType (SELECT/INSERT/DELETE)
- FormDataPRIDUserPrivilegesVehicleType_audit (INSERT)
- FormDataPridMasterData (SELECT)
- SP_FormDataPridAddDivisionToUserPrivilege (EXECUTE)
- clientuser (SELECT)
- prcAuditProcess_V3 (EXECUTE)
- tempdb..##tblMaster (CREATE/DROP/SELECT/INSERT (Global Temporary))
- tempdb..##tblMasterFinal (CREATE/DROP/SELECT/INSERT (Global Temporary))
- tempdb..#tbl... (CREATE/DROP/SELECT/INSERT (Local Temporary))
- vw_FormDataPRIDUserPrivilegesJobStatus (SELECT)
- vw_FormDataPRIDUserPrivilegesJobType (SELECT)
- vw_ServiceTypeCategories (SELECT)

#### Process Inputs

The process accepts the following inputs:

| Procedure | Parameter | Type | Purpose |
|-----------|-----------|------|--------|
| SP_FormDataPRIDUserPrivilegesSetup | @value1 | varchar(500) | Controls the primary action (e.g., 'SelectUsers', 'InsertUserPrivileges', 'UpdateUserPrivileges', 'DeleteUserPrivileges', 'EditUserPrivileges', 'SelectJobType', etc.) |
| SP_FormDataPRIDUserPrivilegesSetup | @fdate | varchar(50) | Likely a 'from date' filter (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @tdate | varchar(50) | Likely a 'to date' filter (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @value2 | varchar(500) | Often used as the RecordId for update, delete, or edit operations |
| SP_FormDataPRIDUserPrivilegesSetup | @clientId | varchar(12) | Identifier for the client (often hardcoded or checked against 'OPRS') |
| SP_FormDataPRIDUserPrivilegesSetup | @useremail | varchar(100) | Email of the user performing the action (used for auditing and identification) |
| SP_FormDataPRIDUserPrivilegesSetup | @userfirstname | varchar(100) | First name of the user (used when inserting records) |
| SP_FormDataPRIDUserPrivilegesSetup | @userlastname | varchar(100) | Last name of the user (used when inserting records) |
| SP_FormDataPRIDUserPrivilegesSetup | @NameFirst | varchar(100) | Likely user's first name (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @NameLast | varchar(100) | Likely user's last name (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @email | varchar(200) | Likely user's email (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @FromNumber | int | Starting row number for pagination (used in 'SelectUsers') |
| SP_FormDataPRIDUserPrivilegesSetup | @ToNumber | int | Ending row number for pagination (used in 'SelectUsers') |
| SP_FormDataPRIDUserPrivilegesSetup | @SQLSortString | nvarchar(max) | Dynamic sorting criteria for 'SelectUsers' |
| SP_FormDataPRIDUserPrivilegesSetup | @SQLFilterString | nvarchar(max) | Dynamic filtering criteria for 'SelectUsers' |
| SP_FormDataPRIDUserPrivilegesSetup | @value3 | varchar(100) | Generic parameter (usage not apparent in provided code) |
| SP_FormDataPRIDUserPrivilegesSetup | @Username | varchar(100) | The username (often email or UserID) whose privileges are being set/updated |
| SP_FormDataPRIDUserPrivilegesSetup | @IsShowDispatchAndWithdraw | varchar(100) | Flag indicating a specific privilege (Dispatch/Withdraw visibility) |
| SP_FormDataPRIDUserPrivilegesSetup | @IsShowHold | varchar(100) | Flag indicating a specific privilege (Hold visibility) |
| SP_FormDataPRIDUserPrivilegesSetup | @isAssigningResources | varchar(100) | Flag indicating a specific privilege (Assigning resources) |
| SP_FormDataPRIDUserPrivilegesSetup | @customer | varchar(max) | Comma-separated list of Customer IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @jobtype | varchar(500) | Comma-separated list of Job Type IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @defaultdate | varchar(50) | Identifier for the default date setting |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultJobType | varchar(500) | Comma-separated list of Default Job Type IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @EditJobOnJobSummary | varchar(50) | Flag indicating privilege to edit jobs on Job Summary |
| SP_FormDataPRIDUserPrivilegesSetup | @EditJobOnAssignJob | varchar(50) | Flag indicating privilege to edit jobs on Assign Job |
| SP_FormDataPRIDUserPrivilegesSetup | @AllowRiskAssessment | varchar(50) | Flag indicating privilege to allow risk assessment |
| SP_FormDataPRIDUserPrivilegesSetup | @ApproveJobfunctionality | varchar(50) | Flag indicating privilege to approve jobs |
| SP_FormDataPRIDUserPrivilegesSetup | @ShowExceptionsOnJobSummary | varchar(50) | Flag indicating privilege to show exceptions on Job Summary |
| SP_FormDataPRIDUserPrivilegesSetup | @IsShowDocument | varchar(50) | Flag indicating privilege to show documents |
| SP_FormDataPRIDUserPrivilegesSetup | @AssignFacility | varchar(max) | Comma-separated list of Assignable Facility IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @AllowJobDeletion | varchar(50) | Flag indicating privilege to delete jobs |
| SP_FormDataPRIDUserPrivilegesSetup | @AllowChildJobDeletion | varchar(50) | Flag indicating privilege to delete child jobs |
| SP_FormDataPRIDUserPrivilegesSetup | @AllowToViewSensitiveDocs | varchar(50) | Flag indicating privilege to view sensitive documents |
| SP_FormDataPRIDUserPrivilegesSetup | @AllowFTIDeletion | varchar(50) | Flag indicating privilege to delete FTI (likely related data) |
| SP_FormDataPRIDUserPrivilegesSetup | @PayStructure | varchar(50) | Comma-separated list of allowed Pay Structures (e.g., 'Hourly', 'Salary') |
| SP_FormDataPRIDUserPrivilegesSetup | @DivisionId | varchar(500) | Comma-separated list of Division IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @IsAllDivision | bit | Flag indicating if user has access to all divisions |
| SP_FormDataPRIDUserPrivilegesSetup | @ServiceTypeCategory | varchar(max) | Comma-separated list of Service Type Category IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @OperationArea | varchar(max) | Comma-separated list of Operation Area IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultOperationArea | varchar(max) | Comma-separated list of Default Operation Area IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @AutoEmailerOnJobSummary | varchar(50) | Flag indicating privilege for auto-emailer on job summary |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultServiceTypeCategory | varchar(max) | Comma-separated list of Default Service Type Category IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @AuthAssignedFacility | varchar(max) | Comma-separated list of Authorized Assignable Facility IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @IsAllAuthServiceTypes | bit | Flag indicating if user has access to all authorized service types |
| SP_FormDataPRIDUserPrivilegesSetup | @IsTrimCableShop | varchar(50) | Flag indicating privilege related to Trim Cable Shop |
| SP_FormDataPRIDUserPrivilegesSetup | @IsAccurizeAugmentCableShop | varchar(50) | Flag indicating privilege related to Accurize/Augment Cable Shop |
| SP_FormDataPRIDUserPrivilegesSetup | @IsScrapCableShop | varchar(50) | Flag indicating privilege related to Scrap Cable Shop |
| SP_FormDataPRIDUserPrivilegesSetup | @IsShipperReceiverWorkOrderMaterialTransfer | varchar(50) | Flag indicating privilege related to Shipper/Receiver Work Order Material Transfer |
| SP_FormDataPRIDUserPrivilegesSetup | @IsShipInstallRemanentReturn | varchar(50) | Flag indicating privilege related to Ship Install Remanent Return |
| SP_FormDataPRIDUserPrivilegesSetup | @ISAllowToChangeJobStatus | bit | Flag indicating privilege to change job status |
| SP_FormDataPRIDUserPrivilegesSetup | @IsWithdrawSynchedInvoices | bit | Flag indicating privilege to withdraw synched invoices |
| SP_FormDataPRIDUserPrivilegesSetup | @TimeZone | int | Identifier for the user's timezone preference |
| SP_FormDataPRIDUserPrivilegesSetup | @jobstatus | varchar(max) | Comma-separated list of Job Status IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultJobStatus | varchar(max) | Comma-separated list of Default Job Status IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @JobRole | varchar(max) | Comma-separated list of Job Role IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultJobRole | varchar(max) | Comma-separated list of Default Job Role IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @VehicleType | varchar(max) | Comma-separated list of Vehicle Type IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultVehicleType | varchar(max) | Comma-separated list of Default Vehicle Type IDs |
| SP_FormDataPRIDUserPrivilegesSetup | @EquipmentType | varchar(max) | Comma-separated list of Equipment Type IDs for privilege assignment |
| SP_FormDataPRIDUserPrivilegesSetup | @DefaultEquipmentType | varchar(max) | Comma-separated list of Default Equipment Type IDs |

---

## Business Rules

*   **User Privilege Uniqueness:** A specific username (`@Username`, linked to `clientuser.UserID`) can only have one active privilege record within the client (`@clientId`). Checked during `InsertUserPrivileges` and `UpdateUserPrivileges`.
*   **Client Context:** All operations are performed within the context of a specific client (`@clientId`), often hardcoded or validated as 'OPRS'.
*   **Granular Access Control:** Privileges are highly specific, controlling visibility (`IsShow...`), edit rights (`IsEdit...`), deletion rights (`IsAllow...`), approval rights (`IsAllowedToApproveJobs`), and access to specific functional areas (Cable Shop flags, Shipper/Receiver flags).
*   **Data Scoping:** User access can be restricted to specific:
    *   Customers
    *   Job Types / Default Job Types
    *   Job Statuses / Default Job Statuses
    *   Operational Areas / Default Operational Areas
    *   Assignable Facilities / Authorized Assignable Facilities
    *   Divisions (or "All")
    *   Pay Structures
    *   Service Type Categories / Default Service Type Categories
    *   Job Roles / Default Job Roles
    *   Vehicle Types / Default Vehicle Types
    *   Equipment Types / Default Equipment Types
*   **"All" Access Representation:** The system uses specific logic (e.g., checking for value '0' or absence of records in detail tables) to represent access to "All" Customers, "All" Facilities, etc., when displaying aggregated data (`SelectUsers`, `EditUserPrivileges`).
*   **Mandatory Auditing:** Deletions and updates trigger the logging of the previous state into corresponding `_audit` tables.
*   **Default Settings:** Users have configurable default settings for date views, job types, operation areas, etc.

## Data Flow

*   **Input:** The procedure receives the action type (`@value1`), user identifiers (`@Username`, `@useremail`), client ID (`@clientId`), numerous boolean flags (`@Is...`), comma-separated lists of IDs (`@customer`, `@jobtype`, `@DivisionId`, etc.), and potentially pagination/filter/sort criteria (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`).
*   **Processing:**
    1.  **(Unconditional)** Executes `SP_FormDataPridAddDivisionToUserPrivilege`.
    2.  Based on `@value1`:
        *   **Lookups (`Select...`):** Reads from master/setup tables (`FormDataPridMasterData`, `FormDataPRIDAddressSetup`, etc.) usually filtered by `ClientId='OPRS'` and `flagactive=1`.
        *   **Create (`InsertUserPrivileges`):** Checks for username existence. Inserts a primary record into `FormDataPRIDUserPrivileges`. Parses comma-separated lists using `string_split` and inserts multiple records into various detail tables (e.g., `FormDataPRIDUserPrivilegesCustomer`, `FormDataPRIDUserPrivilegesJobType`, etc.) linking back via the new `PrivilegeID`.
        *   **Read List (`SelectUsers`):** Uses dynamic SQL to build a query selecting from `FormDataPRIDUserPrivileges`. Aggregates data from multiple detail tables using `STUFF` and `FOR XML PATH`. Applies filtering (`@SQLFilterString`) and sorting (`@SQLSortString`). Uses global temporary tables (`##tblMaster`, `##tblMasterFinal`) to handle pagination (`@FromNumber`, `@ToNumber`).
        *   **Read Single (`EditUserPrivileges`, `GetUserDetails`):** Selects a single record from `FormDataPRIDUserPrivileges` based on `@value2` (RecordId) or `@useremail`. May aggregate details using `STUFF/FOR XML PATH` similar to `SelectUsers`.
        *   **Update (`UpdateUserPrivileges`):**
            *   Audits: Inserts current state from detail tables into `_audit` tables. Calls `prcAuditProcess_V3` for the main table.
            *   Updates: Modifies the main record in `FormDataPRIDUserPrivileges`.
            *   Deletes: Removes *all* existing detail records associated with the `PrivilegeID` (`@value2`).
            *   Inserts: Parses *new* comma-separated lists and inserts new detail records (similar to Create).
        *   **Delete (`DeleteUserPrivileges`):**
            *   Audits: Inserts current state from detail tables into `_audit` tables. Calls `prcAuditProcess_V3` for the main table.
            *   Deletes: Removes records from all detail tables associated with the `PrivilegeID` (`@value2`). Deletes the main record from `FormDataPRIDUserPrivileges`.
*   **Output:** Returns result sets containing:
    *   Lists of reference data (for lookups).
    *   A paginated/filtered/sorted list of user privileges (`SelectUsers`) and a total count.
    *   Details of a single user's privileges (`EditUserPrivileges`, `GetUserDetails`).
    *   Status messages ('Saved', 'Present') or row counts (for Delete).

## Business Entities

*   **Core Entity:**
    *   `UserPrivilege`: Represents a specific configuration of permissions and settings for a user. (Mapped to `FormDataPRIDUserPrivileges` table).
*   **Primary Relationship:**
    *   `User` (from `clientuser` table) `1 <--> 1` `UserPrivilege` (within a specific ClientId). Linked via `UserName`/`UserID`.
*   **Supporting Entities & Relationships (1 UserPrivilege <--> * Many Detail Records):** The `UserPrivilege` entity has one-to-many relationships with numerous detail/linking tables, which in turn link to other     *   `UserPrivilege` `1 --> *` `UserPrivilegesCustomer` `* --> 1` `Customer` (`FormDataPRIDCableCompanyCustomer`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobType` `* --> 1` `JobType` (`FormDataPridMasterData` where `GroupCode='OperationTypeCategory'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobType` `* --> 1` `JobType` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobStatus` `* --> 1` `JobStatus` (`FormDataPridMasterData` where `GroupCode='JobStatus'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobStatus` `* --> 1` `JobStatus` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesAssignFacility` `* --> 1` `Facility` (`FormDataPRIDAddressSetup`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesAuthAssignFacility` `* --> 1` `Facility` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesPayStructure` (Contains 'Hourly'/'Salary')
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDivision` `* --> 1` `Division` (`FormDataPRIDAddressSetup`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesServiceTypeCategory` `* --> 1` `ServiceTypeCategory` (`FormDataPridMasterData` where `GroupCode='ServiceTypeCategory'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultServiceTypeCategory` `* --> 1` `ServiceTypeCategory` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesOperationArea` `* --> 1` `OperationArea` (`FormDataPridMasterData` where `GroupCode='Operational Area'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultOperationArea` `* --> 1` `OperationArea` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesJobRole` `* --> 1` `JobRole` (`FormDataPridMasterData` where `GroupCode='JobRole'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultJobRole` `* --> 1` `JobRole` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesVehicleType` `* --> 1` `VehicleType` (`FormDataPridMasterData` where `GroupCode='TruckTypeSetup'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultVehicleType` `* --> 1` `VehicleType` (...)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesEquipmentType` `* --> 1` `EquipmentType` (`FormDataPridMasterData` where `GroupCode='TrailerTypeSetup'`)
    *   `UserPrivilege` `1 --> *` `UserPrivilegesDefaultEquipmentType` `* --> 1` `EquipmentType` (...)
*   **Audit Entities:** Each primary and detail table has a corresponding `_audit` table (e.g., `FormDataPRIDUserPrivileges_audit`, `FormDataPRIDUserPrivilegesCustomer_audit`) storing historical versions of the records.

## Test Cases

The following test cases validate the business logic implemented in SP_FormDataPRIDUserPrivilegesSetup.

### User Privilege Management / Application Access Control Test Cases

#### UserPrivilegeManagement/ApplicationAccessControl_TC001: Verify successful creation of a new user privilege profile with multiple associated customers, job types, facilities, and roles.

**Priority**: High

**Preconditions**:
['The target username does not already exist in the system.', 'The specified customers, job types, facilities, and roles exist in the respective master data tables.', 'The user performing the action has the necessary permissions to create user privilege profiles.']

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Navigate to the User Privilege Management section and initiate the creation of a new user profile. | The system displays a form to enter user privilege details. |
| 2. Enter a unique username, user's full name, and select multiple items from the available lists for Customers, Job Types, Assign Facilities, and Job Roles (e.g., 2 customers, 3 job types, 2 facilities, 1 role). | The system accepts the input without validation errors. |
| 3. Submit the form to save the new user privilege profile. | The system confirms successful creation of the user profile without errors. |
| 4. Search for the newly created user in the user list view. | The user appears in the list, and the summary view correctly shows the number or names of associated customers, job types, facilities, and roles assigned during creation. |
| 5. View the details of the newly created user profile. | All entered information, including the multiple selected customers, job types, facilities, and roles, are accurately displayed. |

**Expected Final Result**:
A new user privilege profile is successfully created with all specified associations correctly stored and reflected in the system views.

---

#### UserPrivilegeManagement/ApplicationAccessControl_TC002: Verify updating an existing user's privileges by adding/removing associated entities (e.g., customer, job type) and changing a primary setting (e.g., Pay Structure).

**Priority**: High

**Preconditions**:
["An existing user privilege profile exists (e.g., 'TestUser01') with specific initial assignments (e.g., Customer A, Job Type X, Pay Structure P1).", 'Additional master data exists to facilitate changes (e.g., Customer B, Job Type Y, Pay Structure P2).', 'The user performing the action has the necessary permissions to edit user privilege profiles.']

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Navigate to the User Privilege Management section and locate the existing user profile ('TestUser01'). | The user profile 'TestUser01' is found and accessible for editing. |
| 2. Initiate the edit process for 'TestUser01'. | The system displays the user's current privilege details in an editable form. |
| 3. Modify the associations: Add 'Customer B' to the assigned customers list, remove 'Job Type X' from the assigned job types list, and change the 'Pay Structure' selection from P1 to P2. | The system allows the modifications in the form. |
| 4. Submit the changes to update the user privilege profile. | The system confirms the successful update without errors. |
| 5. View the details of the updated user profile ('TestUser01'). | The profile now shows 'Customer A' and 'Customer B' assigned, 'Job Type X' is no longer listed as assigned, and the 'Pay Structure' is displayed as P2. The system correctly reflects the additions, removals, and changes. |
| 6. (Conceptual) Verify that the changes were logged in the system's audit trail. | An audit record exists indicating that 'TestUser01' was updated, capturing the state before the changes were applied (specifically showing Customer A, Job Type X, Pay Structure P1 as previous values for the modified fields/associations). |

**Expected Final Result**:
The user's privileges are successfully updated, reflecting the specified additions, removals, and changes. The update action, including the previous state of the modified data, is logged for auditing purposes.

---

#### UserPrivilegeManagement/ApplicationAccessControl_TC003: Verify successful deletion of a user privilege profile and confirm associated detail records are removed and the deletion is audited.

**Priority**: High

**Preconditions**:
["An existing user privilege profile exists (e.g., 'ToDeleteUser') with multiple associated details (customers, job types, facilities, roles, etc.).", 'The user performing the action has the necessary permissions to delete user privilege profiles.']

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Navigate to the User Privilege Management section and locate the user profile 'ToDeleteUser'. | The user profile 'ToDeleteUser' is found. |
| 2. Initiate the deletion process for 'ToDeleteUser'. | The system prompts for confirmation before proceeding with the deletion. |
| 3. Confirm the deletion. | The system confirms successful deletion without errors. |
| 4. Attempt to search for the deleted user ('ToDeleteUser') in the user list view. | The user 'ToDeleteUser' is no longer found in the list of active user privilege profiles. |
| 5. Attempt to retrieve the details of the deleted user ('ToDeleteUser') via any direct access method (if applicable). | The system indicates that the user profile does not exist or cannot be found. |
| 6. (Conceptual) Verify that the deletion was logged in the system's audit trail. | An audit record exists indicating that the user profile 'ToDeleteUser' and all its associated privilege details (customers, job types, etc.) were deleted, logging the data that was removed. |

**Expected Final Result**:
The user privilege profile 'ToDeleteUser' is completely removed from the active system, access related to this profile is effectively revoked, and the deletion event along with the removed data is recorded in the audit trail.

---

#### UserPrivilegeManagement/ApplicationAccessControl_TC004: Verify that the user list view correctly displays aggregated privilege details and supports filtering based on assigned entities (e.g., Customer).

**Priority**: Medium

**Preconditions**:
[{'At least three user privilege profiles exist': [{'User A': "Assigned Customer 'CUST001', Role 'ROLE_A'."}, {'User B': "Assigned Customers 'CUST001', 'CUST002', Role 'ROLE_B'."}, {'User C': "Assigned Customer 'CUST003', Role 'ROLE_A'."}]}, 'The user performing the action has permissions to view the user privilege list.']

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Navigate to the User Privilege Management section displaying the list of users. | A list/grid appears showing User A, User B, and User C along with other users. |
| 2. Observe the displayed information for User B in the list view. | The list correctly aggregates and displays User B's assigned customers (e.g., shows 'CUST001, CUST002' or similar representation indicating multiple customers). |
| 3. Apply a filter to the list, specifying 'CUST001' as the Customer criteria. | The list updates to show only User A and User B. User C is no longer visible in the filtered list. |
| 4. Clear the previous filter and apply a new filter, specifying 'ROLE_A' as the Role criteria. | The list updates to show only User A and User C. User B is no longer visible in the filtered list. |

**Expected Final Result**:
The user privilege list view accurately displays aggregated association data (like multiple customers) and correctly filters the user list based on specified criteria related to assigned privileges.

---

#### UserPrivilegeManagement/ApplicationAccessControl_TC005: Verify that attempting to create a new user privilege profile with a username that already exists is prevented.

**Priority**: High

**Preconditions**:
["An existing user privilege profile exists with the username 'ExistingUser'.", 'The user performing the action has the necessary permissions to create user privilege profiles.']

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Navigate to the User Privilege Management section and initiate the creation of a new user profile. | The system displays a form to enter user privilege details. |
| 2. Enter 'ExistingUser' as the username, along with other required details (full name, some selections for customers/roles etc.). | The system accepts the input initially. |
| 3. Submit the form to save the new user privilege profile. | The system prevents the creation and displays a clear error message indicating that the username 'ExistingUser' already exists. |
| 4. Check the user list view. | No new user profile with the username 'ExistingUser' has been created. The original 'ExistingUser' profile remains unchanged. |

**Expected Final Result**:
The system successfully prevents the creation of a duplicate user privilege profile based on the username, ensuring username uniqueness.

---

