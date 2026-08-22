<?php

namespace App\Events;

class ProductUpdatedPlain
{
    public function __construct(public int $productId)
    {
    }
}
