#!/bin/zsh
set -e
PROJECT_ROOT="${0:A:h:h}"
FRAME_DIR="${BIRDLAND_FRAMES:-$PROJECT_ROOT/renders/director4k/frames}"
AUDIO_FILE="${BIRDLAND_AUDIO:-$PROJECT_ROOT/assets/audio/opening-75.wav}"
OUTPUT_DIR="${BIRDLAND_OUTPUT:-$PROJECT_ROOT/renders/director4k}"
for frame_number in {0..1679}; do
  frame_name=$(printf 'frame_%04d.png' "$frame_number")
  test -s "$FRAME_DIR/$frame_name" || { echo "Missing frame: $frame_name"; exit 1; }
done
ffmpeg -hide_banner -loglevel warning -y \
-framerate 24 -i "$FRAME_DIR/frame_%04d.png" \
-i "$AUDIO_FILE" -i "$PROJECT_ROOT/renders/director4k/overlay.png" \
-f ffmetadata -i "$PROJECT_ROOT/data/chapters.ffmeta" \
-filter_complex '[0:v]eq=brightness=-0.045:contrast=1.15:saturation=1.16,split=2[sharp][b];[b]gblur=sigma=16[glow];[sharp][glow]blend=all_mode=screen:all_opacity=0.10[lit];[lit][2:v]overlay=0:0,fade=t=out:st=65:d=5[out]' \
-map '[out]' -map 1:a -map_metadata 3 -map_chapters 3 \
-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 24 \
-c:a aac -b:a 256k -ar 48000 -af 'afade=t=out:st=65:d=5' \
-frames:v 1680 -t 70 -movflags +faststart \
"$OUTPUT_DIR/Birdland-Director-4K.mp4"
