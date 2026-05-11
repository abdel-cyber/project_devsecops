variable "aws_region" {
  description = "Région AWS"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Nom du projet"
  type        = string
  default     = "secnotes"
}

variable "cluster_name" {
  description = "Nom du cluster EKS"
  type        = string
  default     = "secnotes-eks"
}
