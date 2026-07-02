# Terraform Troubleshooting Guide

Common issues and solutions for Terraform operations.

## State Issues

### State Lock Errors

**Error:**
```
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional
request failed
Lock Info:
  ID:        abc123-def456
  Path:      s3://bucket/terraform.tfstate
  Operation: OperationTypeApply
  Who:       user@hostname
  Created:   2024-01-15 10:30:00
```

**Causes:**
- Another terraform process is running
- Previous run crashed without releasing lock
- Network interruption during operation

**Solutions:**

1. **Check if process is actually running:**
```bash
# On Unix/Linux
ps aux | grep terraform

# On the machine shown in lock info
ssh user@hostname "ps aux | grep terraform"
```

2. **If no process is running, force unlock:**
```bash
# Get lock ID from error message
terraform force-unlock abc123-def456

# Terraform will ask for confirmation
# Type 'yes' only if you're certain no process is running
```

3. **Prevention:**
```bash
# Use proper process management
terraform apply || {
  echo "Apply failed"
  exit 1
}
# Don't automatically force-unlock in scripts
```

### State File Corruption

**Error:**
```
Error: Failed to load state: state snapshot was created by Terraform v1.5.0, 
which is newer than current v1.4.0
```

**Solution:**
```bash
# Upgrade Terraform to required version
tfenv install 1.5.0
tfenv use 1.5.0

# Verify version
terraform version
```

**Error:**
```
Error: state data in S3 does not have the expected content
```

**Solutions:**

1. **Restore from backup:**
```bash
# List S3 versions
aws s3api list-object-versions \
  --bucket my-terraform-state \
  --prefix terraform.tfstate

# Download previous version
aws s3api get-object \
  --bucket my-terraform-state \
  --key terraform.tfstate \
  --version-id <VERSION_ID> \
  terraform.tfstate.backup

# Restore
terraform state push terraform.tfstate.backup
```

2. **Rebuild from infrastructure:**
```bash
# Last resort - import existing resources
terraform import aws_instance.web i-1234567890abcdef0
```

### Drift Detection

**Scenario:** State doesn't match real infrastructure

**Detection:**
```bash
# Run plan to see drift
terraform plan

# Expected: No changes
# If changes appear, infrastructure was modified outside Terraform
```

**Solutions:**

1. **Refresh state:**
```bash
# Update state to match reality
terraform apply -refresh-only

# Review changes before accepting
```

2. **Accept manual changes:**
```bash
# If manual changes are correct, update code to match
# Then run plan to verify
terraform plan  # Should show no changes
```

3. **Revert manual changes:**
```bash
# Apply Terraform configuration to revert
terraform apply
```

## Dependency Issues

### Cycle Errors

**Error:**
```
Error: Cycle: aws_security_group.app, aws_security_group.db
```

**Cause:** Circular dependency between resources

**Example problem:**
```hcl
resource "aws_security_group" "app" {
  egress {
    security_groups = [aws_security_group.db.id]  # app depends on db
  }
}

resource "aws_security_group" "db" {
  ingress {
    security_groups = [aws_security_group.app.id]  # db depends on app
  }
}
```

**Solution - Use separate rules:**
```hcl
resource "aws_security_group" "app" {
  # No references to db security group
}

resource "aws_security_group" "db" {
  # No references to app security group
}

# Separate rule resources break the cycle
resource "aws_security_group_rule" "app_to_db" {
  type                     = "egress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.db.id
}

resource "aws_security_group_rule" "db_from_app" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.app.id
}
```

### Implicit Dependencies

**Issue:** Resources created in wrong order

**Problem:**
```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  subnet_id     = aws_subnet.public.id  # Explicit dependency
  
  user_data = templatefile("setup.sh", {
    db_endpoint = aws_db_instance.main.endpoint  # Implicit dependency
  })
}
```

**Solution - Make explicit:**
```hcl
resource "aws_instance" "web" {
  ami       = var.ami_id
  subnet_id = aws_subnet.public.id
  
  user_data = templatefile("setup.sh", {
    db_endpoint = aws_db_instance.main.endpoint
  })
  
  # Explicit dependency ensures correct order
  depends_on = [aws_db_instance.main]
}
```

## Provider Issues

### Provider Version Conflicts

