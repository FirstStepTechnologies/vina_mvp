# Phase 3: Video Generation Pipeline - Implementation Plan
**Version:** 2.0 (Revised with Production Best Practices)  
**Date:** February 5, 2026  
**Status:** Ready for Implementation

---

## 🎯 Overview

This document outlines the production-ready implementation of the video generation pipeline for Vina. The pipeline converts lesson JSON (from Phase 2) into vertical TikTok-style videos with professional branding, AI-generated images, text-to-speech narration, and optional subtitles.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Video Generation Pipeline                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Input: Lesson JSON from Database         │
    │  - slides[].slide_title                   │
    │  - slides[].items[].bullet                │
    │  - slides[].items[].talk                  │
    │  - slides[].items[].figure (optional)     │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Step 1: Parallel Asset Generation        │
    │  ┌─────────────────┬─────────────────┐    │
    │  │ Imagen API      │ ElevenLabs API  │    │
    │  │ (Images)        │ (Audio)         │    │
    │  │ Max 3 parallel  │ Max 3 parallel  │    │
    │  │ With retries    │ With retries    │    │
    │  └─────────────────┴─────────────────┘    │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Step 2: Slide Composition (Pillow)       │
    │  - Overlay text on images                 │
    │  - Add Vina logo                          │
    │  - Add progress indicator                 │
    │  - Vertical 1080x1920 format              │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Step 3: Video Assembly (FFmpeg CLI)      │
    │  - Concat slides with audio               │
    │  - Generate subtitle track (VTT)          │
    │  - Export MP4 (H.264 + AAC)               │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Step 4: Upload to Cloudinary             │
    │  - Video URL                              │
    │  - Subtitle URL                           │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  Output: Video Metadata                   │
    │  {                                        │
    │    "video_url": "https://...",            │
    │    "subtitle_url": "https://...",         │
    │    "duration_seconds": 180.5              │
    │  }                                        │
    └───────────────────────────────────────────┘
```

---

## 🔧 Key Design Decisions

### **1. FFmpeg CLI Instead of MoviePy**
**Rationale:** Production reliability, lower memory usage, faster processing.
- MoviePy loads all clips in memory → OOM on cloud servers
- FFmpeg processes streams → constant memory footprint
- FFmpeg is battle-tested for production video processing

### **2. Proper Async Patterns (No `nest_asyncio`)**
**Rationale:** FastAPI already runs Uvicorn with an event loop.
- Use `async def` for pipeline methods
- Use `await` in FastAPI endpoints
- Use `asyncio.run()` only in standalone scripts

### **3. Concurrency Limits on API Calls**
**Rationale:** Prevent rate limiting and manage costs.
- Max 3 parallel Imagen calls (configurable)
- Max 3 parallel ElevenLabs calls (configurable)
- Retry logic with exponential backoff

### **4. Consistent JSON Schema**
**Rationale:** Avoid schema mismatches between generation and rendering.
- Use the existing lesson schema from Phase 2
- No new fields introduced in video pipeline

---

## 📦 Dependencies

```toml
# pyproject.toml additions

dependencies = [
    # Existing...
    "pillow>=11.3.0",           # Slide composition
    "google-generativeai>=0.8.0",  # Imagen API
    "elevenlabs>=2.33.1",       # Text-to-speech
    "cloudinary>=1.44.1",       # Video hosting
    "aiohttp>=3.11.0",          # Async HTTP
    "tenacity>=9.0.0",          # Retry logic
]
```

### **System Dependencies**
```bash
# MacBook
brew install ffmpeg

# Railway/Render (add to Dockerfile or nixpacks.toml)
apt-get install -y ffmpeg
```

---

## 📁 File Structure

```
src/vina_backend/
├── integrations/
│   ├── imagen/
│   │   └── client.py              # Gemini Imagen API client
│   ├── elevenlabs/
│   │   └── tts_client.py          # ElevenLabs TTS client
│   └── cloudinary/
│       └── uploader.py            # Cloudinary upload
├── services/
│   ├── slide_composer.py          # Pillow-based slide rendering
│   ├── video_renderer.py          # FFmpeg-based video assembly
│   └── video_pipeline.py          # Main orchestrator
└── utils/
    ├── ffmpeg_utils.py            # FFmpeg helper functions
    └── subtitle_generator.py      # VTT/SRT generation

assets/
├── fonts/
│   ├── Inter-Bold.ttf
│   ├── Inter-Regular.ttf
│   └── Inter-Light.ttf
└── vina_logo.png

