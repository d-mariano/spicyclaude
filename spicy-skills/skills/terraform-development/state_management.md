# Terraform State Management

Comprehensive guide for managing Terraform state safely and effectively.

## Remote State Backends

### Google Cloud Storage (GCS)

**Recommended for:** GCP-based infrastructure

**Setup:**
```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "prod/terraform.tfstate"
  }
}
```

**Create GCS bucket with best practices:**
```hcl
# infrastructure/state-bucket/main.tf
resource "google_storage_bucket" "terraform_state" {
  name          = "my-terraform-state"
  location      = "US"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.terraform_state.id
  }
  
  lifecycle_rule {
    condition {
      num_newer_versions = 10
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    name        = "terraform-state"
    environment = "global"
    purpose     = "terraform-state"
  }
}

# KMS key for encryption
resource "google_kms_key_ring" "terraform_state" {
  name     = "terraform-state"
  location = "us-central1"
}

resource "google_kms_crypto_key" "terraform_state" {
  name     = "terraform-state-key"
  key_ring = google_kms_key_ring.terraform_state.id
  
  rotation_period = "7776000s" # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}
```

### Terraform Cloud

**Recommended for:** Teams, compliance requirements, remote execution

```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "my-app-prod"
    }
  }
}
```

**With tags for workspace management:**
```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      tags = ["app:my-app", "env:prod", "team:platform"]
    }
  }
}
```

### Azure Blob Storage

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state"
    storage_account_name = "terraformstate12345"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

### Google Cloud Storage

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "terraform/state"
  }
}
```

## State File Organization

### Separate States by Scope

**Don't:** Single state for entire infrastructure
```
Bad:
terraform-state/
└── everything.tfstate  # All resources in one state
```

**Do:** Separate states by logical boundaries
```
Good:
terraform-state/
├── networking/
│   └── terraform.tfstate
├── security/
│   └── terraform.tfstate
├── applications/
│   ├── app-1.tfstate
│   └── app-2.tfstate
└── data/
    └── databases.tfstate
```

**Benefits:**
- Reduced blast radius
- Faster plan/apply operations
- Team-based access control
- Independent update cycles

### State Separation Strategies

**By environment:**
```
state/
├── dev/
│   └── terraform.tfstate
├── staging/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

**By application:**
```
state/
├── app-1/
│   ├── dev.tfstate
│   └── prod.tfstate
└── app-2/
    ├── dev.tfstate
    └── prod.tfstate
```

**By layer:**
```
state/
├── 01-networking/
│   └── terraform.tfstate
├── 02-security/
│   └── terraform.tfstate
├── 03-data/
│   └── terraform.tfstate
└── 04-compute/
    └── terraform.tfstate
```

## Sharing Data Between States

### terraform_remote_state

Read outputs from another state file:

```hcl
# In networking configuration
output "network_id" {
  value       = google_compute_network.main.id
  description = "VPC network ID for use in other configurations"
}

output "subnet_self_links" {
  value       = { for k, v in google_compute_subnetwork.subnets : k => v.self_link }
  description = "Map of subnet self links"
}
```

```hcl
# In application configuration
data "terraform_remote_state" "networking" {
  backend = "gcs"
  
  config = {
    bucket = "my-terraform-state"
    prefix = "networking/terraform.tfstate"
  }
}

resource "google_compute_instance" "app" {
  name         = "app-server"
  machine_type = var.machine_type
  zone         = var.zone
  
  boot_disk {
    initialize_params {
      image = var.image
    }
  }
  
  network_interface {
    subnetwork = data.terraform_remote_state.networking.outputs.subnet_self_links["app-subnet"]
  }
}
```

**Security consideration:** Using `terraform_remote_state` grants access to entire state file. Consider using data sources or external stores for sensitive data.

### Alternative: External Data Stores

**GCP Secret Manager:**
```hcl
# In networking module - store network ID
resource "google_secret_manager_secret" "network_id" {
  secret_id = "network-id"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "network_id" {
  secret      = google_secret_manager_secret.network_id.id
  secret_data = google_compute_network.main.id
}

# In application module - read network ID
data "google_secret_manager_secret_version" "network_id" {
  secret = "network-id"
}

resource "google_compute_instance" "app" {
  # Use the network ID from secret manager
  # Note: You'd typically use a data source to look up the actual subnet
}
```

