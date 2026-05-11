output "vpc_id" {
  value = aws_vpc.secnotes_vpc.id
}

output "eks_cluster_name" {
  value = aws_eks_cluster.secnotes.name
}

output "eks_endpoint" {
  value = aws_eks_cluster.secnotes.endpoint
}
