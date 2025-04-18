#!/bin/bash

set -e  # Exit on error

echo
if [ "$USE_TERRAFORM"=="true" ]; then
	echo '1. INSTALLING TERRAFORM'
	echo
else
	echo 'TERRAFORM is not used.'	
	exit 0
fi

# copy GOOGLE_APPLICATION_CREDENTIALS to terraform subfolder
cp -r gcp terraform

cd terraform

apt-get update && apt-get install -y wget unzip
wget --quiet https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip
unzip terraform_1.5.7_linux_amd64.zip
mv terraform /usr/bin
rm terraform_1.5.7_linux_amd64.zip

echo
echo '2. CHECKING GCP CREDENTIALS'
echo
if [[ -e "$GOOGLE_APPLICATION_CREDENTIALS" ]]
  then
    echo "GOOGLE_APPLICATION_CREDENTIALS file found. "$GOOGLE_APPLICATION_CREDENTIALS
else
    echo "No GOOGLE_APPLICATION_CREDENTIALS file with key paramaters found. Exiting."
    exit 1
fi


echo
echo '3. DEPLOYING TERRAFORM'
echo

echo "Terraform: Initializing..."
terraform init

echo "Terraform: Creating plan..."
terraform plan -var="project="$GCP_PROJECT_NAME -var="bq_dataset_name="$BQ_DATASET -var="bucket_name="$GCS_BUCKET

echo "Terraform: Applying configuration..."
terraform apply -auto-approve

echo "Terraform: Deployment complete!"