**Error:**
```
Error: Inconsistent dependency lock file

Provider hashicorp/aws is required by the following modules:
  - root module: version ~> 5.0
  - module.vpc: version ~> 4.0
```

**Solution:**
```hcl
# Align versions across all modules
# In root module
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# In vpc module - update to match
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### Provider Authentication Errors

**Error:**
```
Error: error configuring Terraform AWS Provider: 
no valid credential sources for Terraform AWS Provider found
```

**Solutions:**

1. **AWS credentials:**
```bash
# Environment variables
export AWS_ACCESS_KEY_ID="xxx"
export AWS_SECRET_ACCESS_KEY="xxx"
export AWS_DEFAULT_REGION="us-east-1"

# Or use AWS CLI profile
export AWS_PROFILE="production"

# Verify
aws sts get-caller-identity
```

2. **Azure credentials:**
```bash
# Service principal
export ARM_CLIENT_ID="xxx"
export ARM_CLIENT_SECRET="xxx"
export ARM_SUBSCRIPTION_ID="xxx"
export ARM_TENANT_ID="xxx"

# Or use Azure CLI
az login
```

3. **GCP credentials:**
```bash
# Service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Or use gcloud
gcloud auth application-default login
```

## Module Issues

### Module Not Found

**Error:**
```
Error: Module not installed

Module module.vpc (from ./modules/vpc) is not yet installed
```

**Solution:**
```bash
# Initialize to download modules
terraform init

# Force redownload
terraform init -upgrade
```

### Module Version Conflicts

**Error:**
```
Error: Failed to query available provider packages

The module "vpc" requires version ~> 3.0 of the AWS provider,
but the current version is 5.0.0
```

**Solution:**
```hcl
# Update module version requirement
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"  # Update to compatible version
}
```

### Module Source Issues

**Error:**
```
Error: Module not found

The module address "github.com/org/repo" could not be resolved
```

**Solutions:**

1. **Verify URL:**
```hcl
# Correct format for GitHub
module "example" {
  source = "git::https://github.com/org/repo.git?ref=v1.0.0"
}

# Or using SSH
module "example" {
  source = "git::ssh://git@github.com/org/repo.git?ref=v1.0.0"
}
```

2. **Check credentials:**
```bash
# For private repos
git config --global credential.helper store

# Or use SSH
ssh -T git@github.com
```

## Resource Errors

### Resource Already Exists

**Error:**
```
Error: ResourceAlreadyExists: Resource 'my-bucket' already exists
```

**Solutions:**

1. **Import existing resource:**
```bash
# Find resource ID
aws s3 ls | grep my-bucket

# Import into state
terraform import aws_s3_bucket.data my-bucket

# Verify
terraform plan  # Should show no changes
```

2. **Use different name:**
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-bucket-${data.aws_caller_identity.current.account_id}"
}
```

### Cannot Destroy Resource

**Error:**
```
Error: Error deleting S3 Bucket: BucketNotEmpty

The bucket you tried to delete is not empty
```

**Solutions:**

1. **Force empty bucket:**
```hcl
resource "aws_s3_bucket" "data" {
  bucket        = "my-bucket"
  force_destroy = true  # Delete even if not empty
}
```

2. **Manual cleanup:**
```bash
# Empty bucket first
aws s3 rm s3://my-bucket --recursive

# Then destroy
terraform destroy
```

**Error:**
```
Error: deleting EC2 Instance: DependencyViolation

Resource has a dependent object
```

**Solution:**
```hcl
# Change destroy order
resource "aws_network_interface" "app" {
  # ...
}

resource "aws_instance" "app" {
  network_interface {
    network_interface_id = aws_network_interface.app.id
  }
  
  # Destroy instance before interface
  depends_on = [aws_network_interface.app]
}
```

## Performance Issues

### Slow Plan/Apply

**Issue:** Plan takes too long

**Causes:**
- Too many resources in one state
- Slow provider API
- Large number of data sources

**Solutions:**

1. **Split state:**
```
# Instead of one monolithic state:
infrastructure/terraform.tfstate (5000 resources)

# Split into:
networking/terraform.tfstate (100 resources)
compute/terraform.tfstate (200 resources)
database/terraform.tfstate (50 resources)
```

2. **Use targeted operations:**
```bash
# Only plan specific resources
terraform plan -target=aws_instance.web

# Apply only changed resources
terraform apply -target=module.vpc
```

