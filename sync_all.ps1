<#
.SYNOPSIS
  一键同步所有 vedic skill 到所有端点
.DESCRIPTION
  以系统config为唯一源，同步到:
  - Claude Desktop App
  - Pro仓库 (antigravity / claude-code / codex)
  - 开源仓库 (antigravity / claude-code / codex)
  然后 git commit + push 两个仓库
.PARAMETER DryRun
  仅检查差异，不执行复制
.PARAMETER NoPush
  复制但不 git push
.EXAMPLE
  .\sync_all.ps1              # 完整同步 + push
  .\sync_all.ps1 -DryRun      # 只看差异
  .\sync_all.ps1 -NoPush      # 同步但不push
#>
param(
  [switch]$DryRun,
  [switch]$NoPush
)

$ErrorActionPreference = "Continue"

# ── 路径定义 ──
$SYS    = "C:\Users\14361\.gemini\config\skills"
$CLAUDE = "C:\Users\14361\.claude\skills"
$PRO    = "d:\0417jhora\vedic-astro-skills-pro"
$OS     = "d:\0417jhora\vedic-astrology-skills"

# ── 只同步这些子目录/文件 ──
# 每个skill下只同步: SKILL.md + resources/ + scripts/ (不含__pycache__、venv等)
$SYNC_ITEMS = @("SKILL.md", "resources", "scripts", "requirements.txt")

# ── Skill 定义 ──
$SKILLS = @(
  @{name="vedic-reader";     sysName="vedic-reader";     type="shared"},
  @{name="vedic-career";     sysName="vedic-career";     type="shared"},
  @{name="vedic-love";       sysName="vedic-love";       type="shared"},
  @{name="vedic-rectifier";  sysName="vedic-rectifier";  type="shared"},
  @{name="vedic-calculator"; sysName="vedic-calculator";  type="shared"},
  @{name="vedic-core";       sysName="vedic-core";       type="os_only"},
  @{name="vedic-core";       sysName="vedic-core-pro";   type="pro_only"}
)

function Get-ShortHash($path) {
  if(Test-Path $path) { return (Get-FileHash $path).Hash.Substring(0,8) }
  return "________"
}

function Sync-File($srcFile, $dstFile, $label) {
  $srcHash = Get-ShortHash $srcFile
  $dstHash = Get-ShortHash $dstFile
  if($srcHash -ne $dstHash) {
    if($DryRun) {
      Write-Host "  [DIFF] $(Split-Path $srcFile -Leaf) → $label" -ForegroundColor Yellow
    } else {
      $dstDir = Split-Path $dstFile
      if(!(Test-Path $dstDir)) { New-Item $dstDir -ItemType Directory -Force | Out-Null }
      Copy-Item $srcFile $dstFile -Force
      Write-Host "  [SYNC] $(Split-Path $srcFile -Leaf) → $label" -ForegroundColor Green
    }
    return 1
  }
  return 0
}

function Sync-Skill($srcDir, $dstDir, $label) {
  if(!(Test-Path $srcDir)) { return }
  $count = 0

  foreach($item in $SYNC_ITEMS) {
    $srcPath = Join-Path $srcDir $item
    if(!(Test-Path $srcPath)) { continue }

    if((Get-Item $srcPath).PSIsContainer) {
      # 目录: 递归同步，排除 __pycache__
      Get-ChildItem $srcPath -File -Recurse | Where-Object {
        $_.FullName -notlike "*__pycache__*" -and
        $_.FullName -notlike "*\ephe\*" -and
        $_.Extension -notin @(".pyc",".pyo",".se1")
      } | ForEach-Object {
        $rel = $_.FullName.Substring($srcPath.Length)
        $dstFile = Join-Path (Join-Path $dstDir $item) $rel
        $count += Sync-File $_.FullName $dstFile $label
      }
    } else {
      # 文件: 直接同步
      $dstFile = Join-Path $dstDir $item
      $count += Sync-File $srcPath $dstFile $label
    }
  }
  return $count
}

