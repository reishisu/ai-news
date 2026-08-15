terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}

# 認証情報を持たないまま plan まで通すための設定。
# apply はしない(できない)。
provider "aws" {
  region                      = "ap-northeast-1"
  access_key                  = "dummy"
  secret_key                  = "dummy"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
}

# Unity Web(マルチスレッド有効)を配るときに足りない3本を
# CloudFront のレスポンスヘッダーポリシーで付ける。
# SecurityHeadersConfig には COOP/COEP/CORP の枠が無いので
# custom_headers_config に書く。
resource "aws_cloudfront_response_headers_policy" "unity_web" {
  name    = "unity-web-coi"
  comment = "COOP/COEP/CORP for Unity Web multithreading"

  custom_headers_config {
    items {
      header   = "Cross-Origin-Opener-Policy"
      value    = "same-origin"
      override = true
    }
    items {
      header   = "Cross-Origin-Embedder-Policy"
      value    = "require-corp"
      override = true
    }
    items {
      # Unity のサーバー設定例に合わせて cross-origin
      header   = "Cross-Origin-Resource-Policy"
      value    = "cross-origin"
      override = true
    }
  }
}
