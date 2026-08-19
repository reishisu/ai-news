<?php

// browser_check.sh 用: 実験ページを配っているオリジン
// (http://127.0.0.1:8130) を許可リストに足した状態。
// これを入れるとブラウザの fetch が通る。

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => ['https://game.example.com', 'http://127.0.0.1:8130'],

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => false,

];
