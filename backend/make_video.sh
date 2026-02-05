#!/bin/bash
# Decision Stream 영상 생성 스크립트
# 대시보드 이미지 + 음성을 합성하여 MP4 영상 생성

set -e

# 날짜 생성
TODAY=$(date +%Y%m%d)
OUTPUT_DIR="output"
IMAGE="$OUTPUT_DIR/dashboard_$TODAY.png"
AUDIO="$OUTPUT_DIR/voice.mp3"
VIDEO="$OUTPUT_DIR/ds_anchor_$TODAY.mp4"

echo "[영상 생성 시작] $VIDEO"

# 파일 존재 확인
if [ ! -f "$IMAGE" ]; then
    echo "❌ 이미지 파일이 없습니다: $IMAGE"
    exit 1
fi

if [ ! -f "$AUDIO" ]; then
    echo "❌ 음성 파일이 없습니다: $AUDIO"
    exit 1
fi

# FFmpeg으로 영상 생성
# - 이미지를 영상 길이만큼 반복
# - 음성과 합성
# - H.264 코덱 (유튜브 호환)
ffmpeg -y \
    -loop 1 -i "$IMAGE" \
    -i "$AUDIO" \
    -c:v libx264 \
    -tune stillimage \
    -c:a aac \
    -b:a 192k \
    -pix_fmt yuv420p \
    -shortest \
    -movflags +faststart \
    "$VIDEO"

echo "✅ 영상 생성 완료: $VIDEO"
echo "파일 크기: $(du -h "$VIDEO" | cut -f1)"
echo "재생 시간: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO" | cut -d. -f1)초"
