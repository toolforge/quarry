resource "openstack_containerinfra_cluster_v1" "k8s_136" {
  name                = "quarry-136"
  cluster_template_id = resource.openstack_containerinfra_clustertemplate_v1.template_136.id
  master_count        = 1
  node_count          = 3
}

resource "local_file" "kube_config" {
  content  = resource.openstack_containerinfra_cluster_v1.k8s_136.kubeconfig.raw_config
  filename = "kube.config"
}

resource "openstack_containerinfra_clustertemplate_v1" "template_136" {
  name                  = "quarry-136"
  coe                   = "kubernetes"
  dns_nameserver        = "8.8.8.8"
  docker_storage_driver = "overlay2"
  docker_volume_size    = 20
  external_network_id   = "wan-transport-eqiad"
  fixed_subnet          = "vxlan-dualstack-ipv4"
  fixed_network         = "VXLAN/IPv6-dualstack"
  flavor                = "g4.cores4.ram8.disk20"
  image                 = "ubuntu-22.04-v1.36.4-for-magnum"
  master_flavor         = "g4.cores2.ram4.disk20"
  master_lb_enabled     = "true"
  network_driver        = "calico"

  labels = {
    kube_tag                       = "v1.36.4"
    container_runtime              = "containerd"
    containerd_version             = "1.6.28"
    containerd_tarball_sha256      = "f70736e52d61e5ad225f4fd21643b5ca1220013ab8b6c380434caeefb572da9b"
    master_lb_floating_ip_enabled  = "false"
  }
}
