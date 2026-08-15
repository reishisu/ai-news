terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"

  # 認証情報なしで plan まで進めるためのダミー。
  # 本番の設定には絶対に書かない。
  access_key                  = "dummy"
  secret_key                  = "dummy"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
}

resource "aws_ecs_cluster" "app" {
  name = "tf-hello"

  tags = {
    Env = "sandbox"
  }
}
