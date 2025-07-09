
##  Test User Accounts

### Staff – Engineering
```json
{
  "email": "cristiano.ronaldo@cr7.com",
  "password": "Password123!"
}
```

### Staff – Research
```json
{
  "email": "burna.boy@example.com",
  "password": "afrobeatKing2024"
}
```

### Staff – Sales
```json
{
  "email": "antoine.griezmann@example.com",
  "password": "anotherPass789"
}
```

---

### Manager – Engineering
```json
{
  "email": "messi.leo@goat.com",
  "password": "MessiRocks10!"
}
```

---

### Admin 
```json
{
  "email": "serena.williams@tennis.com",
  "password": "SerenaPower23!"
}
```

---



# 1. Authentication API Documentation

## Namespace: `authentication`

This namespace handles authentication-related operations including registration, login, logout, and checking API status.

---

### `GET /authentication/home`

**Description:** Home endpoint for authenticated users.

**Authentication Required:** Yes (JWT)

**Response:**
- 200 OK: `{ "message": "API is working!" }`

---

### `POST /authentication/register`

**Description:** Registers a new user.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_no": "1234567890",
  "gender": "Male",
  "address": "123 Street",
  "country": "Country"
}
```

**Responses:**
- 201 Created: `{ "message": "User registered successfully" }`
- 400 Bad Request: `{ "message": "User already exists" }`

---

### `POST /authentication/login`

**Description:** Logs in a user and returns a JWT token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Responses:**
- 200 OK:
```json
{
  "access_token": "JWT_TOKEN_HERE"
}
```
- 401 Unauthorized: `{ "message": "Invalid email or password" }`
- 403 Forbidden: `{ "message": "Access forbidden: Your account has been terminated" }`

---

### `POST /authentication/logout`

**Description:** Logs out the user by invalidating the JWT token.

**Authentication Required:** Yes (JWT)

**Responses:**
- 200 OK: `{ "msg": "Successfully logged out" }`




# 2. Attendance Management API Documentation

**Base URL**: `/api/attendance`  
**Authentication**: JWT Bearer Token (`Authorization: Bearer <token>`)

---

## Endpoints

### GET `/status`
Get the clock-in status of the current user.

**Access**: Staff, Manager, Admin  
**Response**:
```json
{ "status": "not_clocked_in" | "clocked_in" | "clocked_out" }
```

---

### POST `/clock-in`
Clock in for the current user.

**Access**: Staff, Manager, Admin  
**Response**:
```json
{ "message": "Clock-in successful" }
```
**Errors**:
```json
{ "message": "Already clocked in today." }
```

---

### POST `/clock-out`
Clock out for the current user.

**Access**: Staff, Manager, Admin  
**Response**:
```json
{ "message": "Clock-out successful" }
```
**Errors**:
```json
{ "message": "Cannot clock out. Either not clocked in or already clocked out." }
```

---

### GET `/my-attendance`
Get attendance history for the current user.

**Access**: Staff, Manager, Admin  
**Query Parameters** _(optional)_:
- `year`: integer (e.g., 2025)
- `month`: integer (1–12)
- `day`: integer (1–31)

**Response**:
```json
[
  {
    "id": 1,
    "employee_id": 123,
    "date": "2025-07-08",
    "clock_in_time": "08:15:00",
    "clock_out_time": "17:00:00",
    "total_hours": 8.75,
    "status": "Present"
  }
]
```

---

### GET `/department-attendance`
Get attendance for employees in the manager's department.

**Access**: Manager only  
**Query Parameters** _(optional)_:
- `year`, `month`, `day`

**Response**: Same as `/my-attendance`  
**Errors**:
```json
{ "message": "Access denied" }
```

---

### GET `/all-attendance`
Get attendance records for all employees.

**Access**: Admin only (must be in Human Resource department)  
**Query Parameters** _(optional)_:
- `year`, `month`, `day`

**Response**: Same as `/my-attendance`  
**Errors**:
```json
{ "message": "Access denied" }
```

---

### GET `/employee/<id>/attendance`
Get attendance records for a specific employee by ID.

**Access**: Admin only (must be in Human Resource department)  
**Path Parameter**:
- `id`: Employee ID (integer)

**Query Parameters** _(optional)_:
- `year`, `month`, `day`

**Response**: Same as `/my-attendance`  
**Errors**:
```json
{ "message": "Access denied" }
```

---

## Access Levels Summary

| Endpoint                          | Staff | Manager | Admin (HR Only) |
|----------------------------------|:-----:|:-------:|:---------------:|
| `/status`                        | ✅    | ✅      | ✅              |
| `/clock-in`                      | ✅    | ✅      | ✅              |
| `/clock-out`                     | ✅    | ✅      | ✅              |
| `/my-attendance`                | ✅    | ✅      | ✅              |
| `/department-attendance`        | ❌    | ✅      | ❌              |
| `/all-attendance`               | ❌    | ❌      | ✅              |
| `/employee/<id>/attendance`     | ❌    | ❌      | ✅              |

---

##  Authentication Example

```http
Authorization: Bearer <your-jwt-token>
```

---

## 📘 Notes

- Dates default to current day if no filter is applied.
- Only **Admins in HR** can access full employee data.
- Managers can only view data for their department.

---



# 3. Employee Management API Documentation

This section documents the API endpoints related to **Employee Management**.

---

## Namespace: `/employees`

### JWT Authentication Required for all endpoints

---

### GET `/employees/myaccount`

**Description**: Get the current employee's profile.  
**Authorization**: Required (JWT)  
**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_no": "1234567890",
  "gender": "Male",
  "address": "123 Main St",
  "country": "USA",
  "emp_department": "HR",
  "emp_team": "Recruitment",
  "emp_position": "Manager",
  "emp_rank": "admin",
  "emp_leave_balance": 10.0,
  "emp_start_date": "2023-01-01",
  "emp_end_date": null,
  "emp_status": "Active",
  "emp_work_status": "In office"
}
```

