<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class UserCountTest extends TestCase
{
    use RefreshDatabase;

    public function test_users_table_is_readable(): void
    {
        $this->assertSame(0, DB::table('users')->count());
    }
}
