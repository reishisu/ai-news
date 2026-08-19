<?php

// 実験3 用: 許可オリジンを「2件」書いた状態。
// 1件のときと挙動が変わる（記事の要点）。

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => ['https://game.example.com', 'https://app.example.com'],

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => false,

];
