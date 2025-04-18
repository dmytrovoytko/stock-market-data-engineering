terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.28.0"
    }
  }
}

provider "google" {
# creds has been set through the GOOGLE_APPLICATION_CREDENTIALS environment variable.
# To reproduce, see setup.sh
  project = var.project
  region  = var.region
}


resource "google_bigquery_dataset" "my-dataset" {
  dataset_id = var.bq_dataset_name
  project    = var.project
  location   = var.location
}

# Storage resources - optional if bucket_name set
resource "google_storage_bucket" "data_bucket" {
  count = var.bucket_name=="" ? 0 : 1
  name          = var.bucket_name
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90  # Days
    }
    action {
      type = "Delete"
    }
  }
}
