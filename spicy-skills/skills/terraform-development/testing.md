# Terraform Testing Guide

Comprehensive testing strategies for Terraform code.

## Testing Pyramid

```
           ╱╲
          ╱  ╲        Integration Tests
         ╱────╲       (Terratest, Kitchen-Terraform)
        ╱      ╲
       ╱────────╲     Unit Tests
      ╱          ╲    (terraform validate, tflint)
     ╱────────────╲
    ╱              ╲  Static Analysis
   ╱────────────────╲ (checkov, tfsec, terrascan)
```

## Level 1: Static Analysis

Run before commit - catches syntax and security issues without deployment.

### terraform fmt

Format code consistently:

```bash
# Check formatting
terraform fmt -check -recursive

# Fix formatting
terraform fmt -recursive

# In CI/CD
terraform fmt -check -recursive || exit 1
```

### terraform validate

Validate syntax and internal consistency:

```bash
terraform init -backend=false
terraform validate

# Detailed output
terraform validate -json
```

**Common validation errors:**
- Missing required arguments
- Invalid resource types
- Circular dependencies
- Invalid interpolations

### tflint

Advanced linting for provider-specific issues:

```bash
# Install
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Initialize (downloads provider plugins)
tflint --init

# Run
tflint

# With specific config
tflint --config=.tflint.hcl
```

**.tflint.hcl configuration:**
```hcl
plugin "aws" {
  enabled = true
  version = "0.30.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "aws_instance_invalid_type" {
  enabled = true
}
```

### Security Scanning

#### Checkov

Comprehensive policy-as-code scanning:

```bash
# Install
pip install checkov

# Scan directory
checkov -d .

# Scan specific file
checkov -f main.tf

# Output as JSON
checkov -d . -o json

# Skip specific checks
checkov -d . --skip-check CKV_AWS_20,CKV_AWS_21

# Custom policies
checkov -d . --external-checks-dir ./custom-policies
```

**Example custom policy (Python):**
```python
# custom-policies/vpc_flow_logs.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class VPCFlowLogsEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VPC has flow logs enabled"
        id = "CKV_AWS_CUSTOM_1"
        supported_resources = ['aws_vpc']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Check if VPC has flow logs enabled
        # This is simplified - actual check would verify flow logs exist
        return CheckResult.PASSED

check = VPCFlowLogsEnabled()
```

#### tfsec

Fast security scanning:

```bash
# Install
brew install tfsec

# Scan
tfsec .

# Specific formats
tfsec . --format json
tfsec . --format sarif -o results.sarif

# Exclude checks
tfsec . --exclude-rule aws-vpc-no-public-ingress-sgr

# Minimum severity
tfsec . --minimum-severity HIGH
```

**Inline exclusions:**
```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Example security group"
  
  # tfsec:ignore:aws-vpc-no-public-ingress-sgr
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Level 2: Unit Testing

Test individual components without deploying infrastructure.

### terraform-compliance

BDD-style compliance testing:

```bash
# Install
pip install terraform-compliance

# Generate plan
terraform plan -out=plan.out
terraform show -json plan.out > plan.json

# Run tests
terraform-compliance -f tests/ -p plan.json
```

**Example test (tests/security.feature):**
```gherkin
Feature: Security compliance
  Scenario: Ensure S3 buckets are encrypted
    Given I have aws_s3_bucket defined
    Then it must contain server_side_encryption_configuration

  Scenario: Ensure RDS instances are encrypted
    Given I have aws_db_instance defined
    Then it must contain storage_encrypted
    And its value must be true

  Scenario: Ensure security groups don't allow all traffic
    Given I have aws_security_group defined
    When it contains ingress
    Then it must not have cidr_blocks
    Or it must not contain 0.0.0.0/0
```

### Sentinel (Terraform Cloud/Enterprise)

Policy as code for Terraform Cloud:

```hcl
# policies/cost-control.sentinel
import "tfplan/v2" as tfplan

