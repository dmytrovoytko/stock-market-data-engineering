#!/bin/bash

set -e  # Exit on error

echo "Terraform: Destroying resources..."
terraform destroy -auto-approve

echo "Terraform deployment destroyed!"
