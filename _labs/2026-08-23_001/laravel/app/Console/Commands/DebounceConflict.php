<?php

namespace App\Console\Commands;

use App\Events\ProductUpdatedBoth;
use Illuminate\Console\Command;
use LogicException;

class DebounceConflict extends Command
{
    protected $signature = 'demo:conflict';
    protected $description = 'DebounceFor と ShouldBeUnique を併用したらどうなるか';

    public function handle(): void
    {
        try {
            event(new ProductUpdatedBoth(77));
            $this->line('  例外なし');
        } catch (LogicException $e) {
            $this->line('  LogicException');
            foreach (explode("\n", wordwrap($e->getMessage(), 34)) as $line) {
                $this->line('  '.$line);
            }
        }
    }
}
