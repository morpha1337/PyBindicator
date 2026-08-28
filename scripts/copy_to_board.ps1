[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, HelpMessage = "Drive letter of the mounted board, e.g. D or D:")]
    [ValidatePattern('^[A-Za-z]:?$')]
    [string]$DriveLetter
)

$ErrorActionPreference = 'Stop'

#region Configuration

# Directories under the repo root to skip. See AGENTS.md -> Deploying to the board.
$ExcludeDirectories = @(
    '.git',
    '.vscode',
    '.cursor',
    '.vs',
    '.idea',
    'deps',       # UF2 and library bundles — host-only
    'fixtures',   # parser dev samples — not required on device
    'scripts',    # host deploy scripts
    'bin',
    'obj',
    'node_modules',
    'packages',
    'TestResults',
    'Log',
    'Logs',
    '__pycache__'
)

# Individual files at the repo root (or matched by name anywhere) to skip.
$ExcludeFiles = @(
    '.gitignore',
    'AGENTS.md',
    'README.md',
    'secrets.py.example',
    'blink_patterns.py',  # legacy — not used in production firmware
    '*.pyc'
)

#endregion

#region Functions

function Write-ProgressMessage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] $Message"
}

function Get-RepoRoot {
    $repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')
    return $repoRoot.Path.TrimEnd('\')
}

function Normalize-DriveLetter {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DriveLetter
    )

    # Match scripts/space_remaining.ps1: accept "D" or "D:".
    $letter = $DriveLetter.Trim().TrimEnd(':').ToUpper()

    if ($letter -notmatch '^[A-Z]$') {
        throw "Invalid drive letter '$DriveLetter'. Provide a single drive letter, e.g. D or D:."
    }

    return $letter
}

function Get-BoardDrive {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DriveLetter
    )

    $drive = Get-PSDrive -Name $DriveLetter -ErrorAction SilentlyContinue

    if (-not $drive) {
        throw "Drive '$DriveLetter`:' was not found."
    }

    return $drive
}

function Copy-RepoToBoard {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,

        [Parameter(Mandatory = $true)]
        [string]$DestinationRoot,

        [Parameter(Mandatory = $true)]
        [string[]]$ExcludeDirectories,

        [Parameter(Mandatory = $true)]
        [string[]]$ExcludeFiles
    )

    Write-ProgressMessage "Source: $SourceRoot"
    Write-ProgressMessage "Destination: $DestinationRoot"
    Write-ProgressMessage ("Excluding {0} director(ies): {1}" -f $ExcludeDirectories.Count, ($ExcludeDirectories -join ', '))
    Write-ProgressMessage ("Excluding {0} file pattern(s): {1}" -f $ExcludeFiles.Count, ($ExcludeFiles -join ', '))

    $robocopyArgs = @(
        $SourceRoot,
        $DestinationRoot,
        '/E',
        '/COPY:DAT',
        '/DCOPY:DAT',
        '/R:2',
        '/W:2',
        '/BYTES',
        '/ETA',
        '/TEE'
    )

    foreach ($directory in $ExcludeDirectories) {
        if ([string]::IsNullOrWhiteSpace($directory)) {
            continue
        }

        $robocopyArgs += '/XD'
        $robocopyArgs += $directory.Trim().TrimStart('\', '/')
    }

    foreach ($filePattern in $ExcludeFiles) {
        if ([string]::IsNullOrWhiteSpace($filePattern)) {
            continue
        }

        $robocopyArgs += '/XF'
        $robocopyArgs += $filePattern.Trim()
    }

    Write-ProgressMessage 'Copy started.'
    Write-Host ''

    & robocopy @robocopyArgs
    $robocopyExitCode = $LASTEXITCODE

    Write-Host ''

    # Robocopy uses exit codes 0-7 for success with varying detail.
    if ($robocopyExitCode -ge 8) {
        throw "Robocopy failed with exit code $robocopyExitCode."
    }

    Write-ProgressMessage ("Copy finished successfully (robocopy exit code {0})." -f $robocopyExitCode)
}

#endregion

#region Main

try {
    $driveLetter = Normalize-DriveLetter -DriveLetter $DriveLetter
    $null = Get-BoardDrive -DriveLetter $driveLetter
    $destinationRoot = "${driveLetter}:\"
    $repoRoot = Get-RepoRoot

    Write-ProgressMessage '=== Copy repo to board ==='
    Write-ProgressMessage "Drive letter: $driveLetter"

    Copy-RepoToBoard `
        -SourceRoot $repoRoot `
        -DestinationRoot $destinationRoot `
        -ExcludeDirectories $ExcludeDirectories `
        -ExcludeFiles $ExcludeFiles

    Write-ProgressMessage '=== COPY TO BOARD COMPLETE ==='
    Write-Host 'STATUS: COMPLETE'
    exit 0
}
catch {
    Write-ProgressMessage '=== COPY TO BOARD FAILED ==='
    Write-Host 'STATUS: FAILED'
    Write-Error $_
    exit 1
}

#endregion
