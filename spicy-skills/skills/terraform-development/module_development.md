# Module Development Guide

Comprehensive guide for creating production-ready Terraform modules.

## Module Structure

Standard module layout:

```
terraform-google-module/
├── README.md                 # Module documentation
├── main.tf                   # Primary resources
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── versions.tf               # Provider version constraints
├── examples/                 # Usage examples
│   ├── basic/
│   │   ├── main.tf
│   │   └── README.md
│   └── complete/
│       ├── main.tf
│       └── README.md
├── modules/                  # Submodules (optional)
│   └── submodule/
└── tests/                    # Automated tests (optional)
```

## Module Creation Workflow

### Step 1: Define Module Interface

Create clear, documented inputs:

```hcl
# variables.tf
variable "network_name" {
  type        = string
  description = "Name of the VPC network"
  
  validation {
    condition     = can(regex("^[a-z][-a-z0-9]*[a-z0-9]$", var.network_name))
    error_message = "Network name must start with a letter, contain only lowercase letters, numbers, and hyphens."
  }
}

variable "subnets" {
  type = list(object({
    subnet_name   = string
    subnet_ip     = string
    subnet_region = string
  }))
  description = "List of subnets to create"
  
  validation {
    condition     = length(var.subnets) >= 1
    error_message = "At least 1 subnet required."
  }
}

variable "labels" {
  type        = map(string)
  description = "Common labels to apply to all resources"
  default     = {}
}
```

### Step 2: Implement Core Logic

Use resource modules for grouped functionality:

```hcl
# main.tf
resource "google_compute_network" "this" {
  name                    = var.network_name
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "this" {
  for_each = { for subnet in var.subnets : subnet.subnet_name => subnet }
  
  name          = each.value.subnet_name
  ip_cidr_range = each.value.subnet_ip
  region        = each.value.subnet_region
  network       = google_compute_network.this.id
  project       = var.project_id
  
  private_ip_google_access = var.enable_private_google_access
  
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Use dynamic blocks for optional features
resource "google_compute_firewall" "this" {
  for_each = var.firewall_rules

  name    = each.key
  network = google_compute_network.this.name
  project = var.project_id

  dynamic "allow" {
    for_each = each.value.allow
    content {
      protocol = allow.value.protocol
      ports    = lookup(allow.value, "ports", null)
    }
  }

  source_ranges = lookup(each.value, "source_ranges", null)
  source_tags   = lookup(each.value, "source_tags", null)
  target_tags   = lookup(each.value, "target_tags", null)
}
```

### Step 3: Define Outputs

Export useful values for consumers:

```hcl
# outputs.tf
output "network_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.this.id
}

output "network_self_link" {
  description = "URI of the VPC network"
  value       = google_compute_network.this.self_link
}

output "subnet_ids" {
  description = "Map of subnet names to IDs"
  value       = { for k, v in google_compute_subnetwork.this : k => v.id }
}

output "subnet_self_links" {
  description = "Map of subnet names to self links"
  value       = { for k, v in google_compute_subnetwork.this : k => v.self_link }
}
```

### Step 4: Version Constraints

Pin provider versions for consistency:

```hcl
# versions.tf
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

### Step 5: Document the Module

Create comprehensive README using terraform-docs:

```bash
# Install terraform-docs
brew install terraform-docs

# Generate documentation
terraform-docs markdown table . > README.md
```

Manual README template:

```markdown
# GCP VPC Module

Terraform module for creating GCP VPC networks with best practices.

## Features

- Custom mode VPC network
- Multiple subnets across regions
- VPC Flow Logs enabled
- Private Google Access support

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  project_id   = "my-project-id"
  network_name = "production-vpc"
  
  subnets = [
    {
      subnet_name   = "subnet-us-central1"
      subnet_ip     = "10.10.10.0/24"
      subnet_region = "us-central1"
    },
    {
      subnet_name   = "subnet-us-east1"
      subnet_ip     = "10.10.20.0/24"
      subnet_region = "us-east1"
    }
  ]
  
  labels = {
    environment = "production"
    managed_by  = "terraform"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.5.0 |
| google | ~> 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| network_name | Name of VPC network | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| network_id | ID of the VPC network |
```

## Module Best Practices

### 1. Use Consistent Variable Patterns

**Type definitions:**
```hcl
# String for single values
variable "vpc_name" {
  type = string
}

# List for multiple values of same type
variable "availability_zones" {
  type = list(string)
}

# Map for key-value pairs
variable "tags" {
  type = map(string)
}

# Object for structured data
variable "vpc_config" {
  type = object({
    cidr              = string
    enable_dns        = bool
    secondary_cidrs   = optional(list(string), [])
  })
}
```

### 2. Implement Robust Validation

```hcl
variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  
  validation {
    condition     = can(regex("^t[23]\\.", var.instance_type))
    error_message = "Only t2 and t3 instance types allowed for cost control."
  }
}

variable "backup_retention_days" {
  type        = number
  description = "Number of days to retain backups"
  default     = 7
  
  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 35
    error_message = "Retention must be between 7 and 35 days per compliance policy."
  }
}
```

### 3. Use Locals for Computed Values

```hcl
locals {
  # Common tags applied to all resources
  common_tags = merge(
    var.tags,
    {
      ManagedBy   = "Terraform"
      Module      = "vpc"
      CreatedDate = timestamp()
    }
  )
  
  # Compute subnet CIDRs
  private_subnet_cidrs = [
    for idx, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, idx)
  ]
  
  public_subnet_cidrs = [
    for idx, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, idx + length(var.availability_zones))
  ]
  
  # Conditional logic
  create_nat_gateway = var.enable_nat_gateway && length(var.availability_zones) > 0
}
```

### 4. Handle Optional Features

```hcl
# Conditional resource creation
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_s3_endpoint ? 1 : 0
  
  vpc_id       = aws_vpc.this.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
}

