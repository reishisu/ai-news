#!/bin/bash
# plan の中身から、サービスが何を指しているかを出す。
J=$(terraform show -json plan.bin)
echo "$J" | jq -r '.resource_changes[]
 | select(.type=="aws_ecs_service").change.after
 | "desired_count : \(.desired_count)",
   "launch_type   : \(.launch_type)",
   "lb.container  : \(.load_balancer[0].container_name)",
   "lb.port       : \(.load_balancer[0].container_port)"'
echo "$J" | jq -r '.resource_changes[]
 | select(.type=="aws_lb_target_group").change.after
 | "tg.target_type: \(.target_type)",
   "tg.port       : \(.port)"'
echo "$J" | jq -r '.resource_changes[]
 | select(.type=="aws_ecs_task_definition").change.after
 | "td.cpu/mem    : \(.cpu)/\(.memory)",
   "td.network    : \(.network_mode)"'
