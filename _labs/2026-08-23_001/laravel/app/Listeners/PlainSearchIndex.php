<?php

namespace App\Listeners;

use App\Events\ProductUpdatedPlain;
use Illuminate\Contracts\Queue\ShouldQueue;

class PlainSearchIndex implements ShouldQueue
{
    public function handle(ProductUpdatedPlain $event): void
    {
        file_put_contents(
            storage_path('ran.log'),
            "商品{$event->productId} を更新\n",
            FILE_APPEND
        );
    }
}
