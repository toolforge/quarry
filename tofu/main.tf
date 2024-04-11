terraform {
  required_version = "= 1.6.2"
  backend "s3" {
    region   = "eqiad1"
    bucket   = "quarry:tofu-state"
    endpoint = "https://object.eqiad1.wikimediacloud.org"
    key      = "state/main"

    skip_region_validation      = true
    skip_credentials_validation = true
    force_path_style            = true
  }

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
