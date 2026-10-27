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
  default = "f87c4ec574684cefb5b638ef3a4f1c71"
}
