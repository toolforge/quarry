resource "openstack_containerinfra_cluster_v1" "k8s_127a" {
  name                = "quarry-127a"
  cluster_template_id = resource.openstack_containerinfra_clustertemplate_v1.template_127a.id
  master_count        = 1
  node_count          = 4
}

resource "local_file" "kube_config" {
  content  = resource.openstack_containerinfra_cluster_v1.k8s_127a.kubeconfig.raw_config
  filename = "kube.config"
}

resource "openstack_containerinfra_clustertemplate_v1" "template_127a" {
  name                  = "quarry-127a"
  coe                   = "kubernetes"
  dns_nameserver        = "8.8.8.8"
  docker_storage_driver = "overlay2"
  docker_volume_size    = 20
  external_network_id   = "wan-transport-eqiad"
  fixed_subnet          = "cloud-instances2-b-eqiad"
  fixed_network         = "lan-flat-cloudinstances2b"
  flavor                = "g4.cores4.ram8.disk20"
  floating_ip_enabled   = "false"
  image                 = "Fedora-CoreOS-38"
  master_flavor         = "g4.cores2.ram4.disk20"
  network_driver        = "calico"

  labels = {
    kube_tag                       = "v1.27.8-rancher2"
    container_runtime              = "containerd"
    containerd_version             = "1.6.28"
    containerd_tarball_sha256      = "f70736e52d61e5ad225f4fd21643b5ca1220013ab8b6c380434caeefb572da9b"
    cloud_provider_tag             = "v1.27.3"
    cinder_csi_plugin_tag          = "v1.27.3"
    k8s_keystone_auth_tag          = "v1.27.3"
    magnum_auto_healer_tag         = "v1.27.3"
    octavia_ingress_controller_tag = "v1.27.3"
    calico_tag                     = "v3.26.4"
  }
}
