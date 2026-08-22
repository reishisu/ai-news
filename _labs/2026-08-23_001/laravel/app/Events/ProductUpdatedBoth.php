<?php

namespace App\Events;

class ProductUpdatedBoth
{
    public function __construct(public int $productId)
    {
    }
}