**Benefits:**
- Granular access control via IAM
- No access to entire state
- Can use across different tools

## State Locking

### Why Locking Matters

Without locking, concurrent runs can corrupt state:

```
User A: terraform apply
User B: terraform apply  ← Both read same state
                         ← Both write changes
                         ← State corruption!
```

### Lock Providers

**GCS (automatic):**
```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "terraform.tfstate"
    # Locking is automatic - no additional configuration needed
  }
}
```

**Terraform Cloud (automatic):**
- Locking built-in
- Shows who has the lock
- Can force-unlock via UI

### Handling Lock Issues

**If state is locked:**
```bash
# Check lock information
terraform force-unlock <LOCK_ID>

# Only use force-unlock if:
# 1. Process definitely crashed/terminated
# 2. No other Terraform process running
# 3. You understand the risks
```

**Prevent accidental force-unlocks:**
```bash
# In CI/CD, fail fast on locked state
terraform apply || {
  echo "Apply failed - state may be locked"
  exit 1
}
# Don't auto force-unlock
```

## State Migration

### Migrating Between Backends

**From local to GCS:**

Step 1: Configure backend
```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "terraform.tfstate"
  }
}
```

Step 2: Initialize with migration
```bash
terraform init -migrate-state

# Review migration plan
# Terraform will show what it will do

# Confirm migration
# Type 'yes' when prompted
```

Step 3: Verify
```bash
# Check state is in GCS
gsutil ls gs://my-terraform-state/

# Old local state should still exist as backup
ls terraform.tfstate.backup
```

**Between different GCS buckets:**
```bash
# Update backend configuration
# Then run:
terraform init -migrate-state -reconfigure
```

### Moving Resources Between States

**Scenario:** Split monolithic state into separate states

**Step 1: Identify resources to move**
```bash
terraform state list

# Example output:
# aws_vpc.main
# aws_subnet.public[0]
# aws_subnet.public[1]
# aws_instance.app[0]
# aws_instance.app[1]
```

**Step 2: Move resources**
```bash
# Remove from current state (exports to file)
terraform state rm aws_instance.app[0] > app-0.tfstate
terraform state rm aws_instance.app[1] > app-1.tfstate

# In new configuration, import the resources
cd ../new-config
terraform import aws_instance.app[0] i-1234567890abcdef0
terraform import aws_instance.app[1] i-0987654321fedcba0
```

**Better approach: Use `terraform state mv`**
```bash
# Initialize both state configurations
cd ../old-config
terraform init

cd ../new-config
terraform init

# Move resource between states
terraform state mv \
  -state-out=../new-config/terraform.tfstate \
  aws_instance.app[0] \
  aws_instance.app[0]
```

## State File Inspection

### View State Contents

```bash
# List all resources
terraform state list

# Show detailed resource
terraform state show aws_instance.web

# Show all state in JSON
terraform show -json > state.json
```

### Pull State for Inspection

```bash
# Download current state
terraform state pull > current.tfstate

# View in readable format
cat current.tfstate | jq '.'

# Compare states
diff <(terraform state pull) old.tfstate
```

## State Manipulation

### WARNING: Dangerous Operations

State manipulation should be last resort. Always:
1. Backup state first
2. Understand exactly what you're doing
3. Test in non-production first
4. Have rollback plan

### Common State Operations

**Remove resource from state (keeps in infrastructure):**
```bash
# Resource remains in AWS but Terraform forgets about it
terraform state rm aws_instance.old_server

# Terraform will no longer manage this resource
# Useful when migrating to different management tool
```

**Import existing resource:**
```bash
# Resource exists in AWS but not in state
terraform import aws_instance.new_server i-1234567890abcdef0

# Must have matching configuration in .tf files
```

**Rename resource in state:**
```bash
# After renaming in configuration
terraform state mv aws_instance.old_name aws_instance.new_name

# Avoids destroy + recreate
```

