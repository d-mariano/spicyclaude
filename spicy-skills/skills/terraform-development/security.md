# Terraform Security Best Practices

Comprehensive security guidance for Terraform infrastructure as code.

## Secrets Management

### Never Hard-Code Secrets

**❌ BAD - Hard-coded secrets:**
```hcl
resource "google_sql_database_instance" "main" {
  name             = "main-instance"
  database_version = "POSTGRES_14"
}

resource "google_sql_user" "main" {
  name     = "admin"
  instance = google_sql_database_instance.main.name
  password = "SuperSecret123!"  # NEVER DO THIS
}
```

**✅ GOOD - Use environment variables:**
```hcl
variable "db_password" {
  type        = string
  description = "Database password"
  sensitive   = true
}

resource "google_sql_user" "main" {
  name     = "admin"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}
```

```bash
# Set via environment variable
export TF_VAR_db_password="$(gcloud secrets versions access latest --secret=db-password)"

terraform apply
```

**✅ BEST - Fetch from Secret Manager:**
```hcl
data "google_secret_manager_secret_version" "db_password" {
  secret = "production-database-password"
}

resource "google_sql_user" "main" {
  name     = "admin"
  instance = google_sql_database_instance.main.name
  password = data.google_secret_manager_secret_version.db_password.secret_data
}
```

### Sensitive Variable Handling

**Mark variables as sensitive:**
```hcl
variable "api_key" {
  type        = string
  description = "API key for external service"
  sensitive   = true  # Redacted in plan/apply output
}

variable "database_credentials" {
  type = object({
    username = string
    password = string
  })
  description = "Database credentials"
  sensitive   = true
}
```

**Sensitive outputs:**
```hcl
output "database_endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "Database connection endpoint"
}

output "database_password" {
  value       = aws_db_instance.main.password
  description = "Database password"
  sensitive   = true  # Won't display in console
}
```

### Secrets Management Solutions

**GCP Secret Manager:**
```hcl
# Create secret
resource "google_secret_manager_secret" "db_password" {
  secret_id = "prod-db-password"
  
  replication {
    auto {}
  }
  
  labels = {
    environment = "prod"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password  # Set via TF_VAR or CI/CD
}

# Use secret
data "google_secret_manager_secret_version" "db_password" {
  secret = google_secret_manager_secret.db_password.id
}

resource "google_sql_user" "main" {
  name     = "app"
  instance = google_sql_database_instance.main.name
  password = data.google_secret_manager_secret_version.db_password.secret_data
}
```

**HashiCorp Vault:**
```hcl
provider "vault" {
  address = "https://vault.company.com"
  # Auth via environment variables or cloud provider
}

data "vault_generic_secret" "database" {
  path = "secret/database"
}

resource "google_sql_user" "main" {
  name     = data.vault_generic_secret.database.data["username"]
  password = data.vault_generic_secret.database.data["password"]
  instance = google_sql_database_instance.main.name
}
```

## Least Privilege Access

### IAM Policies

**Principle:** Grant minimum permissions required.

**❌ BAD - Overly permissive:**
```hcl
resource "google_project_iam_member" "app" {
  project = var.project_id
  role    = "roles/owner"  # Full project access - too broad!
  member  = "serviceAccount:app@project.iam.gserviceaccount.com"
}
```

**✅ GOOD - Specific permissions:**
```hcl
# Service account for application
resource "google_service_account" "app" {
  account_id   = "app-service-account"
  display_name = "Application Service Account"
  project      = var.project_id
}

# Grant only needed permissions
resource "google_storage_bucket_iam_member" "app_storage" {
  bucket = google_storage_bucket.app_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app.email}"
}

resource "google_project_iam_member" "app_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app.email}"
}
```

### Service-Specific Roles

**Separate service accounts for different services:**
```hcl
# Compute Engine service account
resource "google_service_account" "compute" {
  account_id   = "compute-service-account"
  display_name = "Compute Engine Service Account"
  project      = var.project_id
}

# Cloud Functions service account
resource "google_service_account" "functions" {
  account_id   = "functions-service-account"
  display_name = "Cloud Functions Service Account"
  project      = var.project_id
}

# Grant minimal permissions
resource "google_project_iam_member" "compute_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.compute.email}"
}
```

## Network Security

### VPC Design

**Isolate tiers with subnets:**
```hcl
# VPC network
resource "google_compute_network" "main" {
  name                    = "main-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Public subnet for load balancers
resource "google_compute_subnetwork" "public" {
  name          = "public-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id
}

# Private subnet for application servers
resource "google_compute_subnetwork" "private" {
  name                     = "private-subnet"
  ip_cidr_range            = "10.0.2.0/24"
  region                   = var.region
  network                  = google_compute_network.main.id
  project                  = var.project_id
  private_ip_google_access = true
  
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Database subnet
resource "google_compute_subnetwork" "database" {
  name          = "database-subnet"
  ip_cidr_range = "10.0.3.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id
}
```

