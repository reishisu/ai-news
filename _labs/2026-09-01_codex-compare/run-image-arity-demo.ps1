param(
  [switch]$Retake,
  [int]$PreRunDelaySeconds = 4,
  [int]$PostRunHoldSeconds = 40,
  [string]$WindowTitle = 'CODEX-DEMO-IMAGE-ARITY'
)

$Host.UI.RawUI.WindowTitle = $WindowTitle
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()

try {
  Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class CodexTrapFont {
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
  $font = New-Object CodexTrapFont+FontInfo
  $font.cbSize = [uint32][System.Runtime.InteropServices.Marshal]::SizeOf([type]'CodexTrapFont+FontInfo')
  $font.FaceName = 'Consolas'
  $font.dimY = 26
  $font.FontFamily = 54
  $font.FontWeight = 400
  [void][CodexTrapFont]::SetCurrentConsoleFontEx([CodexTrapFont]::GetStdHandle(-11), $false, [ref]$font)
} catch {}

try {
  $Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size(100, 200)
  $Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size(100, 20)
} catch {}

Set-Location 'D:\ainews-studio\ai-news-video'
$labDir = 'out\_codex\2026-09-01_codex-compare'
$rawLog = Join-Path $labDir $(if ($Retake) { 'recording-image-arity-raw.log' } else { 'image-arity-raw.log' })
New-Item -ItemType Directory -Path $labDir -Force | Out-Null
Remove-Item -LiteralPath $rawLog -Force -ErrorAction SilentlyContinue

Clear-Host
Write-Host '再現: -i は後ろの文字列まで画像引数として飲み込む' -ForegroundColor Yellow
Write-Host 'help: -i, --image <FILE>...' -ForegroundColor Cyan
Write-Host ''
Write-Host 'PS D:\ainews-studio\ai-news-video> ' -NoNewline -ForegroundColor DarkCyan
Write-Host 'codex exec -i out/wintest/probe_12s.png "画像の文字を一行で書き写す"' -ForegroundColor White
Write-Host ''
Start-Sleep -Seconds $PreRunDelaySeconds

& codex exec --sandbox read-only --skip-git-repo-check --color never `
  -i 'out/wintest/probe_12s.png' '画像の文字を一行で書き写す' 2>&1 | ForEach-Object {
    $line = [string]$_
    [IO.File]::AppendAllText($rawLog, $line + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    if ($line -notmatch 'ERROR rmcp') { Write-Host $line }
  }
$exitCode = $LASTEXITCODE
Write-Host ''
Write-Host ('exit code: ' + $exitCode) -ForegroundColor Yellow
Write-Host '対策: プロンプトは標準入力から渡す' -ForegroundColor Green
Write-Host '録画終了まで、この窓は閉じません' -ForegroundColor DarkGray
Start-Sleep -Seconds $PostRunHoldSeconds
