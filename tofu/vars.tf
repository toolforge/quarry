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
  default = "446ab9c3713b4a0b8c2da540021dd314"
}
