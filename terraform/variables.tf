variable "project" {
  description = "Project"
  default     = "my-project-test-01-421509"
}

variable "region" {
  description = "Region"
  default     = "us-west1"
}

variable "location" {
  description = "GCS Bucket and BQ Location"
  default     = "us-west1"
}


variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "stocks"
}

# if bucket_name left empty it will not be created!
variable "bucket_name" {
  description = "The name of the GCS bucket for raw data"
  type        = string
  default	  = ""
}