scripts/
└── test_video_pipeline.py         # End-to-end test
```

---

## 🚀 Implementation Steps

### **Step 1: Imagen Client (Image Generation)**
**File:** `src/vina_backend/integrations/imagen/client.py`

**Features:**
- Async image generation with Gemini Imagen 3
- Concurrency limiting (max 3 parallel)
- Retry logic (3 attempts, exponential backoff)
- 9:16 aspect ratio enforcement
- Professional style preset

**Testing:**
- Generate 5 images in parallel
- Verify 1080x1920 resolution
- Check retry behavior on API errors

---

### **Step 2: ElevenLabs TTS Client**
**File:** `src/vina_backend/integrations/elevenlabs/tts_client.py`

**Features:**
- Async audio generation
- Concurrency limiting (max 3 parallel)
- Retry logic
- Professional voice settings
- MP3 output format

**Testing:**
- Generate audio for 5 slides in parallel
- Verify audio quality and duration
- Check retry behavior on API errors

---

### **Step 3: Slide Composer**
**File:** `src/vina_backend/services/slide_composer.py`

**Features:**
- Vertical 1080x1920 canvas
- Text overlay with word wrapping
- Vina logo placement (bottom left)
- Progress indicator (bottom right)
- Consistent branding across all slides
- Fallback to gradient background if no image

**Testing:**
- Render 5 slides with different content lengths
- Verify text doesn't overflow
- Check logo and progress indicator placement
- Test on both generated images and default backgrounds

---

### **Step 4: Video Renderer (FFmpeg)**
**File:** `src/vina_backend/services/video_renderer.py`

**Features:**
- FFmpeg CLI-based video assembly
- Subtitle generation (WebVTT format)
- Memory-efficient processing (no in-memory clips)
- H.264 video codec, AAC audio codec
- Optimized settings for cloud deployment

**Testing:**
- Render full 5-slide video
- Verify audio-video sync
- Check subtitle timing
- Verify file size (<20MB for 3-min video)
- Test on both MacBook and Railway

---

### **Step 5: Cloudinary Uploader**
**File:** `src/vina_backend/integrations/cloudinary/uploader.py`

**Features:**
- Video upload with public URL
- Subtitle file upload
- Organized folder structure
- Error handling and retries

**Testing:**
- Upload sample video
- Upload subtitle file
- Verify URLs are accessible
- Check video playback in browser

---

### **Step 6: Pipeline Orchestrator**
**File:** `src/vina_backend/services/video_pipeline.py`

**Features:**
- End-to-end orchestration
- Parallel asset generation (images + audio)
- Sequential slide composition
- FFmpeg video assembly
- Cloudinary upload
- Temporary file cleanup
- Comprehensive error handling

**Testing:**
- Full pipeline test with sample lesson
- Verify all steps complete successfully
- Check cleanup of temporary files
- Test error recovery (API failures, etc.)

---

## 🧪 Testing Strategy

### **Unit Tests**
```python
# tests/test_imagen_client.py
async def test_generate_single_image():
    client = ImagenClient(api_key="...")
    image_path = await client.generate_image_async(
        prompt="Professional office background",
        output_path=Path("test_image.png")
    )
    assert image_path.exists()
    img = Image.open(image_path)
    assert img.size == (1080, 1920)

# tests/test_tts_client.py
async def test_generate_audio():
    client = TTSClient(api_key="...", voice_id="...")
    audio_path = await client.generate_audio_async(
        text="Welcome to this lesson",
        output_path=Path("test_audio.mp3")
    )
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0
```

### **Integration Test**
```python
# scripts/test_video_pipeline.py
async def test_full_pipeline():
    # 1. Load sample lesson from DB
    lesson = get_lesson_from_db("l01_what_llms_are", difficulty=3)
    
    # 2. Generate video
    pipeline = VideoPipeline(...)
    result = await pipeline.generate_video(
        lesson_json=lesson,
        lesson_id="l01_what_llms_are",
        user_profile={"profession": "Clinical Researcher"}
    )
    
    # 3. Verify outputs
    assert result["video_url"].startswith("https://res.cloudinary.com/")
    assert result["subtitle_url"].endswith(".vtt")
    assert result["duration_seconds"] > 0
    
    print(f"✅ Video: {result['video_url']}")
    print(f"✅ Subtitles: {result['subtitle_url']}")
    print(f"✅ Duration: {result['duration_seconds']}s")
```

---

## 🔐 Environment Variables

```bash
# .env additions

# Imagen (Gemini)
GOOGLE_AI_API_KEY=your_gemini_api_key

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Professional voice

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Video Settings
VIDEO_PARALLEL_IMAGES=3
VIDEO_PARALLEL_AUDIO=3
VIDEO_GENERATE_SUBTITLES=true
```

---

## 🚢 Deployment Configuration

### **Railway/Render (nixpacks.toml)**
```toml
[phases.setup]
nixPkgs = ["ffmpeg"]

[phases.install]
cmds = ["pip install -e ."]

[start]
cmd = "uvicorn vina_backend.main:app --host 0.0.0.0 --port $PORT"
```

### **Alternative: Dockerfile**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["uvicorn", "vina_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 Performance Targets

| Metric | Target | Notes |
|:-------|:-------|:------|
| **Video Generation Time** | <60s for 5-slide lesson | Parallel asset generation |
| **Memory Usage** | <512MB peak | FFmpeg streaming, aggressive cleanup |
| **Video File Size** | <20MB for 3-min video | H.264 CRF 23, AAC 128kbps |
| **API Success Rate** | >95% | With retry logic |
| **Subtitle Accuracy** | 100% | Generated from known text |

---

## ✅ Success Criteria

- [ ] Generate video from lesson JSON in <60 seconds
- [ ] Video plays correctly on mobile (vertical 9:16)
- [ ] Audio syncs perfectly with slides
- [ ] Subtitles display correctly in video player
- [ ] Logo and branding consistent across all slides
- [ ] Works identically on MacBook and Railway
- [ ] Memory usage stays under 512MB
- [ ] All temporary files cleaned up after generation

---

## 🎯 Next Steps

1. **Implement Step 1:** Imagen Client (2 hours)
2. **Implement Step 2:** ElevenLabs TTS Client (1 hour)
3. **Implement Step 3:** Slide Composer (3 hours)
4. **Implement Step 4:** Video Renderer (2 hours)
5. **Implement Step 5:** Cloudinary Uploader (1 hour)
6. **Implement Step 6:** Pipeline Orchestrator (2 hours)
7. **End-to-End Testing** (2 hours)

**Total Estimated Time:** 13 hours

---

**Document Status:** ✅ Ready for Implementation  
**Next Action:** Begin Step 1 (Imagen Client)
