<?php

namespace App\Console\Commands;

use App\Events\ProductUpdated;
use App\Events\ProductUpdatedPlain;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Symfony\Component\Console\Output\NullOutput;

class DebounceDemo extends Command
{
    protected $signature = 'demo:debounce {mode : plain|debounce}';
    protected $description = '同じイベントを4回投げて、リスナーが何回動くか数える';

    public function handle(): void
    {
        $log = storage_path('ran.log');
        @unlink($log);
        DB::table('jobs')->delete();
        Cache::flush();

        $debounced = $this->argument('mode') === 'debounce';

        for ($i = 1; $i <= 4; $i++) {
            $debounced
                ? event(new ProductUpdated(77))
                : event(new ProductUpdatedPlain(77));
            $this->line("  {$i}回目を発火");
            usleep(500_000);
        }

        $this->line('  4秒待つ');
        sleep(4);

        $this->line('  キューを流す');
        Artisan::call('queue:work', [
            '--stop-when-empty' => true,
        ], new NullOutput());

        $lines = file_exists($log)
            ? count(file($log, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES))
            : 0;

        $this->newLine();
        $this->line("  発火 4 回 / 実行 {$lines} 回");
    }
}
