terraform {
  # license is incompatable at version 1.6.0
  required_version = "= 1.5.3"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.51.0"
    }
  }
}

provider "openstack" {
  auth_url                      = var.auth-url
  tenant_id                     = var.tenant_id
  application_credential_id     = var.application_credential_id
  application_credential_secret = var.application_credential_secret
}
