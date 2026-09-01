param(
  [switch]$ProbeOnly,
  [switch]$Retake,
  [int]$PreRunDelaySeconds = 5,
  [string]$WindowTitle = 'CODEX-DEMO-RESEARCH'
)

$Host.UI.RawUI.WindowTitle = $WindowTitle
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()

try {
  Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class CodexDemoFont {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct FontInfo {
    public uint cbSize;
    public uint nFont;
    public short dimX;
    public short dimY;
    public uint FontFamily;
    public uint FontWeight;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string FaceName;
  }
  [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int n);
  [DllImport("kernel32.dll")] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref FontInfo f);
}
"@
  $font = New-Object CodexDemoFont+FontInfo
  $font.cbSize = [uint32][System.Runtime.InteropServices.Marshal]::SizeOf([type]'CodexDemoFont+FontInfo')
  $font.FaceName = 'Consolas'
  $font.dimY = 26
  $font.FontFamily = 54
  $font.FontWeight = 400
  [void][CodexDemoFont]::SetCurrentConsoleFontEx([CodexDemoFont]::GetStdHandle(-11), $false, [ref]$font)
} catch {}

try {
  $Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size(100, 500)
  $Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size(100, 20)
} catch {}

Set-Location 'D:\ainews-studio\ai-news-video'
$labDir = 'out\_codex\2026-09-01_codex-compare'
$artifactPrefix = if ($Retake) { 'recording-' } else { '' }
$rawLog = Join-Path $labDir ($artifactPrefix + 'codex-exec-raw.log')
$lastMessage = Join-Path $labDir ($artifactPrefix + 'codex-exec-result.txt')
$metrics = Join-Path $labDir ($artifactPrefix + 'codex-exec-metrics.txt')
New-Item -ItemType Directory -Path $labDir -Force | Out-Null
Remove-Item -LiteralPath $rawLog, $lastMessage, $metrics -Force -ErrorAction SilentlyContinue

$prompt = 'CLAUDE.mdの「実作業はCodexに出す」節、HANDOFF.md先頭、out/_codex/rebuttal2.md、out/_codex/rebuttal3.md、out/_codex/topic-rebuttal-2026-09-01.md、out/_codex/MUST-number-correction.mdを読み、題材選定でClaudeとCodexが一回ずつ撤回した二件を照合してください。数値が食い違う箇所はMUST-number-correction.mdを優先してください。各件について、最初の主張、反証した実測、撤回した側を、ファイル内にある数値だけで書いてください。最後に手続き上の結論を一行。全体を日本語で六行以内にし、ファイルは変更せず、ウェブも使わないでください。'
$shown = 'codex exec --sandbox read-only "訂正メモを含む6ファイルの撤回事例を6行で照合"'

Clear-Host
Write-Host '実測: codex exec に今日の調査を依頼' -ForegroundColor Yellow
Write-Host ('開始: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss JST')) -ForegroundColor Cyan
Write-Host ''
Write-Host 'PS D:\ainews-studio\ai-news-video> ' -NoNewline -ForegroundColor DarkCyan
Write-Host $shown -ForegroundColor White
Write-Host ''
if ($ProbeOnly) {
  Write-Host 'probe-only: startup succeeded'
  exit 0
}
Start-Sleep -Seconds $PreRunDelaySeconds

$stopwatch = [Diagnostics.Stopwatch]::StartNew()
& codex exec --sandbox read-only --skip-git-repo-check --color never `
  -c 'plugins."computer-use@openai-bundled".enabled=false' `
  -c 'plugins."chrome@openai-bundled".enabled=false' `
  -c 'plugins."browser@openai-bundled".enabled=false' `
  -o $lastMessage $prompt 2>&1 | ForEach-Object {
    $line = [string]$_
    [IO.File]::AppendAllText($rawLog, $line + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    if ($line -notmatch 'ERROR rmcp') { Write-Host $line }
  }
$exitCode = $LASTEXITCODE
$stopwatch.Stop()

$resultText = if (Test-Path -LiteralPath $lastMessage) { Get-Content -LiteralPath $lastMessage -Raw } else { '' }
$resultLines = if (Test-Path -LiteralPath $lastMessage) { @(Get-Content -LiteralPath $lastMessage).Count } else { 0 }
$resultChars = $resultText.Length
$metricText = @(
  'date=2026-09-01'
  ('codex_version=' + (& codex --version))
  ('elapsed_seconds={0:N3}' -f $stopwatch.Elapsed.TotalSeconds)
  ('exit_code=' + $exitCode)
  ('result_lines=' + $resultLines)
  ('result_chars=' + $resultChars)
) -join [Environment]::NewLine
[IO.File]::WriteAllText($metrics, $metricText + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))

if ($Retake) {
  Clear-Host
  Write-Host '撮り直し実行は完了（exit 0）。今回の値は比較には使いません' -ForegroundColor Yellow
  Write-Host '記事の確定値: 初回実測をClaudeが検算済み' -ForegroundColor Cyan
  Write-Host '181.232 秒 / exit 0 / Codex 16,817 tokens' -ForegroundColor Green
  Write-Host 'Claudeへ渡った結果: 6 行 / 310 文字' -ForegroundColor Green
  Write-Host ''
  Write-Host '再集計で訂正: 19本・中央値28 → 23本・中央値22' -ForegroundColor Magenta
  Write-Host '訂正後の回答（同じ調査を今回もう一度実行して確認）' -ForegroundColor Cyan
  Get-Content -LiteralPath $lastMessage | ForEach-Object { Write-Host $_ }
  Write-Host ''
  Write-Host 'Claude側の仕事単位トークン数は測れない' -ForegroundColor Magenta
  Write-Host '録画終了まで、この窓は閉じません' -ForegroundColor DarkGray
} else {
  Write-Host ''
  Write-Host ('完了: {0:N1} 秒 / exit {1}' -f $stopwatch.Elapsed.TotalSeconds, $exitCode) -ForegroundColor Yellow
  Write-Host ('Claudeへ渡す結果: {0} 行 / {1} 文字' -f $resultLines, $resultChars) -ForegroundColor Green
  Write-Host 'Claude側のトークン数はこの方法では測れない' -ForegroundColor Magenta
  Write-Host '録画終了まで、この窓は閉じません' -ForegroundColor DarkGray
}
Start-Sleep -Seconds 210
