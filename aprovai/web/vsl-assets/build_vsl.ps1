# Build VSL from slides + narration using ffmpeg
# Usage: .\build_vsl.ps1 [-Voice george|leticia]
param([string]$Voice = "george")

$ASSETS = "$PSScriptRoot"
$FFMPEG  = "ffmpeg"  # update if installed to specific path

# Slide durations (seconds) per scene — tuned to ~53s (George) / ~60s (LeticIA)
# Scene:  1     2     3     4     5     6
if ($Voice -eq "george") {
    $AUDIO  = "$ASSETS\narration.mp3"
    $DURS   = @(6.5, 7.5, 10.0, 12.0, 11.0, 6.0)
    $OUTPUT = "$ASSETS\vsl-george.mp4"
} else {
    $AUDIO  = "$ASSETS\narration-leticia.mp3"
    $DURS   = @(7.0, 8.5, 11.0, 13.0, 13.0, 7.5)
    $OUTPUT = "$ASSETS\vsl-leticia.mp4"
}

Write-Host "Building VSL with voice: $Voice"
Write-Host "Audio: $AUDIO"

# Build concat file
$concatFile = "$ASSETS\concat_list.txt"
$content = ""
for ($i = 1; $i -le 6; $i++) {
    $dur = $DURS[$i-1]
    $slide = "$ASSETS\slide_0$i.png"
    $content += "file '$slide'`nduration $dur`n"
}
Set-Content -Path $concatFile -Value $content -Encoding UTF8

# Build video: concat slides + add audio + burn captions
& $FFMPEG -y `
    -f concat -safe 0 -i "$concatFile" `
    -i "$AUDIO" `
    -vf "scale=1280:720,fps=24,subtitles='$ASSETS\captions.srt':force_style='Fontname=Arial,Fontsize=26,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,MarginV=40'" `
    -c:v libx264 -preset fast -crf 22 `
    -c:a aac -b:a 128k `
    -shortest `
    "$OUTPUT"

Write-Host "`nDone: $OUTPUT"
