# SP_formdataPRIDDispatcherMaster Business Logic Analysis

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Domains and Relationships](#business-domains-and-relationships)
3. [Business Processes](#business-processes)
   1. [Management of PRID Dispatcher Master data, including creation, retrieval, updating, deletion (soft), and lookup of associated cable companies. Supports data presentation with pagination, sorting, and filtering.](#management-of-prid-dispatcher-master-data,-including-creation,-retrieval,-updating,-deletion-(soft),-and-lookup-of-associated-cable-companies.-supports-data-presentation-with-pagination,-sorting,-and-filtering.)
4. [Business Rules](#business-rules)
5. [Data Flow](#data-flow)
6. [Business Entities](#business-entities)
7. [Test Cases](#test-cases)
   1. [Management of PRID Dispatcher Master data, including creation, retrieval, updating, deletion (soft), and lookup of associated cable companies. Supports data presentation with pagination, sorting, and filtering. Test Cases](#test-cases-management-of-prid-dispatcher-master-data,-including-creation,-retrieval,-updating,-deletion-(soft),-and-lookup-of-associated-cable-companies.-supports-data-presentation-with-pagination,-sorting,-and-filtering.)

## Executive Summary

Okay, here is a focused analysis of the business logic implemented in the `SP_formdataPRIDDispatcherMaster` stored procedure based on the provided information.

## Business Logic Analysis: SP_formdataPRIDDispatcherMaster

### 1. High-Level Overview

This stored procedure serves as a central hub for managing **PRID Dispatcher Master** records within the system. It encapsulates the core data operations (CRUD - Create, Read, Update, Delete) and related lookups. It acts as a multi-functional endpoint controlled by the `@value1` parameter, handling data retrieval for display (with features like pagination, sorting, filtering), data entry, modification, logical deletion (soft delete), and providing lookup data for associated entities like Cable Companies.

### 2. Business Domains

Based on the procedure's name, tables, and parameters, the business domains involved are:

*   **Master Data Management:** Specifically managing a core list of Dispatcher personnel or contacts.
*   **Contact Management:** Storing and managing contact details (First Name, Last Name, Email) for dispatchers.
*   **Operations Support / Service Management:** The term "Dispatcher" and association with "Cable Company" suggests a role in coordinating field services, requests, or projects (potentially related to "PRID" - Project/Procurement Request ID).
*   **Client Data Scoping:** The consistent use of `@clientId` indicates a multi-tenant or client-specific data management environment.

### 3. Key Business Processes Implemented

*   **Dispatcher Master Data Creation:** Adding new dispatcher records to the system, ensuring they are unique based on specific criteria.
*   **Dispatcher Master Data Retrieval (List View):** Fetching a list of active dispatchers, potentially filtered and sorted, for display in grids or lists, including pagination support. This process involves joining with Cable Company data for display purposes.
*   **Dispatcher Master Data Retrieval (Single View):** Fetching the complete details of a single dispatcher record, typically for editing purposes.
*   **Dispatcher Master Data Modification:** Updating the details of an existing dispatcher record.
*   **Dispatcher Master Data Deactivation (Soft Delete):** Marking a dispatcher record as inactive (`FlagActive=0`) rather than physically deleting it, preserving historical data and relationships.
*   **Cable Company Lookup:** Providing a list of available Cable Companies (likely for selection in a dropdown menu when creating or editing a dispatcher).
*   **Auditing:** Recording changes (Updates, Deletes) made to dispatcher records via the `prcAuditProcess_V3` procedure.

### 4. Business Rules Enforced

*   **Uniqueness Constraint:** A dispatcher record is considered unique based on the combination of `CableCompany`, `FirstName`, `LastName`, `OthercompanyName`, `Email`, and `ClientID`. The procedure prevents the creation ('Insert') or update ('Update') of records that would violate this uniqueness rule (returning 'Duplicate').
*   **Active Record Management:** Operations like standard selection ('Select') and editing ('Edit') primarily target active records (`FlagActive=1`).
*   **Soft Deletion:** Records are not physically deleted. Instead, they are marked as inactive, enforcing data retention policies.
*   **Data Scoping by Client:** All primary operations (Insert, Update, Delete, Edit, SelectCompany) are scoped by the `@clientId`, ensuring data isolation between clients.
*   **Audit Trail Requirement:** Updates and deletions must be logged through an auditing mechanism (`prcAuditProcess_V3`).
*   **Cable Company Association:** Dispatchers are associated with a Cable Company record (via `cablecompany` referencing `FormDataPRIDCableCompanyCustomer.recordid`).

### 5. Data Flow

1.  **Input:** The procedure receives control parameters (`@value1`, `@recordId`, `@clientId`), user information (`@userEmail`, `@userfirstName`, `@userLastName`), dispatcher data (`@cablecompany`, `@firstname`, `@lastname`, `@OthercompanyName`, `@email`), and presentation parameters (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`).
2.  **Processing:**
    *   The `@value1` parameter directs the execution flow to the appropriate logic block (Select, Insert, Update, Delete, Edit, SelectCompany).
    *   **Read Operations ('Select', 'Edit', 'SelectCompany'):** Data is queried from `FormDataPRIDDispatcherMaster` and potentially joined with `FormDataPRIDCableCompanyCustomer`. For 'Select', dynamic SQL is used with temporary tables (`##tblcustomers`, `##tblcustomersFinal`) to handle sorting, filtering, and pagination.
    *   **Write Operations ('Insert', 'Update', 'Delete'):**
        *   Duplicate checks are performed by querying `FormDataPRIDDispatcherMaster`.
        *   If checks pass (or are not required), data is inserted (`INSERT`) or updated (`UPDATE`) in `FormDataPRIDDispatcherMaster`.
        *   For 'Update' and 'Delete', the `prcAuditProcess_V3` procedure is called *before* the modification.
        *   'Delete' performs an `UPDATE` to set `FlagActive=0`.
3.  **Output:**
    *   **'Select':** Returns a result set containing the requested page of dispatcher data and another result set with the total count of filtered records.
    *   **'Insert', 'Update', 'Delete':** Returns the `@@ROWCOUNT` (number of affected rows) on success or the string 'Duplicate' on failure due to uniqueness constraints. *(Note: The 'Delete' ELSE block has potentially erroneous logic returning nothing specific after `update... set completetime='a'`).*
    *   **'Edit':** Returns a single row result set with the details of the specified dispatcher.
    *   **'SelectCompany':** Returns a result set containing the ID (`companyid`) and Name (`CableCompanyCustomerName`) of relevant cable companies.

### 6. Business Entities and Relationships

*   **Dispatcher:** (Represented by `FormDataPRIDDispatcherMaster`) The primary entity managed by this procedure. Attributes include `FirstName`, `LastName`, `Email`, `OthercompanyName`, `FlagActive`.
*   **Cable Company:** (Represented by `FormDataPRIDCableCompanyCustomer`) An entity associated with the Dispatcher. Attributes include `CableCompanyCustomerName`.
*   **Client:** An implicit entity defining the data scope/tenant (identified by `@clientId`).
*   **User:** The actor performing the data management operations (identified by `@userEmail`, etc.).

**Relationships:**

*   A `Dispatcher` *is associated with* one `Cable Company` (via the `FormDataPRIDDispatcherMaster.cablecompany` field linking to `FormDataPRIDCableCompanyCustomer.recordid`). This is a one-to-many relationship from the perspective of the Cable Company (one Cable Company can have many Dispatchers).
*   `Dispatcher` data *belongs to* a `Client`.
*   Data modifications on `Dispatcher` records are *audited against* the `User` performing the action.

## Business Domains and Relationships

Based on the procedure's name, tables, and parameters, the 
*   **Master Data Management:** Specifically managing a core list of Dispatcher personnel or contacts.
*   **Contact Management:** Storing and managing contact details (First Name, Last Name, Email) for dispatchers.
*   **Operations Support / Service Management:** The term "Dispatcher" and association with "Cable Company" suggests a role in coordinating field services, requests, or projects (potentially related to "PRID" - Project/Procurement Request ID).
*   **Client Data Scoping:** The consistent use of `@clientId` indicates a multi-tenant or client-specific data management environment.

## Business Processes

This section details the key business processes implemented in SP_formdataPRIDDispatcherMaster.

### Management of PRID Dispatcher Master data, including creation, retrieval, updating, deletion (soft), and lookup of associated cable companies. Supports data presentation with pagination, sorting, and filtering.

#### Process Overview

*Management of PRID Dispatcher Master data, including creation, retrieval, updating, deletion (soft), and lookup of associated cable companies. Supports data presentation with pagination, sorting, and filtering.* process handles the following business functions:

- **SP_formdataPRIDDispatcherMaster**: This stored procedure acts as a CRUD (Create, Read, Update, Delete) and selection handler for 'PRID Dispatcher Master' data. It uses the @value1 parameter to determine the action:
- 'Select': Retrieves a paginated, sorted, and filtered list of active dispatchers, joining with cable company customer information. Uses dynamic SQL and temporary tables (##tblcustomers, ##tblcustomersFinal). Returns the selected page of data and the total count.
- 'Insert': Inserts a new dispatcher record after checking for duplicates based on CableCompany, FirstName, LastName, OtherCompanyName, Email, and ClientID. Returns the row count or 'Duplicate'.
- 'Update': Updates an existing dispatcher record identified by @recordId after checking for potential duplicates with the new values (excluding the current record). Calls an audit procedure (prcAuditProcess_V3) before updating. Returns the row count or 'Duplicate'.
- 'Delete': Performs a soft delete by setting the FlagActive flag to 0 for the dispatcher record identified by @recordId and @clientId. Calls an audit procedure (prcAuditProcess_V3) before updating. Returns the row count. *Note: The ELSE block contains a potentially erroneous update (`Set completetime='a'`).*
- 'Edit': Retrieves the details of a single active dispatcher record identified by @recordId for editing purposes, joining with cable company customer information.
- 'SelectCompany': Retrieves a list of active cable company customers (ID and Name) associated with the given @clientId, potentially including a specific inactive one if its ID matches @recordId. Used for populating dropdowns or lookups.


#### Database Entities Involved

This process interacts with the following database entities:

- ##tblcustomers (INSERT (Temporary table for 'Select'))
- ##tblcustomersFinal (INSERT, SELECT (Temporary table for 'Select'))
- Calls procedure prcAuditProcess_V3 (EXECUTE)
- FormDataPRIDCableCompanyCustomer (SELECT)
- FormDataPRIDDispatcherMaster (SELECT, INSERT, UPDATE (including soft DELETE))

#### Process Inputs

The process accepts the following inputs:

| Procedure | Parameter | Type | Purpose |
|-----------|-----------|------|--------|
| SP_formdataPRIDDispatcherMaster | @value1 | varchar(50) | Control parameter to specify the operation (Select, Insert, Update, Delete, Edit, SelectCompany). |
| SP_formdataPRIDDispatcherMaster | @recordId | nvarchar(10) | Unique identifier for the dispatcher record (used in Update, Delete, Edit, SelectCompany). |
| SP_formdataPRIDDispatcherMaster | @FormCode | nvarchar(50) | Identifier for the form associated with the data (used in Insert). |
| SP_formdataPRIDDispatcherMaster | @userEmail | NVARCHAR(200) | Email of the user performing the action (used for auditing and tracking). |
| SP_formdataPRIDDispatcherMaster | @userfirstName | NVARCHAR(200) | First name of the user performing the action (used in Insert). |
| SP_formdataPRIDDispatcherMaster | @userLastName | NVARCHAR(200) | Last name of the user performing the action (used in Insert). |
| SP_formdataPRIDDispatcherMaster | @clientId | nvarchar(100) | Identifier for the client, used for data scoping and filtering. |
| SP_formdataPRIDDispatcherMaster | @cablecompany | nvarchar(max) | Identifier (likely recordid from FormDataPRIDCableCompanyCustomer) or potentially name of the associated cable company. |
| SP_formdataPRIDDispatcherMaster | @firstname | nvarchar(max) | First name of the dispatcher. |
| SP_formdataPRIDDispatcherMaster | @lastname | nvarchar(max) | Last name of the dispatcher. |
| SP_formdataPRIDDispatcherMaster | @OthercompanyName | nvarchar(max) | Name of another associated company. |
| SP_formdataPRIDDispatcherMaster | @email | nvarchar(max) | Email address of the dispatcher. |
| SP_formdataPRIDDispatcherMaster | @FromNumber | int | Starting row number for pagination (used in 'Select'). |
| SP_formdataPRIDDispatcherMaster | @ToNumber | int | Ending row number for pagination (used in 'Select'). |
| SP_formdataPRIDDispatcherMaster | @SQLSortString | nvarchar(max) | Dynamic sorting criteria string (used in 'Select'). |
| SP_formdataPRIDDispatcherMaster | @SQLFilterString | nvarchar(max) | Dynamic filtering criteria string (used in 'Select'). |

---

## Business Rules

*   **Uniqueness Constraint:** A dispatcher record is considered unique based on the combination of `CableCompany`, `FirstName`, `LastName`, `OthercompanyName`, `Email`, and `ClientID`. The procedure prevents the creation ('Insert') or update ('Update') of records that would violate this uniqueness rule (returning 'Duplicate').
*   **Active Record Management:** Operations like standard selection ('Select') and editing ('Edit') primarily target active records (`FlagActive=1`).
*   **Soft Deletion:** Records are not physically deleted. Instead, they are marked as inactive, enforcing data retention policies.
*   **Data Scoping by Client:** All primary operations (Insert, Update, Delete, Edit, SelectCompany) are scoped by the `@clientId`, ensuring data isolation between clients.
*   **Audit Trail Requirement:** Updates and deletions must be logged through an auditing mechanism (`prcAuditProcess_V3`).
*   **Cable Company Association:** Dispatchers are associated with a Cable Company record (via `cablecompany` referencing `FormDataPRIDCableCompanyCustomer.recordid`).

## Data Flow

1.  **Input:** The procedure receives control parameters (`@value1`, `@recordId`, `@clientId`), user information (`@userEmail`, `@userfirstName`, `@userLastName`), dispatcher data (`@cablecompany`, `@firstname`, `@lastname`, `@OthercompanyName`, `@email`), and presentation parameters (`@FromNumber`, `@ToNumber`, `@SQLSortString`, `@SQLFilterString`).
2.  **Processing:**
    *   The `@value1` parameter directs the execution flow to the appropriate logic block (Select, Insert, Update, Delete, Edit, SelectCompany).
    *   **Read Operations ('Select', 'Edit', 'SelectCompany'):** Data is queried from `FormDataPRIDDispatcherMaster` and potentially joined with `FormDataPRIDCableCompanyCustomer`. For 'Select', dynamic SQL is used with temporary tables (`##tblcustomers`, `##tblcustomersFinal`) to handle sorting, filtering, and pagination.
    *   **Write Operations ('Insert', 'Update', 'Delete'):**
        *   Duplicate checks are performed by querying `FormDataPRIDDispatcherMaster`.
        *   If checks pass (or are not required), data is inserted (`INSERT`) or updated (`UPDATE`) in `FormDataPRIDDispatcherMaster`.
        *   For 'Update' and 'Delete', the `prcAuditProcess_V3` procedure is called *before* the modification.
        *   'Delete' performs an `UPDATE` to set `FlagActive=0`.
3.  **Output:**
    *   **'Select':** Returns a result set containing the requested page of dispatcher data and another result set with the total count of filtered records.
    *   **'Insert', 'Update', 'Delete':** Returns the `@@ROWCOUNT` (number of affected rows) on success or the string 'Duplicate' on failure due to uniqueness constraints. *(Note: The 'Delete' ELSE block has potentially erroneous logic returning nothing specific after `update... set completetime='a'`).*
    *   **'Edit':** Returns a single row result set with the details of the specified dispatcher.
    *   **'SelectCompany':** Returns a result set containing the ID (`companyid`) and Name (`CableCompanyCustomerName`) of relevant cable companies.

## Business Entities

*   **Dispatcher:** (Represented by `FormDataPRIDDispatcherMaster`) The primary entity managed by this procedure. Attributes include `FirstName`, `LastName`, `Email`, `OthercompanyName`, `FlagActive`.
*   **Cable Company:** (Represented by `FormDataPRIDCableCompanyCustomer`) An entity associated with the Dispatcher. Attributes include `CableCompanyCustomerName`.
*   **Client:** An implicit entity defining the data scope/tenant (identified by `@clientId`).
*   **User:** The actor performing the data management operations (identified by `@userEmail`, etc.).

**Relationships:**

*   A `Dispatcher` *is associated with* one `Cable Company` (via the `FormDataPRIDDispatcherMaster.cablecompany` field linking to `FormDataPRIDCableCompanyCustomer.recordid`). This is a one-to-many relationship from the perspective of the Cable Company (one Cable Company can have many Dispatchers).
*   `Dispatcher` data *belongs to* a `Client`.
*   Data modifications on `Dispatcher` records are *audited against* the `User` performing the action.

## Test Cases

The following test cases validate the business logic implemented in SP_formdataPRIDDispatcherMaster.

### Management of PRID Dispatcher Master data, including creation, retrieval, updating, deletion (soft), and lookup of associated cable companies. Supports data presentation with pagination, sorting, and filtering. Test Cases

#### ManagementofPRIDDispatcherMasterdata,includingcreation,retrieval,updating,deletion(soft),andlookupofassociatedcablecompanies.Supportsdatapresentationwithpagination,sorting,andfiltering._TC001: Verify successful creation of a unique PRID Dispatcher and its retrieval in the active list.

**Priority**: High

**Preconditions**:
["A ClientID (e.g., 'Client123') exists.", "An active Cable Company Customer record exists for ClientID 'Client123' (e.g., CableCompanyID 50, Name 'Cable Co Alpha').", {"No active or inactive dispatcher exists for ClientID 'Client123' with the combination": "CableCompanyID=50, FirstName='John', LastName='Doe', OtherCompanyName='', Email='john.doe@test.com'."}]

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Execute SP_formdataPRIDDispatcherMaster with @value1='Insert', providing ClientID='Client123', CableCompanyID=50, FirstName='John', LastName='Doe', OtherCompanyName='', Email='john.doe@test.com', and other required non-identifying fields. | The stored procedure returns a success indicator (e.g., row count '1'). |
| 2. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client123', PageNumber=1, PageSize=10, SortColumn='FirstName', SortDirection='ASC', and filter criteria matching FirstName='John' and LastName='Doe'. | The stored procedure returns a list containing the newly created dispatcher 'John Doe' associated with 'Cable Co Alpha'. The record's FlagActive status should indicate it is active. The total record count returned should reflect at least 1 matching record. |

**Expected Final Result**:
A new PRID Dispatcher record is successfully created, marked as active, associated with the correct cable company, and can be retrieved via the 'Select' operation for active records.

---

#### ManagementofPRIDDispatcherMasterdata,includingcreation,retrieval,updating,deletion(soft),andlookupofassociatedcablecompanies.Supportsdatapresentationwithpagination,sorting,andfiltering._TC002: Verify that creating a PRID Dispatcher with duplicate identifying information (CableCompany, FirstName, LastName, OtherCompanyName, Email, ClientID) is prevented.

**Priority**: High

**Preconditions**:
["A ClientID (e.g., 'Client456') exists.", "An active Cable Company Customer record exists for ClientID 'Client456' (e.g., CableCompanyID 60, Name 'Cable Co Beta').", "An active dispatcher record already exists for ClientID 'Client456' with CableCompanyID=60, FirstName='Jane', LastName='Smith', OtherCompanyName='Beta Dispatch', Email='jane.smith@test.com'."]

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Execute SP_formdataPRIDDispatcherMaster with @value1='Insert', providing ClientID='Client456', CableCompanyID=60, FirstName='Jane', LastName='Smith', OtherCompanyName='Beta Dispatch', Email='jane.smith@test.com'. | The stored procedure returns the specific indicator 'Duplicate'. |
| 2. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client456', PageNumber=1, PageSize=10, and filter criteria matching FirstName='Jane' and LastName='Smith'. | The stored procedure returns only the single, original dispatcher record for 'Jane Smith'. No new record was created. |

**Expected Final Result**:
The system correctly prevents the creation of a duplicate dispatcher record based on the specified unique combination of fields and returns a 'Duplicate' status.

---

#### ManagementofPRIDDispatcherMasterdata,includingcreation,retrieval,updating,deletion(soft),andlookupofassociatedcablecompanies.Supportsdatapresentationwithpagination,sorting,andfiltering._TC003: Verify retrieval of active dispatchers with pagination, sorting (descending by LastName), and filtering (by Cable Company Name).

**Priority**: High

**Preconditions**:
["A ClientID (e.g., 'Client789') exists.", {"At least three active dispatcher records exist for ClientID 'Client789', all associated with the same active Cable Company (e.g., CableCompanyID 70, Name 'Cable Co Gamma')": [{'Dispatcher 1': "FirstName='Alice', LastName='Williams'"}, {'Dispatcher 2': "FirstName='Bob', LastName='Taylor'"}, {'Dispatcher 3': "FirstName='Charlie', LastName='Miller'"}]}, "Other active dispatchers associated with different cable companies may exist for ClientID 'Client789'."]

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client789', PageNumber=1, PageSize=2, SortColumn='LastName', SortDirection='DESC', and a filter for Cable Company Name = 'Cable Co Gamma'. | The stored procedure returns 2 records: 'Alice Williams' and 'Bob Taylor' (sorted Z-A by LastName). The total record count returned should be 3. |
| 2. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client789', PageNumber=2, PageSize=2, SortColumn='LastName', SortDirection='DESC', and the same filter for Cable Company Name = 'Cable Co Gamma'. | The stored procedure returns 1 record: 'Charlie Miller'. The total record count returned should still be 3. |
| 3. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client789', PageNumber=1, PageSize=10, SortColumn='LastName', SortDirection='DESC', and no filter for Cable Company Name. | The stored procedure returns a list potentially including dispatchers from other cable companies, still sorted by LastName descending, and the total count reflects all active dispatchers for Client789. |

**Expected Final Result**:
The 'Select' operation correctly filters dispatchers by Cable Company Name, sorts them according to the specified column and direction, and implements pagination accurately, returning the correct subset of records and the total count for the filtered set.

---

#### ManagementofPRIDDispatcherMasterdata,includingcreation,retrieval,updating,deletion(soft),andlookupofassociatedcablecompanies.Supportsdatapresentationwithpagination,sorting,andfiltering._TC004: Verify soft deletion of a dispatcher record and ensure it is excluded from subsequent active searches and 'Edit' retrieval.

**Priority**: High

**Preconditions**:
["A ClientID (e.g., 'Client101') exists.", "An active dispatcher record exists for ClientID 'Client101' with a known recordId (e.g., 999) and details (e.g., FirstName='Mark', LastName='Davis')."]

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Execute SP_formdataPRIDDispatcherMaster with @value1='Delete', providing ClientID='Client101' and recordId=999. | The stored procedure returns a success indicator (e.g., row count '1'). The audit procedure (prcAuditProcess_V3) is expected to have been called before the update. |
| 2. Execute SP_formdataPRIDDispatcherMaster with @value1='Select', ClientID='Client101', PageNumber=1, PageSize=10, and filter criteria matching FirstName='Mark' and LastName='Davis'. | The stored procedure returns a list that *does not* include the dispatcher 'Mark Davis' (recordId 999). The total record count reflects only the remaining active dispatchers matching the filter (if any). |
| 3. Execute SP_formdataPRIDDispatcherMaster with @value1='Edit', providing recordId=999. | The stored procedure does not return any dispatcher details, as the 'Edit' operation retrieves only active records. |

**Expected Final Result**:
The dispatcher record is successfully marked as inactive (soft-deleted), is no longer retrieved by the 'Select' operation for active records, and cannot be retrieved for editing via the 'Edit' operation.

---

#### ManagementofPRIDDispatcherMasterdata,includingcreation,retrieval,updating,deletion(soft),andlookupofassociatedcablecompanies.Supportsdatapresentationwithpagination,sorting,andfiltering._TC005: Verify that the 'SelectCompany' action retrieves active cable companies for a client, plus a specific inactive one if its ID is provided.

**Priority**: Medium

**Preconditions**:
["A ClientID (e.g., 'Client202') exists.", {"Cable Company 'Active East' (ID": "80) exists for ClientID 'Client202' and is active."}, {"Cable Company 'Active West' (ID": "81) exists for ClientID 'Client202' and is active."}, {"Cable Company 'Inactive North' (ID": "82) exists for ClientID 'Client202' but is *inactive*."}, "A dispatcher might or might not be currently associated with 'Inactive North'."]

**Test Steps**:

| Step | Expected Result |
|------|----------------|
| 1. Execute SP_formdataPRIDDispatcherMaster with @value1='SelectCompany', ClientID='Client202', and recordId=82 (the ID of the inactive company). | The stored procedure returns a list containing 'Active East' (ID: 80), 'Active West' (ID: 81), and 'Inactive North' (ID: 82). |
| 2. Execute SP_formdataPRIDDispatcherMaster with @value1='SelectCompany', ClientID='Client202', and recordId=0 (or any ID other than 82). | The stored procedure returns a list containing only the active companies: 'Active East' (ID: 80) and 'Active West' (ID: 81). 'Inactive North' is not included. |

**Expected Final Result**:
The 'SelectCompany' lookup correctly retrieves all active cable companies for the client and conditionally includes a specific inactive company only when its ID is passed via the recordId parameter, suitable for populating dropdowns that need to show a previously assigned but now inactive company.

---

