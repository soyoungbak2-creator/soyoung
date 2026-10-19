# output

| 파일 | 내용 |
|---|---|
| final_zh_subtitled.mp4 | 최종본(중국어 자막 번인), 33.23초, 1080×1920, H.264 High/yuv420p, AAC 48kHz 스테레오, faststart |
| final_no_subtitles.mp4 | 같은 편집, 자막 없음 |
| subtitles_zh.srt | 최종 중국어 자막(간체) |
| subtitles_zh.ass | 번인에 사용한 스타일 자막(WenQuanYi Zen Hei) |
| edit_table.md | 컷별 원본 파일·구간·편집 의도, 원본 파일 정보 |
| edit.py / subs.py | 재현 스크립트 |
| xiaohongshu_copy.md | 중국어 제목 3개, 캡션 1개, 해시태그 5개 |

## 재현 방법
```bash
python3 subs.py                       # subtitles_zh.ass / .srt 생성
python3 edit.py <원본 .mov 폴더> [빌드 폴더]   # 두 MP4 렌더링 (FFmpeg 6.1, libass 필요)
```
원본 파일은 읽기만 하고 수정하지 않습니다.
