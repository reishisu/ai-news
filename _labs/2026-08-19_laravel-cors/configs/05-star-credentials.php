<?php

// 実験6 用: allowed_origins=['*'] と supports_credentials=true の組み合わせ。
// 「*のまま出るのか / Originがエコーされるのか / エラーになるのか」を実測する。

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => ['*'],

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => true,

];
