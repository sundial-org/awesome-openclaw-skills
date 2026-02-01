# Ontology Commands

Work with Foundry ontologies, object types, objects, actions, and queries.

## RID Format
`ri.ontology.main.ontology.{uuid}`

## List Ontologies

```bash
pltr ontology list [--page-size N] [--format FORMAT] [--output FILE]

# Example
pltr ontology list --format table
```

## Get Ontology Details

```bash
pltr ontology get ONTOLOGY_RID [--format FORMAT]

# Example
pltr ontology get ri.ontology.main.ontology.abc123
```

## Object Type Commands

### List Object Types

```bash
pltr ontology object-type-list ONTOLOGY_RID [--format FORMAT]

# Example
pltr ontology object-type-list ri.ontology.main.ontology.abc123
```

### Get Object Type Details

```bash
pltr ontology object-type-get ONTOLOGY_RID OBJECT_TYPE

# OBJECT_TYPE is the API name

# Example
pltr ontology object-type-get ri.ontology.main.ontology.abc123 Employee
```

## Object Commands

### List Objects

```bash
pltr ontology object-list ONTOLOGY_RID OBJECT_TYPE [OPTIONS]

# Options:
#   --page-size INTEGER    Results per page
#   --properties TEXT      Comma-separated properties to include

# Example
pltr ontology object-list ri.ontology.main.ontology.abc123 Employee
pltr ontology object-list ri.ontology.main.ontology.abc123 Employee --properties "name,department,email"
```

### Get Specific Object

```bash
pltr ontology object-get ONTOLOGY_RID OBJECT_TYPE PRIMARY_KEY [--properties TEXT]

# Example
pltr ontology object-get ri.ontology.main.ontology.abc123 Employee "john.doe"
```

### Aggregate Objects

```bash
pltr ontology object-aggregate ONTOLOGY_RID OBJECT_TYPE AGGREGATIONS [OPTIONS]

# AGGREGATIONS is JSON
# Options:
#   --group-by TEXT    Fields to group by (comma-separated)
#   --filter TEXT      Filter criteria (JSON)

# Example - Count by department
pltr ontology object-aggregate ri.ontology.main.ontology.abc123 Employee '{"count": "count"}' --group-by department
```

### List Linked Objects

```bash
pltr ontology object-linked ONTOLOGY_RID OBJECT_TYPE PRIMARY_KEY LINK_TYPE [--properties TEXT]

# Example
pltr ontology object-linked ri.ontology.main.ontology.abc123 Employee "john.doe" worksIn
```

## Action Commands

### Apply Action

```bash
pltr ontology action-apply ONTOLOGY_RID ACTION_TYPE PARAMETERS

# PARAMETERS is JSON

# Example
pltr ontology action-apply ri.ontology.main.ontology.abc123 promoteEmployee '{"employeeId": "john.doe", "newLevel": "senior"}'
```

### Validate Action

Validate parameters without executing:

```bash
pltr ontology action-validate ONTOLOGY_RID ACTION_TYPE PARAMETERS

# Example
pltr ontology action-validate ri.ontology.main.ontology.abc123 promoteEmployee '{"employeeId": "john.doe", "newLevel": "senior"}'
```

## Query Commands

### Execute Predefined Query

```bash
pltr ontology query-execute ONTOLOGY_RID QUERY_NAME [--parameters JSON]

# Example
pltr ontology query-execute ri.ontology.main.ontology.abc123 getEmployeesByDepartment --parameters '{"department": "Engineering"}'
```

## Common Patterns

### Explore an ontology
```bash
ONTOLOGY="ri.ontology.main.ontology.abc123"

# List all object types
pltr ontology object-type-list $ONTOLOGY

# Get details of a specific type
pltr ontology object-type-get $ONTOLOGY Employee

# List objects with specific properties
pltr ontology object-list $ONTOLOGY Employee --properties "name,department,startDate"
```

### Get employee and their projects
```bash
ONTOLOGY="ri.ontology.main.ontology.abc123"

# Get employee
pltr ontology object-get $ONTOLOGY Employee "john.doe"

# Get linked projects
pltr ontology object-linked $ONTOLOGY Employee "john.doe" worksOn --properties "name,status,deadline"
```

### Department statistics
```bash
pltr ontology object-aggregate ri.ontology.main.ontology.abc123 Employee \
  '{"count": "count", "avg_salary": "avg"}' \
  --group-by department \
  --format csv --output department_stats.csv
```

### Export employees to JSON
```bash
pltr ontology object-list ri.ontology.main.ontology.abc123 Employee \
  --properties "name,department,email,startDate" \
  --format json --output employees.json
```
