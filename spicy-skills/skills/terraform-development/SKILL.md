---
name: terraform-development
description: >
  Guides Terraform/HCL configuration structure, module design, state
  management, and provider usage during both planning and implementation.
  Use when designing infrastructure, planning Terraform architecture, or
  writing .tf files. Triggers: 'terraform', 'tofu', 'HCL', '.tf', 'tfvars',
  'terraform plan', 'terraform apply', 'terraform module', 'provider',
  'resource block', infrastructure as code design. Does not apply to Pulumi,
  CDK, CloudFormation, Ansible, Kubernetes manifests, or Helm charts.
---

# Terraform Development Skill

Expert assistance for Terraform infrastructure as code, from basic configurations to enterprise-scale deployments.

## Quick Start

For immediate tasks, use these common patterns:

**Create a basic resource:**
```hcl
resource "google_compute_instance" "example" {
  name         = "example-instance"
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
  
  labels = {
    environment = var.environment
  }
}
```

**Define a variable with validation:**
```hcl
variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

## Core Workflows

### Creating New Infrastructure

1. **Define resources** - Start with required providers and resources
2. **Add variables** - Parameterize for reusability
3. **Format and validate** - Run `terraform fmt` and `terraform validate`
4. **Plan and review** - Execute `terraform plan` to preview changes
5. **Apply changes** - Run `terraform apply` after approval

### Building Modules

1. **Identify reusable patterns** - Group related resources
2. **Define clear interfaces** - Document inputs and outputs
3. **Implement validation** - Add variable validations
4. **Create examples** - Provide usage examples in `examples/`
5. **Document thoroughly** - Maintain README with terraform-docs

## When to Use Different Approaches

**Single configuration vs Modules:**
- Small projects (< 5 resources): Single configuration
- Reusable components: Resource modules
- Environment management: Infrastructure modules

**State management:**
- Local development: Local state (temporary only)
- Team collaboration: Remote state (S3, Terraform Cloud)
- Production: Remote state with locking and versioning

## Essential Patterns

### Remote State Configuration
```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "prod/terraform.tfstate"
  }
}
```

### Module Usage
```hcl
module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 9.0"

  project_id   = var.project_id
  network_name = "my-vpc"
  
  subnets = [
    {
      subnet_name   = "subnet-01"
      subnet_ip     = "10.10.10.0/24"
      subnet_region = "us-central1"
    },
    {
      subnet_name   = "subnet-02"
      subnet_ip     = "10.10.20.0/24"
      subnet_region = "us-central1"
    }
  ]
}
```

### Dynamic Blocks for Flexibility
```hcl
resource "google_compute_firewall" "example" {
  name    = "example-firewall"
  network = var.network_name

  dynamic "allow" {
    for_each = var.firewall_rules
    content {
      protocol = allow.value.protocol
      ports    = allow.value.ports
    }
  }
  
  source_ranges = var.source_ranges
}
```

## Advanced Topics

**Comprehensive module development:** See [module_development.md](module_development.md)
**Project structure patterns:** See [project_structure.md](project_structure.md)
**Testing strategies:** See [testing.md](testing.md)
**State management:** See [state_management.md](state_management.md)
**Security and secrets:** See [security.md](security.md)

## Common Commands Reference

**Initialize:** `terraform init` - Download providers and modules
**Format:** `terraform fmt -recursive` - Format all .tf files
**Validate:** `terraform validate` - Check syntax
**Plan:** `terraform plan -out=tfplan` - Preview changes
**Apply:** `terraform apply tfplan` - Execute changes
**Destroy:** `terraform destroy` - Remove all managed resources

**Debug:** `TF_LOG=DEBUG terraform plan` - Enable detailed logging

## Naming Conventions

Follow these patterns for consistency:

**Resources:** `<resource_type>.<descriptive_name>` (lowercase with underscores)
- ✓ `google_compute_instance.web_server`
- ✗ `google_compute_instance.WebServer` or `google_compute_instance.gcp-web-server`

**Variables:** Descriptive nouns (singular for single values, plural for lists)
- ✓ `machine_type`, `zones`
- ✗ `machineType`, `z`

**Modules:** Verb or noun phrases with hyphens
- ✓ `terraform-google-vpc`, `network-module`
- ✗ `VPC_Module`, `network_1`

## Critical Reminders

- **Never commit secrets** - Use environment variables or secret managers
- **Always use remote state** for team projects with locking enabled
- **Format before commit** - Run `terraform fmt` and `terraform validate`
- **Tag all resources** - Implement consistent tagging strategy
- **Version pin providers** - Specify `required_version` and provider versions
- **Use data sources** over hard-coded values when possible
- **Implement variable validation** for critical inputs
- **Test before apply** - Always review `terraform plan` output

## Quick Troubleshooting

**State locked:** Someone else is running Terraform, or previous run failed
- Check for running operations
- If confirmed safe: Force unlock with provided lock ID

**Provider version conflict:** Different versions required
- Pin versions in `required_providers` block
- Run `terraform init -upgrade` if intentional update

**Resource already exists:** Resource exists but not in state
- Use `terraform import` to add existing infrastructure
- Or rename/remove the conflicting resource

**Cycle error:** Circular dependency detected
- Review resource dependencies
- Use `depends_on` sparingly and explicitly

For detailed debugging, see [troubleshooting.md](troubleshooting.md)
