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
  default = "baa6e82f83db46709f7180f31b3f7132"
}
