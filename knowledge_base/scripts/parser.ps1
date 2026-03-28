# ZXA10 命令参考手册 - HTML解析脚本
# 用途：将5241个HTML文件解析为结构化JSON
# 创建时间：2026-03-28
# 状态：开发中

param(
    [string]$BasePath = "E:\QClaw\workspace\project\chm_extracted",
    [string]$OutputPath = "E:\QClaw\workspace\project\chm_extracted\output\commands",
    [switch]$Verbose
)

$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Parse-CommandPage {
    param([string]$FilePath, [string]$Chapter, [string]$Section)
    
    $result = @{
        name = ""
        chapter = $Chapter
        section = $Section
        description = ""
        mode = ""
        level = 0
        syntax = ""
        parameters = @()
        usage = ""
        examples = @()
        related_commands = @()
        source_file = (Split-Path $FilePath -Leaf)
    }
    
    try {
        $reader = New-Object System.IO.StreamReader($FilePath, [System.Text.Encoding]::UTF8)
        $content = $reader.ReadToEnd()
        $reader.Close()
        
        # 提取命令名称（从title）
        if ($content -match '<title>([^<]+)</title>') {
            $result.name = $matches[1].Trim()
        }
        
        # 提取命令格式
        if ($content -match '命令格式[\s\S]*?<td[^>]*>([^<]+)</td>') {
            $result.syntax = $matches[1].Trim()
        }
        
        # 提取命令模式
        if ($content -match '命令模式[\s\S]*?<td[^>]*>([^<]+)</td>') {
            $result.mode = $matches[1].Trim()
        }
        
        # 提取权限级别
        if ($content -match '命令默认权限级别[\s\S]*?<td[^>]*>(\d+)</td>') {
            $result.level = [int]$matches[1]
        }
        
        # 提取功能说明
        if ($content -match '功能说明[\s\S]*?<td[^>]*>([^<]+)</td>') {
            $result.description = $matches[1].Trim()
        }
        
        # 提取使用说明
        if ($content -match '使用说明[\s\S]*?<td[^>]*>([\s\S]*?)</td>') {
            $usage = $matches[1] -replace '<[^>]+>', ' ' -replace '\s+', ' ' | ForEach-Object { $_.Trim() }
            $result.usage = $usage
        }
        
        # 提取范例（命令格式范例）
        $examples = @()
        if ($content -match '范例[\s\S]*?<pre[^>]*>([\s\S]*?)</pre>') {
            $preContent = $matches[1] -replace '<[^>]+>', '' -replace '\s+', "`n"
            $examples += $preContent.Trim()
        }
        $result.examples = $examples
        
    }
    catch {
        if ($Verbose) { Write-Host "  解析错误: $FilePath - $_" -ForegroundColor Red }
    }
    
    return $result
}

function Get-Chapters {
    param([string]$Path)
    
    $chapters = @()
    $chapterDirs = Get-ChildItem $Path -Directory | Where-Object { $_.Name -match '^\d{2}' }
    
    foreach ($chapterDir in $chapterDirs) {
        $chapterName = $chapterDir.Name -replace '^\d+', ''
        
        $sections = @()
        $sectionDirs = Get-ChildItem $chapterDir.FullName -Directory | Where-Object { $_.Name -match '^\d{2}' }
        
        foreach ($sectionDir in $sectionDirs) {
            $sectionName = $sectionDir.Name -replace '^\d+', ''
            $htmlFiles = Get-ChildItem $sectionDir.FullName -Filter "*.html"
            
            $commands = @()
            foreach ($file in $htmlFiles) {
                $cmd = Parse-CommandPage -FilePath $file.FullName -Chapter $chapterName -Section $sectionName
                if ($cmd.name) {
                    $commands += $cmd
                }
            }
            
            $sections += @{
                name = $sectionName
                file_count = $htmlFiles.Count
                commands = $commands
            }
        }
        
        $chapters += @{
            name = $chapterName
            path = $chapterDir.Name
            section_count = $sectionDirs.Count
            sections = $sections
        }
    }
    
    return $chapters
}

# 主程序
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ZXA10 命令参考手册 - 批量解析工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 确保输出目录存在
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

Write-Host "开始解析... " -NoNewline
$allData = Get-Chapters -Path $BasePath

# 生成每个章节的JSON
$totalCommands = 0
foreach ($chapter in $allData) {
    $chapterFile = Join-Path $OutputPath "$($chapter.path).json"
    $chapterData = @{
        chapter_name = $chapter.name
        chapter_path = $chapter.path
        section_count = $chapter.section_count
        sections = $chapter.sections
        generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    $chapterData | ConvertTo-Json -Depth 10 | Out-File -FilePath $chapterFile -Encoding UTF8
    $totalCommands += ($chapter.sections | ForEach-Object { $_.commands.Count } | Measure-Object -Sum).Sum
}

# 生成总索引
$indexData = @{
    total_chapters = $allData.Count
    total_sections = ($allData | ForEach-Object { $_.section_count } | Measure-Object -Sum).Sum
    total_commands = $totalCommands
    chapters = $allData | ForEach-Object { @{name=$_.name; path=$_.path; sections=$_.section_count} }
    generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$indexFile = Join-Path $OutputPath "INDEX.json"
$indexData | ConvertTo-Json -Depth 10 | Out-File -FilePath $indexFile -Encoding UTF8

Write-Host "完成!" -ForegroundColor Green
Write-Host "解析了 $($allData.Count) 个章节" -ForegroundColor Yellow
Write-Host "总命令数: $totalCommands" -ForegroundColor Yellow
Write-Host "输出目录: $OutputPath" -ForegroundColor Cyan
