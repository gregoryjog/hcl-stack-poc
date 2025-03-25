# --- child_modules/ami/variables.tf


variable "distro" {
  type        = string
  description = "Linux Distro to Use"

  validation {
    condition     = contains(["ubuntu", "rhel", "amazon"], lower(var.distro))
    error_message = "Invalid Linux distribution specified"
  }
}