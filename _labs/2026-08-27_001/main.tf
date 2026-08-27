terraform {
  required_providers {
    local = { source = "hashicorp/local" }
  }
}

resource "local_file" "memo" {
  filename = "${path.module}/hello.txt"
  content  = "consider me infrastructure\n"

  lifecycle {
    destroy = false
  }
}
