<?php

namespace App\Events;

class ProductUpdated
{
    public function __construct(public int $productId)
    {
    }
}
