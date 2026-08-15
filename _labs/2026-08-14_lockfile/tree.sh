#!/bin/bash
# node_modules を「名前 バージョン」だけで一覧する(スコープ付きも含む)
find node_modules -mindepth 2 -maxdepth 3 -name package.json \
  -not -path '*/node_modules/*/node_modules/*' | sort | while read -r f; do
  node -e '
    const p = require(process.argv[1]);
    console.log(p.name.padEnd(18), p.version);
  ' "$PWD/$f"
done
