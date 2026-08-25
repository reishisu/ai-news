<?php
// PHP の in_array は、第3引数(strict)が無いと型を揃えてから比べる。
// Laravel 13.27.0 は in_array / doesnt_contain ルールでここに true を渡すようになった。
$other = [1, 0, 'abc'];
$cases = ['1', 0.0, 'ABC', true, null];
printf("%-6s %-6s %-6s\n", 'value', 'loose', 'strict');
foreach ($cases as $v) {
    printf("%-6s %-6s %-6s\n",
        var_export($v, true),
        in_array($v, $other) ? 'match' : '-',
        in_array($v, $other, true) ? 'match' : '-');
}
