<?php

namespace App\Listeners;

use App\Events\ProductUpdatedBoth;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Queue\Attributes\DebounceFor;

#[DebounceFor(3)]
class BothAttributes implements ShouldQueue, ShouldBeUnique
{
    public function handle(ProductUpdatedBoth $event): void
    {
    }
}