# Dynamic blocks for variable-length configurations
resource "aws_security_group" "this" {
  name        = var.security_group_name
  description = var.security_group_description
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

### 5. Use Data Sources Wisely

```hcl
# Get current project
data "google_project" "current" {}

# Get current client config
data "google_client_config" "current" {}

# Get latest container-optimized OS image
data "google_compute_image" "cos" {
  family  = "cos-stable"
  project = "cos-cloud"
}

# Use in resource
resource "google_compute_instance" "this" {
  name         = "web-server"
  machine_type = var.machine_type
  zone         = var.zone
  
  boot_disk {
    initialize_params {
      image = data.google_compute_image.cos.self_link
    }
  }
  
  network_interface {
    network = "default"
  }
}
```

### 6. Implement Lifecycle Rules

```hcl
resource "google_compute_instance" "this" {
  name         = "critical-server"
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
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_compute_firewall" "this" {
  name    = var.firewall_name
  network = var.network
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
  
  # Ignore changes made outside Terraform
  lifecycle {
    ignore_changes = [
      description,
      labels["last_modified"]
    ]
  }
}

resource "google_sql_database_instance" "this" {
  name             = var.database_name
  database_version = "POSTGRES_14"
  region           = var.region
  
  settings {
    tier = "db-f1-micro"
  }
  
  # Create new before destroying old
  lifecycle {
    create_before_destroy = true
  }
}
```

## Advanced Module Patterns

### Submodules for Complex Logic

```
terraform-google-gke/
├── main.tf                   # GKE cluster
├── modules/
│   ├── node-pool/           # Node pools submodule
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── iam/                 # IAM roles submodule
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── examples/
```

Usage:
```hcl
# In parent module main.tf
module "node_pool" {
  source = "./modules/node-pool"
  
  project_id      = var.project_id
  cluster_name    = google_container_cluster.this.name
  location        = var.region
  node_count      = var.node_count
  machine_type    = var.node_machine_type
  disk_size_gb    = var.node_disk_size
  service_account = module.iam.node_service_account
}
```

### Module Composition

Reference other modules for complete solutions:

```hcl
# infrastructure-module/main.tf
module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 9.0"
  
  project_id   = var.project_id
  network_name = "app-vpc"
  
  subnets = [
    {
      subnet_name   = "gke-subnet"
      subnet_ip     = "10.0.0.0/24"
      subnet_region = "us-central1"
    }
  ]
}

module "gke" {
  source  = "terraform-google-modules/kubernetes-engine/google"
  version = "~> 30.0"
  
  project_id        = var.project_id
  name              = "app-cluster"
  region            = "us-central1"
  network           = module.vpc.network_name
  subnetwork        = module.vpc.subnets_names[0]
  ip_range_pods     = "gke-pods"
  ip_range_services = "gke-services"
}

module "cloud_sql" {
  source  = "terraform-google-modules/sql-db/google//modules/postgresql"
  version = "~> 18.0"
  
  project_id       = var.project_id
  name             = "app-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"
  
  ip_configuration = {
    ipv4_enabled        = false
    private_network     = module.vpc.network_self_link
    require_ssl         = true
    allocated_ip_range  = "google-managed-services"
  }
}
```

### For_each for Resource Collections

```hcl
# Create multiple similar resources
variable "databases" {
  type = map(object({
    database_version = string
    tier             = string
    disk_size        = number
    region           = string
  }))
  
  default = {
    "app-db" = {
      database_version = "POSTGRES_14"
      tier             = "db-custom-2-7680"
      disk_size        = 100
      region           = "us-central1"
    }
    "analytics-db" = {
      database_version = "POSTGRES_14"
      tier             = "db-custom-4-15360"
      disk_size        = 500
      region           = "us-central1"
    }
  }
}

resource "google_sql_database_instance" "this" {
  for_each = var.databases
  
  name             = each.key
  database_version = each.value.database_version
  region           = each.value.region
  
  settings {
    tier      = each.value.tier
    disk_size = each.value.disk_size
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_self_link
      require_ssl     = true
    }
  }
  
  labels = merge(
    var.labels,
    {
      name = each.key
    }
  )
}
```

## Testing Modules

Create example configurations in `examples/`:

```hcl
# examples/basic/main.tf
module "vpc" {
  source = "../.."  # Reference parent module
  
  vpc_name           = "example-vpc"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  
  enable_nat_gateway = true
  
  tags = {
    Environment = "test"
    Example     = "basic"
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

## Publishing Modules

### Version Tagging

Use semantic versioning:
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

### Terraform Registry

For public modules, publish to Terraform Registry:

1. Repository name format: `terraform-<PROVIDER>-<NAME>`
2. Add required files: README, LICENSE
3. Tag releases with semantic versions
4. Register at registry.terraform.io

### Private Registry

For private modules:
```hcl
module "vpc" {
  source  = "app.terraform.io/my-org/vpc/aws"
  version = "~> 2.0"
  
  # ... configuration
}
```
