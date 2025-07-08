---
## File Descriptions

### 1. `__init__.py`
- Initializes the database module.
- Typically used to set up imports or configurations for the database package.
---

### 2. `create_database.py`

- **Purpose**: Handles the creation of the database if it does not already exist.
- **Key Functions**:
  - `create_database_if_not_exists(db_name, user, password, host)`: Creates the database if it does not exist.

---

### 3. `database.md`

- **Purpose**: Contains documentation for the database module.
- **Usage**: Provides an overview of the database-related files and their functionality.

---

### 4. `get_creds_db.py`

- **Purpose**: Fetches credentials (e.g., API tokens, user credentials) from the database.
- **Key Functions**:
  - `get_credentials(entity_id)`: Retrieves credentials for a specific entity.

---

### 5. `insert_data_db.py`

- **Purpose**: Handles the insertion of data into the database.
- **Key Functions**:
  - `insert_audit_data(entity_id, data, mode)`: Inserts audit logs into the database for tracking purposes.

---

### 6. `schemas.py`

- **Purpose**: Defines the database schemas using SQLAlchemy.
- **Key Components**:
  - Models for tables such as `ZohoCreds`, `AuditLogs`, etc.
  - Relationships and constraints for database tables.

---

### 7. `update_data.py`

- **Purpose**: Handles updates to existing data in the database.
- **Key Functions**:
  - `update_credentials(entity_id, new_data)`: Updates credentials for a specific entity.
  - `update_audit_logs(log_id, updated_data)`: Updates audit log entries.

---

## Usage Notes

1. **Database Creation**:

   - Use `create_database.py` to ensure the database is created before running the application.

2. **Schema Management**:

   - All schema definitions are in `schemas.py`. Modify this file to add or update database tables.

3. **Data Insertion**:

   - Use `insert_data_db.py` for inserting new data, such as audit logs or user activity.

4. **Data Updates**:

   - Use `update_data.py` for updating existing records in the database.

5. **Credential Management**:
   - Use `get_creds_db.py` and `update_data.py` for fetching and updating credentials.

---

## Notes for Developers

- **Environment Variables**:

  - Ensure database connection details (e.g., host, user, password) are set in environment variables or configuration files.

- **Testing**:

  - Test database operations (e.g., creation, insertion, updates) in a staging environment before deploying to production.

- **Logging**:
  - Add logging for all database operations to track errors and performance issues.

---

This documentation provides an overview of the database module and its components, making it easier for developers to understand and work with the database-related functionality.
