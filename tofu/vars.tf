# connection vars
variable "auth-url" {
  type = string
  default = "https://openstack.eqiad1.wikimediacloud.org:25000"
}
variable "tenant_id" {
  type = string
  default = "quarry"
}
variable "application_credential_id" {
  type = string
  default = "5219385175b34239be24de627ec7b7cf"
}
