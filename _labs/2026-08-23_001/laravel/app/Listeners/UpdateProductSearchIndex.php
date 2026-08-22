<?php

namespace App\Listeners;

use App\Events\ProductUpdated;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Queue\Attributes\DebounceFor;

#[DebounceFor(3)]
class UpdateProductSearchIndex implements ShouldQueue
{
    public function handle(ProductUpdated $event): void
    {
        file_put_contents(
            storage_path('ran.log'),
            "商品{$event->productId} を更新\n",
            FILE_APPEND
        );
    }

    public function debounceId(ProductUpdated $event): string
    {
        return (string) $event->productId;
    }
}
