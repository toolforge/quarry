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
  default = "4917ce71b98e498e8a6c5814b095b28e"
}
