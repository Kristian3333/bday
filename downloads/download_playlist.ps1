# Save this as download_playlist.ps1

# Function to ensure youtube-dl is installed
function Ensure-YoutubeDL {
    if (-not (Get-Command -Name "yt-dlp.exe" -ErrorAction SilentlyContinue)) {
        Write-Host "Installing yt-dlp..."
        winget install yt-dlp.yt-dlp
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Please install yt-dlp manually from: https://github.com/yt-dlp/yt-dlp#installation"
            exit 1
        }
    }
}

# Function to download playlist
function Download-YoutubePlaylist {
    param (
        [Parameter(Mandatory=$true)]
        [string]$PlaylistUrl,
        
        [string]$OutputDir = "downloads"
    )

    # Create output directory if it doesn't exist
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }

    # Build the yt-dlp command with optimal parameters
    $ytdlpArgs = @(
        $PlaylistUrl,
        "--format", "best[height<=720]",
        "--output", "$OutputDir/%(title)s.%(ext)s",
        "--no-check-certificate",
        "--ignore-errors",
        "--no-warnings",
        "--quiet",
        "--extract-audio",
        "--add-metadata",
        "--geo-bypass",
        "--no-playlist-reverse",
        "--fragment-retries", "10",
        "--retries", "10",
        "--force-ipv4",
        "--throttled-rate", "100K",
        "--sleep-interval", "5",
        "--max-sleep-interval", "10",
        "--no-progress"
    )

    try {
        Write-Host "Starting download of playlist: $PlaylistUrl"
        Write-Host "Files will be saved to: $OutputDir`n"

        # Execute yt-dlp
        $process = Start-Process -FilePath "yt-dlp" -ArgumentList $ytdlpArgs -NoNewWindow -Wait -PassThru

        if ($process.ExitCode -eq 0) {
            Write-Host "`nPlaylist download completed successfully!"
        }
        else {
            Write-Host "`nSome errors occurred during download. Check the output directory for successfully downloaded files."
        }
    }
    catch {
        Write-Host "An error occurred: $_"
    }
}

# Main script
$playlistUrl = Read-Host -Prompt "Enter YouTube playlist URL"
$outputDir = Read-Host -Prompt "Enter output directory (press Enter for default 'downloads')"

if ([string]::IsNullOrWhiteSpace($outputDir)) {
    $outputDir = "downloads"
}

# Ensure youtube-dl is installed
Ensure-YoutubeDL

# Start download
Download-YoutubePlaylist -PlaylistUrl $playlistUrl -OutputDir $outputDir