---

### PUT `/employees/myaccount/update`

**Description**: Update personal profile of the current employee.  
**Authorization**: Required (JWT)  
**Request Body**:
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "phone_no": "9876543210",
  "gender": "Female",
  "address": "456 Main St",
  "country": "Canada"
}
```
**Response**:
```json
{ "message": "Profile updated successfully" }
```

---

### GET `/employees/`

**Description**: View all employees (HR can see all, managers only their department).  
**Authorization**: Required (JWT)  
**Response**: List of employee profiles (see model above).  
**Access**:
- HR: all employees
- Manager: department employees only

---

### GET `/employees/<id>`

**Description**: Get a specific employee's profile by ID.  
**Authorization**: Required (JWT)  
**Access**:
- HR: all employees
- Manager: employees in same department

---

### PUT `/employees/<id>/update`

**Description**: HR updates employee job information.  
**Authorization**: Required (JWT)  
**Request Body**:
```json
{
  "emp_department": "IT",
  "emp_team": "Backend",
  "emp_position": "Engineer",
  "emp_rank": "staff"
}
```
**Response**:
```json
{ "message": "Employee record updated successfully" }
```

---

### PUT `/employees/<id>/terminate`

**Description**: HR terminates an employee by setting status and end date.  
**Authorization**: Required (JWT)  
**Response**:
```json
{ "message": "Employee John Doe terminated successfully" }
```

---

## Data Models

### Employee Model

Includes all employee details like name, contact, department, status, etc.

### UpdateProfile

Fields:
- `first_name`
- `last_name`
- `phone_no`
- `gender`
- `address`
- `country`

### HRUpdate

Fields:
- `emp_department`
- `emp_team`
- `emp_position`
- `emp_rank`



# 4. Leave Management API Documentation

Namespace: `leave`  
Description: Leave management operations for employees, managers, and admins.

---

## Models

### LeaveRequest
| Field           | Type    | Description                                           |
|-----------------|---------|-------------------------------------------------------|
| id              | Integer | Unique ID of the leave request                         |
| employee_id     | Integer | ID of the employee requesting leave                    |
| leave_type      | String  | Type of leave (`Annual`, `Sick`, `Personal`, `Emergency`) |
| start_date     | String  | Start date of the leave (`YYYY-MM-DD`)                 |
| end_date       | String  | End date of the leave (`YYYY-MM-DD`)                   |
| days_requested | Float   | Number of days requested                                |
| reason         | String  | Reason for leave                                       |
| status         | String  | Leave status (`Pending`, `Approved`, `Rejected`)       |
| approved_by    | Integer | Employee ID of the approver                             |
| approved_at    | String  | Timestamp of approval/rejection                         |
| rejection_reason | String | Reason for rejection (if any)                           |

---

### RequestInput
| Field       | Type   | Required | Description               |
|-------------|--------|----------|---------------------------|
| leave_type  | String | Yes      | Type of leave             |
| start_date  | String | Yes      | Leave start date          |
| end_date    | String | Yes      | Leave end date            |
| reason      | String | Yes      | Reason for the leave      |

---

### StatusUpdate
| Field            | Type   | Required | Description                   |
|------------------|--------|----------|-------------------------------|
| rejection_reason | String | No       | Reason for rejecting the leave|

---

## Endpoints

### Get All Leave Requests  
`GET /leave/all-requests`  
- **Access:** Admins and Managers only  
- **Description:** View leave requests based on role access. Managers see only requests in their department; Admins see all.

---

### Submit a Leave Request  
`POST /leave/request`  
- **Access:** Authenticated employee  
- **Request Body:** `RequestInput`  
- **Description:** Submit a leave request with start/end dates, type, and reason.  
- **Validation:**  
  - Dates must be in `YYYY-MM-DD` format.  
  - End date must be after start date.  
  - Employee must have sufficient leave balance.

---

### Get My Leave Requests  
`GET /leave/my-requests`  
- **Access:** Authenticated employee  
- **Description:** Retrieve all leave requests submitted by the current user.

---

### Edit a Pending Leave Request  
`PUT /leave/<id>/edit`  
- **Access:** Owner of the leave request only  
- **Request Body:** `RequestInput`  
- **Description:** Edit a leave request if it is still pending.  
- **Validation:**  
  - Only pending requests can be edited.  
  - Sufficient leave balance must exist for updated dates.

---

### Delete a Pending Leave Request  
`DELETE /leave/<id>/delete`  
- **Access:** Owner of the leave request only  
- **Description:** Delete a pending leave request.

---

### Get Pending Leave Requests  
`GET /leave/pending`  
- **Access:** Admins and Managers  
- **Description:** List all pending leave requests. Managers see only their department's requests; Admins see all.

---

### Approve a Leave Request  
`PUT /leave/<id>/approve`  
- **Access:** Admins and Managers  
- **Description:** Approve a pending leave request.  
- **Business Rules:**  
  - Managers can only approve requests from their department.  
  - Admins can only approve requests from other admins.

---

### Reject a Leave Request  
`PUT /leave/<id>/reject`  
- **Access:** Admins and Managers  
- **Request Body:** `StatusUpdate`  
- **Description:** Reject a pending leave request.  
- **Business Rules:**  
  - Managers can only reject requests from their department.  
  - Admins can only reject requests from other admins.

---

### Start Leave  
`POST /leave/start`  
- **Access:** Authenticated employee  
- **Description:** Mark an approved leave as started if it begins today. Updates employee status to 'On leave'.  
- **Validation:**  
  - Employee must not already be on leave.  
  - There must be an approved leave request starting today.

---

### Get Leave Balance  
`GET /leave/balance`  
- **Access:** Authenticated employee  
- **Description:** Retrieve the current leave balance of the employee.

---

## Authentication

All routes require JWT authentication (`@jwt_required()`).

---

## Error Responses

- `400 Bad Request`: Invalid input, date format errors, insufficient leave balance, or request already processed.
- `403 Forbidden`: Access denied due to insufficient privileges.
- `404 Not Found`: Requested leave or employee does not exist.

---

# Notes

- Dates are expected in ISO format: `YYYY-MM-DD`.
- Leave statuses: `Pending`, `Approved`, `Rejected`.
- Leave types: `Annual`, `Sick`, `Personal`, `Emergency`.
- Role-based access controls enforced for managers and admins.

---

*End of Documentation*
