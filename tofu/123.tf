resource "openstack_containerinfra_cluster_v1" "k8s_123_2" {
  name                = "quarry-123-2"
  cluster_template_id = resource.openstack_containerinfra_clustertemplate_v1.template_123_2.id
  master_count        = 1
  node_count          = 2
}

resource "local_file" "kube_config" {
  content  = resource.openstack_containerinfra_cluster_v1.k8s_123_2.kubeconfig.raw_config
  filename = "kube.config"
}

resource "openstack_containerinfra_clustertemplate_v1" "template_123_2" {
  name                  = "quarry-123-2"
  coe                   = "kubernetes"
  dns_nameserver        = "8.8.8.8"
  docker_storage_driver = "overlay2"
  docker_volume_size    = 20
  external_network_id   = "wan-transport-eqiad"
  fixed_subnet          = "cloud-instances2-b-eqiad"
  fixed_network         = "lan-flat-cloudinstances2b"
  flavor                = "g3.cores4.ram8.disk20"
  floating_ip_enabled   = "false"
  image                 = "Fedora-CoreOS-38"
  master_flavor         = "g3.cores2.ram4.disk20"
  network_driver        = "flannel"

  labels = {
    kube_tag               = "v1.23.15-rancher1-linux-amd64"
    hyperkube_prefix       = "docker.io/rancher/"
    cloud_provider_enabled = "true"
  }
}
