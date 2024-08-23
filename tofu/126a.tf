resource "openstack_containerinfra_cluster_v1" "k8s_126a" {
  name                = "quarry-126a"
  cluster_template_id = resource.openstack_containerinfra_clustertemplate_v1.template_126a.id
  master_count        = 1
  node_count          = 2
}

resource "local_file" "kube_config" {
  content  = resource.openstack_containerinfra_cluster_v1.k8s_126a.kubeconfig.raw_config
  filename = "kube.config"
}

resource "openstack_containerinfra_clustertemplate_v1" "template_126a" {
  name                  = "quarry-126a"
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
  network_driver        = "flannel"

  labels = {
    kube_tag                  = "v1.26.8-rancher1"
    container_runtime         = "containerd"
    containerd_version        = "1.6.20"
    containerd_tarball_sha256 = "1d86b534c7bba51b78a7eeb1b67dd2ac6c0edeb01c034cc5f590d5ccd824b416"
    hyperkube_prefix          = "docker.io/rancher/"
    cloud_provider_enabled    = "true"
  }
}