3. **Reduce data source queries:**
```hcl
# Instead of querying same data multiple times
data "aws_ami" "ubuntu" {
  # This runs once per resource that uses it
}

# Use locals
locals {
  ubuntu_ami = data.aws_ami.ubuntu.id
}

resource "aws_instance" "web" {
  ami = local.ubuntu_ami
}
```

4. **Enable parallelism:**
```bash
# Increase parallel operations (default is 10)
terraform apply -parallelism=20
```

### Memory Issues

**Error:**
```
Fatal error: out of memory
```

**Solutions:**

1. **Increase memory limits:**
```bash
# Adjust Go memory settings
export GOGC=20
export GOMEMLIMIT=8GiB

terraform apply
```

2. **Reduce state size:**
```bash
# Check state size
terraform state pull | wc -c

# If > 10MB, consider splitting
```

## Debugging

### Enable Debug Logging

**All debug output:**
```bash
export TF_LOG=DEBUG
terraform plan

# Save to file
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform-debug.log
terraform apply
```

**Specific log levels:**
```bash
export TF_LOG=TRACE  # Most verbose
export TF_LOG=DEBUG
export TF_LOG=INFO
export TF_LOG=WARN
export TF_LOG=ERROR
```

**Provider-specific logging:**
```bash
# AWS provider debug
export TF_LOG_PROVIDER=DEBUG
export TF_LOG_CORE=WARN  # Less verbose core logs

terraform apply
```

### Crash Reports

**Location:**
```
crash.log  # In current directory
```

**What to do:**
1. Check crash.log for error details
2. Search GitHub issues: github.com/hashicorp/terraform/issues
3. Create bug report with:
   - Terraform version
   - Provider version
   - Minimal reproduction case
   - Crash log

### Common Error Patterns

**Invalid address:**
```
Error: Invalid reference

aws_instance.web.id cannot be referenced here
```
**Cause:** Referencing resource that doesn't exist or typo

**Solution:**
```bash
# List all resources
terraform state list

# Verify correct name
terraform state show aws_instance.web
```

**Invalid interpolation:**
```
Error: Invalid template interpolation value

The expression result cannot be used in a string template
```

**Cause:** Trying to interpolate null or wrong type

**Solution:**
```hcl
# Add null check
resource "aws_instance" "web" {
  tags = {
    # Instead of:
    # Name = var.name
    
    # Use:
    Name = var.name != null ? var.name : "default"
  }
}
```

## Best Practices for Troubleshooting

### Before Making Changes

1. **Create backup:**
```bash
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate
```

2. **Document the issue:**
- What changed?
- What's the error?
- Expected vs actual behavior

3. **Test in non-production:**
```bash
# Copy production config to test
terraform workspace new test
terraform apply  # Test fix here first
```

### Investigation Steps

1. **Review recent changes:**
```bash
git log --oneline --since="1 week ago"
git diff HEAD~1 HEAD
```

2. **Check provider status:**
- AWS: status.aws.amazon.com
- Azure: status.azure.com
- GCP: status.cloud.google.com

3. **Validate configuration:**
```bash
terraform fmt -check
terraform validate
```

4. **Review plan carefully:**
```bash
terraform plan -out=tfplan
terraform show tfplan  # Detailed view
```

### Recovery Procedures

**If apply fails mid-run:**
1. Don't panic - state may be partially updated
2. Review error message carefully
3. Run `terraform plan` to see current state
4. Fix underlying issue
5. Run `terraform apply` again - Terraform will resume

**If state is corrupted:**
1. Try `terraform state pull` - if this fails, state is badly corrupted
2. Restore from S3 version (if using S3 backend)
3. Restore from local backup
4. Last resort: `terraform import` all resources

## Quick Reference

| Issue | Command |
|-------|---------|
| State locked | `terraform force-unlock <ID>` |
| Need to refresh state | `terraform apply -refresh-only` |
| Import resource | `terraform import <address> <id>` |
| Remove from state | `terraform state rm <address>` |
| View resource | `terraform state show <address>` |
| List all resources | `terraform state list` |
| Enable debug logs | `export TF_LOG=DEBUG` |
| Target specific resource | `terraform apply -target=<address>` |
| Upgrade providers | `terraform init -upgrade` |