### Firewall Rules - Least Privilege

**❌ BAD - Open to the world:**
```hcl
resource "google_compute_firewall" "bad" {
  name    = "allow-all"
  network = google_compute_network.main.name
  project = var.project_id
  
  allow {
    protocol = "all"
  }
  
  source_ranges = ["0.0.0.0/0"]  # Open to internet!
}
```

**✅ GOOD - Specific rules:**
```hcl
# Allow HTTPS from internet to load balancer
resource "google_compute_firewall" "lb_https" {
  name    = "allow-lb-https"
  network = google_compute_network.main.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["lb"]
  
  description = "Allow HTTPS from internet to load balancer"
}

# Allow HTTP from internet (redirect to HTTPS)
resource "google_compute_firewall" "lb_http" {
  name    = "allow-lb-http"
  network = google_compute_network.main.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["lb"]
  
  description = "Allow HTTP for redirect to HTTPS"
}

# Allow traffic from load balancer to application servers
resource "google_compute_firewall" "lb_to_app" {
  name    = "allow-lb-to-app"
  network = google_compute_network.main.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
  
  source_tags = ["lb"]
  target_tags = ["app"]
  
  description = "Allow load balancer to reach application servers"
}

# Allow traffic from application servers to database
resource "google_compute_firewall" "app_to_db" {
  name    = "allow-app-to-db"
  network = google_compute_network.main.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }
  
  source_tags = ["app"]
  target_tags = ["database"]
  
  description = "Allow application servers to reach database"
}

# Deny all other traffic (implicit, but explicit for clarity)
resource "google_compute_firewall" "deny_all_ingress" {
  name     = "deny-all-ingress"
  network  = google_compute_network.main.name
  project  = var.project_id
  priority = 65535
  
  deny {
    protocol = "all"
  }
  
  source_ranges = ["0.0.0.0/0"]
  
  description = "Explicit deny all other ingress traffic"
}
```

## Encryption

### Data at Rest

**Cloud Storage encryption:**
```hcl
resource "google_storage_bucket" "data" {
  name     = "my-data-bucket"
  location = "US"
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.data.id
  }
  
  labels = {
    environment = "production"
    encrypted   = "true"
  }
}

# KMS key for encryption
resource "google_kms_key_ring" "data" {
  name     = "data-encryption"
  location = "us-central1"
  project  = var.project_id
}

resource "google_kms_crypto_key" "data" {
  name            = "data-encryption-key"
  key_ring        = google_kms_key_ring.data.id
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
  
  labels = {
    purpose = "data-encryption"
  }
}
```

**Cloud SQL encryption:**
```hcl
resource "google_sql_database_instance" "main" {
  name             = "main-instance"
  database_version = "POSTGRES_14"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier = "db-custom-2-7680"
    
    # Encryption at rest with CMEK
    disk_encryption_configuration {
      kms_key_name = google_kms_crypto_key.sql.id
    }
    
    # Automated backups
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }
    
    # IP configuration
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
      require_ssl                                   = true
    }
  }
  
  deletion_protection = true
  
  labels = {
    environment = "production"
  }
}
```

**Compute Engine disk encryption:**
```hcl
resource "google_compute_disk" "data" {
  name  = "data-disk"
  type  = "pd-ssd"
  zone  = var.zone
  size  = 100
  
  disk_encryption_key {
    kms_key_self_link = google_kms_crypto_key.disk.id
  }
  
  labels = {
    purpose = "application-data"
  }
}
```

### Data in Transit

**Enforce TLS:**
```hcl
# HTTPS Load Balancer
resource "google_compute_ssl_certificate" "main" {
  name        = "app-cert"
  private_key = file("path/to/private-key.pem")
  certificate = file("path/to/certificate.pem")
  project     = var.project_id
}

resource "google_compute_target_https_proxy" "main" {
  name    = "app-https-proxy"
  url_map = google_compute_url_map.main.id
  
  ssl_certificates = [google_compute_ssl_certificate.main.id]
  ssl_policy       = google_compute_ssl_policy.modern.id
  
  project = var.project_id
}

resource "google_compute_ssl_policy" "modern" {
  name            = "modern-ssl-policy"
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
  project         = var.project_id
}

# Redirect HTTP to HTTPS
resource "google_compute_url_map" "http_redirect" {
  name    = "http-redirect"
  project = var.project_id
  
  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}
```

**Cloud SQL SSL enforcement:**
```hcl
resource "google_sql_database_instance" "main" {
  name             = "main-instance"
  database_version = "POSTGRES_14"
  region           = var.region
  
  settings {
    tier = "db-custom-2-7680"
    
    ip_configuration {
      ipv4_enabled    = false
      require_ssl     = true  # Force SSL connections
      private_network = google_compute_network.main.id
    }
  }
}
```

## Logging and Monitoring

### Enable Cloud Audit Logs

