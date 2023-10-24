# probably replace with (import) active database before deploy
resource "openstack_db_instance_v1" "mariadb" {
  region    = "eqiad1-r"
  name      = "quarry-k8s-test"
  flavor_id = "bb8bee7e-d8f9-460b-8344-74f745c139b9"
  size      = 10

  network {
    uuid = "7425e328-560c-4f00-8e99-706f3fb90bb4"
  }

  user {
    name      = "quarry"
    host      = "%"
    password  = var.db_password
    databases = ["quarry"]
  }

  database {
    name = "quarry"
  }

  datastore {
    version = "10.5.10"
    type    = "mariadb"
  }
}