**Replace resource address:**
```bash
# Move resource between modules
terraform state mv \
  module.old_module.aws_instance.web \
  module.new_module.aws_instance.web
```

## State Backup and Recovery

### Automatic Backups

**GCS with versioning (recommended):**
```hcl
resource "google_storage_bucket" "terraform_state" {
  name     = "my-terraform-state"
  location = "US"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      num_newer_versions = 90
      age                = 30
    }
    action {
      type = "Delete"
    }
  }
}
```

**Local backups:**
Terraform automatically creates `.terraform.tfstate.backup` before modifications

### Manual Backups

```bash
# Before risky operation
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate

# Before manual state edit
cp terraform.tfstate terraform.tfstate.manual-backup
```

### State Recovery

**From GCS version:**
```bash
# List versions
gsutil ls -a gs://my-terraform-state/default/terraform.tfstate

# Download specific version (generation number)
gsutil cp gs://my-terraform-state/default/terraform.tfstate#<GENERATION> \
  recovered-state.tfstate

# Replace current state (CAREFUL!)
terraform state push recovered-state.tfstate
```

**From local backup:**
```bash
# Replace state with backup
cp terraform.tfstate.backup terraform.tfstate

# Push to remote backend
terraform state push terraform.tfstate
```

## State Security

### Sensitive Data in State

**Problem:** State files contain sensitive data in plaintext
- Passwords
- Private keys
- Access tokens
- Connection strings

**Solutions:**

**1. Encrypt state at rest:**
```hcl
# GCS backend with KMS encryption
resource "google_storage_bucket" "terraform_state" {
  name     = "my-terraform-state"
  location = "US"
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.terraform_state.id
  }
}

resource "google_kms_key_ring" "terraform_state" {
  name     = "terraform-state"
  location = "us-central1"
}

resource "google_kms_crypto_key" "terraform_state" {
  name            = "terraform-state-key"
  key_ring        = google_kms_key_ring.terraform_state.id
  rotation_period = "7776000s" # 90 days
}
```

**2. Restrict state access:**
```hcl
# IAM policy for state bucket
resource "google_storage_bucket_iam_binding" "terraform_state" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  
  members = [
    "serviceAccount:terraform@my-project.iam.gserviceaccount.com",
  ]
}

# Prevent public access
resource "google_storage_bucket_iam_binding" "prevent_public" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.legacyBucketReader"
  
  members = [] # No public access
}
```

**3. Use external secrets:**
```hcl
# Don't store secrets in state
# Use data sources to fetch at runtime
data "google_secret_manager_secret_version" "db_password" {
  secret = "prod-db-password"
}

resource "google_sql_database_instance" "main" {
  name             = "main-instance"
  database_version = "POSTGRES_14"
  
  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_user" "main" {
  name     = "app"
  instance = google_sql_database_instance.main.name
  password = data.google_secret_manager_secret_version.db_password.secret_data
  # Password stored in Secret Manager, not state
}
```

### Access Control

**IAM policy for state bucket:**
```hcl
# Grant specific service account access to state bucket
resource "google_storage_bucket_iam_member" "terraform_state_admin" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform@my-project.iam.gserviceaccount.com"
}

# Grant read-only access to viewers
resource "google_storage_bucket_iam_member" "terraform_state_viewer" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectViewer"
  member = "group:infrastructure-viewers@company.com"
}

# Ensure no public access
resource "google_storage_bucket_iam_binding" "no_public_access" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.legacyBucketReader"
  
  members = [] # Empty list prevents public access
}
```

## State Best Practices Checklist

- [ ] Always use remote backend for team projects
- [ ] Enable state locking
- [ ] Enable state encryption
- [ ] Configure state versioning/backups
- [ ] Separate states by scope (app, environment, layer)
- [ ] Restrict state file access (IAM, RBAC)
- [ ] Never commit state files to version control
- [ ] Use `terraform_remote_state` sparingly
- [ ] Test state migrations in non-production first
- [ ] Backup state before manual manipulation
- [ ] Document state structure and dependencies
- [ ] Monitor state file size (split if > 10MB)