# ── 主逻辑 ──
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Vedic Skills 全量同步" -ForegroundColor Cyan
Write-Host "  $(if($DryRun){'[DRY RUN - 仅检查]'}else{'[执行同步]'})" -ForegroundColor $(if($DryRun){"Yellow"}else{"Green"})
Write-Host "========================================`n" -ForegroundColor Cyan

$total = 0

foreach($skill in $SKILLS) {
  $sysDir = "$SYS\$($skill.sysName)"
  if(!(Test-Path $sysDir)) { continue }

  $targets = @()

  switch($skill.type) {
    "shared" {
      $targets += @{dir="$CLAUDE\$($skill.name)"; label="Claude/$($skill.name)"}
      $targets += @{dir="$PRO\antigravity\skills\$($skill.name)"; label="Pro/anti/$($skill.name)"}
      $targets += @{dir="$PRO\claude-code\skills\$($skill.name)"; label="Pro/cc/$($skill.name)"}
      $targets += @{dir="$PRO\codex\skills\$($skill.name)"; label="Pro/codex/$($skill.name)"}
      $targets += @{dir="$OS\antigravity\skills\$($skill.name)"; label="OS/anti/$($skill.name)"}
      $targets += @{dir="$OS\claude-code\skills\$($skill.name)"; label="OS/cc/$($skill.name)"}
      $targets += @{dir="$OS\codex\skills\$($skill.name)"; label="OS/codex/$($skill.name)"}
    }
    "os_only" {
      $targets += @{dir="$CLAUDE\$($skill.name)"; label="Claude/$($skill.name)"}
      $targets += @{dir="$OS\antigravity\skills\$($skill.name)"; label="OS/anti/$($skill.name)"}
      $targets += @{dir="$OS\claude-code\skills\$($skill.name)"; label="OS/cc/$($skill.name)"}
      $targets += @{dir="$OS\codex\skills\$($skill.name)"; label="OS/codex/$($skill.name)"}
    }
    "pro_only" {
      $targets += @{dir="$CLAUDE\$($skill.sysName)"; label="Claude/$($skill.sysName)"}
      $targets += @{dir="$PRO\antigravity\skills\$($skill.name)"; label="Pro/anti/$($skill.name)"}
      $targets += @{dir="$PRO\claude-code\skills\$($skill.name)"; label="Pro/cc/$($skill.name)"}
      $targets += @{dir="$PRO\codex\skills\$($skill.name)"; label="Pro/codex/$($skill.name)"}
    }
  }

  foreach($t in $targets) {
    $total += Sync-Skill $sysDir $t.dir $t.label
  }
}

if($total -eq 0) {
  Write-Host "  ✅ 所有端点已一致，无需同步" -ForegroundColor Green
}

if(!$DryRun -and !$NoPush -and $total -gt 0) {
  Write-Host "`n── Git Push ──" -ForegroundColor Cyan

  Push-Location $PRO
  git add -A 2>$null
  $diff = git diff --cached --stat 2>$null
  if($diff) {
    git commit -m "sync: auto-sync from system config $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>$null
    git push 2>$null
    Write-Host "  ✅ Pro仓库 pushed" -ForegroundColor Green
  } else {
    Write-Host "  ○ Pro仓库 无变更" -ForegroundColor Gray
  }
  Pop-Location

  Push-Location $OS
  git add -A 2>$null
  $diff = git diff --cached --stat 2>$null
  if($diff) {
    git commit -m "sync: auto-sync from system config $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>$null
    git push 2>$null
    Write-Host "  ✅ 开源仓库 pushed" -ForegroundColor Green
  } else {
    Write-Host "  ○ 开源仓库 无变更" -ForegroundColor Gray
  }
  Pop-Location
}

Write-Host "`n✨ 完成（同步了 $total 个文件）`n" -ForegroundColor Green