# Allowed instance types for cost control
allowed_types = ["t2.micro", "t2.small", "t3.micro", "t3.small"]

# Find all EC2 instances
instances = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_instance" and
  rc.mode is "managed" and
  (rc.change.actions contains "create" or rc.change.actions contains "update")
}

# Main rule
main = rule {
  all instances as _, instance {
    instance.change.after.instance_type in allowed_types
  }
}
```

**Policy set:**
```hcl
# policy-set.hcl
policy "cost-control" {
  source = "./cost-control.sentinel"
  enforcement_level = "hard-mandatory"
}

policy "required-tags" {
  source = "./required-tags.sentinel"
  enforcement_level = "soft-mandatory"
}
```

## Level 3: Integration Testing

Deploy to sandbox environments and validate.

### Terratest

Go-based testing framework:

```go
// test/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        // Path to Terraform code
        TerraformDir: "../examples/basic",
        
        // Variables to pass
        Vars: map[string]interface{}{
            "vpc_name": "test-vpc",
            "vpc_cidr": "10.0.0.0/16",
            "availability_zones": []string{"us-east-1a", "us-east-1b"},
        },
        
        // Disable colors in output
        NoColor: true,
    }

    // Clean up resources at the end
    defer terraform.Destroy(t, terraformOptions)

    // Run terraform init and apply
    terraform.InitAndApply(t, terraformOptions)

    // Validate outputs
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
    
    vpcCidr := terraform.Output(t, terraformOptions, "vpc_cidr")
    assert.Equal(t, "10.0.0.0/16", vpcCidr)
    
    privateSubnetIds := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
    assert.Equal(t, 2, len(privateSubnetIds))
}

func TestVPCModuleWithNATGateway(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "enable_nat_gateway": true,
            "single_nat_gateway": false,
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Verify NAT gateways were created
    natGatewayIds := terraform.OutputList(t, terraformOptions, "nat_gateway_ids")
    assert.NotEmpty(t, natGatewayIds)
}
```

**Run tests:**
```bash
cd test
go mod init vpc-test
go mod tidy
go test -v -timeout 30m
```

**Advanced Terratest patterns:**
```go
// Validate actual AWS resources
func TestVPCExistsInAWS(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/basic",
    }
    
    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)
    
    // Get VPC ID from output
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    
    // Verify VPC exists in AWS
    awsRegion := "us-east-1"
    vpc := aws.GetVpcById(t, vpcId, awsRegion)
    
    assert.Equal(t, vpcId, *vpc.VpcId)
    assert.Equal(t, "available", *vpc.State)
}
```

### Kitchen-Terraform

Ruby-based testing with InSpec:

**kitchen.yml:**
```yaml
driver:
  name: terraform
  root_module_directory: test/fixtures/basic

provisioner:
  name: terraform

verifier:
  name: terraform
  systems:
    - name: basic
      backend: aws
      controls:
        - vpc_exists
        - subnets_exist

platforms:
  - name: terraform

suites:
  - name: default
    verifier:
      systems:
        - name: basic
          backend: aws
          profile_locations:
            - test/integration/basic
```

**InSpec tests (test/integration/basic/controls/vpc.rb):**
```ruby
vpc_id = attribute('vpc_id', description: 'The VPC ID')

control 'vpc_exists' do
  impact 1.0
  title 'VPC should exist'
  
  describe aws_vpc(vpc_id) do
    it { should exist }
    its('cidr_block') { should eq '10.0.0.0/16' }
    its('state') { should eq 'available' }
  end
end

control 'subnets_exist' do
  impact 1.0
  title 'Subnets should exist'
  
  describe aws_subnets.where(vpc_id: vpc_id) do
    its('count') { should be >= 2 }
  end
end
```

## Level 4: Plan Validation

Validate terraform plan output before apply.

### terraform-plan-validator

Custom validation scripts:

```bash
#!/bin/bash
# scripts/validate-plan.sh

