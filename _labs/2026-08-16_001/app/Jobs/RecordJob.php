<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class RecordJob implements ShouldQueue
{
    use Queueable;

    public function __construct(public string $label)
    {
    }

    public function handle(): void
    {
        file_put_contents(
            storage_path('done.log'),
            $this->label.PHP_EOL,
            FILE_APPEND
        );
    }
}
