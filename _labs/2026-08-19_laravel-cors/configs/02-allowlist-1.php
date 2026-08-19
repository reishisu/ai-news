<?php

// 実験2・3・4a 用: 許可オリジンを「1件だけ」書いた状態。
// php artisan config:publish cors で出たファイルの allowed_origins だけを変えたもの。

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => ['https://game.example.com'],

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => false,

];