# Generate plan
terraform plan -out=tfplan
terraform show -json tfplan > plan.json

# Check for resource destruction
destroyed=$(jq '[.resource_changes[] | select(.change.actions[] | contains("delete"))] | length' plan.json)

if [ "$destroyed" -gt 0 ]; then
  echo "ERROR: Plan would destroy $destroyed resources"
  exit 1
fi

# Check for expensive resources
large_instances=$(jq '[.resource_changes[] | 
  select(.type == "aws_instance") | 
  select(.change.after.instance_type | test("^(c5|m5|r5)\\.(9|12|16|18|24)xlarge$"))] | 
  length' plan.json)

if [ "$large_instances" -gt 0 ]; then
  echo "WARNING: Plan includes $large_instances large instance types"
fi

echo "Plan validation passed"
```

### OPA (Open Policy Agent)

Advanced policy validation:

```rego
# policies/cost_control.rego
package terraform.cost

import future.keywords.contains
import future.keywords.if

# Allowed instance types
allowed_instance_types := {
    "t2.micro",
    "t2.small", 
    "t3.micro",
    "t3.small"
}

# Check if instance type is allowed
deny[msg] if {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    contains(resource.change.actions, "create")
    not allowed_instance_types[resource.change.after.instance_type]
    
    msg := sprintf(
        "Instance type %s not allowed. Allowed types: %v",
        [resource.change.after.instance_type, allowed_instance_types]
    )
}

# Check total cost estimate
deny[msg] if {
    total_monthly := sum([
        cost |
        resource := input.resource_changes[_]
        cost := estimate_cost(resource)
    ])
    
    total_monthly > 1000
    
    msg := sprintf("Estimated monthly cost $%.2f exceeds $1000 limit", [total_monthly])
}
```

**Run OPA:**
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json

opa eval --data policies/ --input plan.json 'data.terraform.cost.deny'
```

## Test Automation in CI/CD

### GitHub Actions

```yaml
# .github/workflows/terraform-test.yml
name: Terraform Test

on:
  pull_request:
    paths:
      - '**.tf'
      - '.github/workflows/terraform-test.yml'

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Format
        run: terraform fmt -check -recursive
      
      - name: Terraform Init
        run: terraform init -backend=false
      
      - name: Terraform Validate
        run: terraform validate
      
      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
        with:
          tflint_version: latest
      - run: tflint --init
      - run: tflint -f compact
      
      - name: Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          soft_fail: false
      
      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: .
          soft_fail: false

  unit-test:
    runs-on: ubuntu-latest
    needs: static-analysis
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Plan
        run: |
          terraform init
          terraform plan -out=tfplan
          terraform show -json tfplan > plan.json
      
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: terraform-plan
          path: plan.json

  integration-test:
    runs-on: ubuntu-latest
    needs: unit-test
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Run Terratest
        run: |
          cd test
          go test -v -timeout 30m
```

### Pre-commit Hooks

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
        args:
          - --hook-config=--path-to-file=README.md
          - --hook-config=--add-to-existing-file=true
          - --hook-config=--create-file-if-not-exist=true
      - id: terraform_tflint
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl
      - id: terraform_tfsec
      - id: terraform_checkov
        args:
          - --args=--quiet
          - --args=--skip-check CKV_AWS_20
```

**Install and use:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Testing Checklist

Before committing code:
- [ ] `terraform fmt` - Format code
- [ ] `terraform validate` - Validate syntax
- [ ] `tflint` - Run linter
- [ ] `checkov` or `tfsec` - Security scan
- [ ] `terraform plan` - Generate and review plan

Before merging PR:
- [ ] All static analysis passed
- [ ] Plan reviewed and approved
- [ ] Unit tests passed
- [ ] Documentation updated

Before production deploy:
- [ ] Integration tests passed in staging
- [ ] Manual verification completed
- [ ] Rollback plan documented
- [ ] Change approved by stakeholders
