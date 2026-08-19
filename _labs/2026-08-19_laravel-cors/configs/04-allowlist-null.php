<?php

// 実験5 用: Origin: null (WebViewがfile://から読み込んだ場合に相当) を
// 許可リストに足した状態。2件あるので「動的に判定する」枝に入る。

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => ['https://game.example.com', 'null'],

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => false,

];