**Track all API calls:**
```hcl
# Enable audit logs for the project
resource "google_project_iam_audit_config" "project" {
  project = var.project_id
  service = "allServices"
  
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  
  audit_log_config {
    log_type = "DATA_READ"
  }
  
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# Create log sink to Cloud Storage for long-term retention
resource "google_logging_project_sink" "audit_logs" {
  name        = "audit-logs-to-storage"
  destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"
  project     = var.project_id
  
  filter = "logName:\"logs/cloudaudit.googleapis.com\""
  
  unique_writer_identity = true
}

resource "google_storage_bucket" "audit_logs" {
  name          = "audit-logs-${var.project_id}"
  location      = "US"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}
```

### VPC Flow Logs

**Monitor network traffic:**
```hcl
resource "google_compute_subnetwork" "app" {
  name          = "app-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id
  
  # Enable VPC Flow Logs
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
    metadata_fields      = [
      "src_instance",
      "dst_instance",
      "src_vpc",
      "dst_vpc"
    ]
  }
  
  private_ip_google_access = true
}
```

### Resource Access Logging

**Cloud Storage access logs:**
```hcl
resource "google_storage_bucket" "data" {
  name     = "my-data-bucket"
  location = "US"
  project  = var.project_id
  
  logging {
    log_bucket        = google_storage_bucket.logs.name
    log_object_prefix = "storage-access-logs/"
  }
}

resource "google_storage_bucket" "logs" {
  name          = "logs-${var.project_id}"
  location      = "US"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}
```

**Load Balancer access logs:**
```hcl
resource "google_compute_backend_service" "app" {
  name    = "app-backend"
  project = var.project_id
  
  # Enable access logs
  log_config {
    enable      = true
    sample_rate = 1.0
  }
  
  backend {
    group = google_compute_instance_group.app.self_link
  }
}
```

## Compliance and Governance

### Labeling Strategy

**Enforce labels for governance:**
```hcl
locals {
  required_labels = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
    owner       = var.owner_email
    cost_center = var.cost_center
  }
}

resource "google_compute_instance" "app" {
  name         = "app-server-${var.environment}"
  machine_type = var.machine_type
  zone         = var.zone
  
  boot_disk {
    initialize_params {
      image = var.image
    }
  }
  
  network_interface {
    network = "default"
  }
  
  labels = merge(
    local.required_labels,
    {
      role = "application"
    }
  )
}
```

### Resource Naming Conventions

**Consistent, auditable names:**
```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"
}

resource "google_storage_bucket" "data" {
  name     = "${local.name_prefix}-data-${var.project_id}"
  location = var.region
  project  = var.project_id
  
  labels = {
    name = "${local.name_prefix}-data"
  }
}
```

### Policy as Code

**Sentinel (Terraform Cloud):**
```hcl
# policies/encryption-required.sentinel
import "tfplan/v2" as tfplan

# Ensure all S3 buckets have encryption
s3_buckets = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_s3_bucket_server_side_encryption_configuration" and
  (rc.change.actions contains "create" or rc.change.actions contains "update")
}

main = rule {
  all s3_buckets as _, bucket {
    bucket.change.after.rule[0].apply_server_side_encryption_by_default != null
  }
}
```

**OPA (Open Policy Agent):**
```rego
# policies/security.rego
package terraform.security

# Deny S3 buckets without encryption
deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not has_encryption(resource)
  
  msg := sprintf(
    "S3 bucket %s must have encryption enabled",
    [resource.address]
  )
}

has_encryption(resource) {
  # Check if encryption config exists
  config := resource.change.after
  config.server_side_encryption_configuration != null
}
```

## Security Scanning

### Pre-commit Checks

**Run security scans before commit:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_tfsec
      - id: terraform_checkov
        args:
          - --args=--framework terraform
```

### CI/CD Security Gates

**Block insecure changes:**
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false  # Fail pipeline on issues
          
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          soft_fail: false
```

## Security Checklist

### Infrastructure Security
- [ ] All data encrypted at rest (Cloud Storage, Cloud SQL, Compute Engine disks)
- [ ] All data encrypted in transit (TLS/SSL)
- [ ] Firewall rules follow least privilege
- [ ] No public access to databases
- [ ] VPC Flow Logs enabled
- [ ] Cloud Audit Logs enabled for audit logging

### Access Control
- [ ] IAM roles use least privilege
- [ ] No hard-coded credentials
- [ ] Secrets stored in Secret Manager
- [ ] Service-specific service accounts
- [ ] MFA required for sensitive operations
- [ ] Regular access review process

### Code Security
- [ ] No secrets in version control
- [ ] Sensitive variables marked as sensitive
- [ ] Security scanning in CI/CD
- [ ] Pre-commit hooks configured
- [ ] Code review required
- [ ] Branch protection enabled

### Compliance
- [ ] Required labels on all resources
- [ ] Naming conventions enforced
- [ ] Policy as code implemented
- [ ] Regular security audits
- [ ] Compliance reporting automated
- [ ] Disaster recovery plan documented
