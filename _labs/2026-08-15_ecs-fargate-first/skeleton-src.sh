#!/bin/bash
# 雛形の値がどこで決まるかを、
# AWS CLI 同梱のソースから示す。
F=$(python3 -c "import awscli.botocore.utils as u;print(u.__file__)")
echo "${F#/usr/local/lib/python3.11/dist-packages/}"
grep -n "random.choice(shape.enum)" "$F" \
  | sed 's/^\([0-9]*\): */L\1: /'
