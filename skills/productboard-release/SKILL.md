---
name: productboard-release
description: Manage ProductBoard releases and roadmap planning
user-invocable: false
homepage: https://github.com/robertoamoreno/openclaw-productboard
metadata: {"openclaw":{"emoji":"🚀"}}
---

# ProductBoard Release Planning Skill

Plan and manage product releases by organizing features, tracking progress, and updating statuses in ProductBoard.

## Available Tools

- `pb_feature_create` - Create new features for releases
- `pb_feature_update` - Update feature status and details
- `pb_feature_list` - List features by status or product
- `pb_feature_get` - Get detailed feature information
- `pb_product_list` - List products
- `pb_product_hierarchy` - View product structure
- `pb_user_list` - Find users to assign as owners

## Release Planning Workflow

### 1. Review Current State

```
1. pb_product_hierarchy - Understand workspace structure
2. pb_feature_list with status "candidate" - Review feature candidates
3. pb_feature_list with status "in-progress" - Check ongoing work
```

### 2. Prioritize Features

Review candidates and update their status:

```
pb_feature_update:
  - id: "feature-id"
  - status: "in-progress"  // Move to active development
```

### 3. Assign Owners

Find users and assign feature ownership:

```
1. pb_user_list - Get available team members
2. pb_feature_update:
   - id: "feature-id"
   - ownerEmail: "developer@company.com"
```

### 4. Set Timeframes

Add planning dates to features:

```
pb_feature_update:
  - id: "feature-id"
  - startDate: "2024-01-15"
  - endDate: "2024-02-15"
```

### 5. Track Progress

Monitor feature statuses:

```
pb_feature_list with status "in-progress" - Active development
pb_feature_list with status "shipped" - Completed features
```

## Feature Status Lifecycle

| Status | Description |
|--------|-------------|
| `new` | Just created, not yet evaluated |
| `candidate` | Being considered for development |
| `in-progress` | Actively being developed |
| `shipped` | Released to customers |
| `postponed` | Deferred to future planning |
| `archived` | No longer relevant |

## Planning Scenarios

### Sprint Planning

1. List candidates: `pb_feature_list` with status "candidate"
2. Review each feature: `pb_feature_get` for details
3. Move selected features to in-progress: `pb_feature_update`
4. Assign owners: `pb_feature_update` with ownerEmail
5. Set sprint dates: `pb_feature_update` with startDate/endDate

### Release Retrospective

1. List shipped features: `pb_feature_list` with status "shipped"
2. Review feedback on features: Use feedback skill tools
3. Archive completed work: `pb_feature_update` with status "archived"

### Quarterly Planning

1. Review product hierarchy: `pb_product_hierarchy`
2. List all active features by product
3. Reassess priorities and update statuses
4. Create new features as needed: `pb_feature_create`

## Organizing Features

### By Product

```
pb_feature_create:
  - name: "Feature name"
  - productId: "product-id"
  - status: "candidate"
```

### By Component

```
pb_feature_create:
  - name: "Feature name"
  - componentId: "component-id"
  - status: "candidate"
```

### As Sub-feature

```
pb_feature_create:
  - name: "Sub-feature name"
  - parentFeatureId: "parent-feature-id"
```

## Best Practices

1. **Use consistent statuses**: Move features through the lifecycle systematically
2. **Assign owners early**: Clear ownership improves accountability
3. **Set realistic timeframes**: Update dates as plans change
4. **Organize hierarchically**: Use products, components, and sub-features
5. **Archive completed work**: Keep the backlog clean by archiving shipped features
6. **Review regularly**: Use listing tools to audit feature states
