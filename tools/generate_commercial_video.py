"""Pentactopus Commercial Video Producer & End-to-End Walkthrough Engine.

Generates a broadcast-quality Full HD (1920x1080) marketing & walkthrough demo video:
1. Professional neural voiceover narration (edge-tts en-US-ChristopherNeural) across 6 acts:
   - Act 1: Introduction to Pentactopus
   - Act 2: Core Architecture & Perceptual AI
   - Act 3: Cross-Platform Installation & Local Commands
   - Act 4: Remote Device Mesh & Multi-Device Control
   - Act 5: Unit Economics & Subscription Pricing
   - Act 6: Enterprise Customization & Call to Action
2. Studio-composed ambient electronic tech soundtrack mixed seamlessly under speech
3. High-resolution 1080p visual slides with gradient overlays, branding, and typography
4. Merged with FFmpeg into marketing/Pentactopus_Commercial_Demo.mp4
"""

import os
import sys
import asyncio
import subprocess
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
import edge_tts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "marketing", "video_assets")
OUTPUT_VIDEO = os.path.join(BASE_DIR, "marketing", "Pentactopus_Commercial_Demo.mp4")
ARTIFACT_DIR = r"C:\Users\Sany\.gemini\antigravity-ide\brain\465a4303-b5be-4691-9e73-d72152cc913c"
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\Sany\AppData\Local\Microsoft\WinGet\Links\ffmpeg.EXE"

os.makedirs(ASSETS_DIR, exist_ok=True)

# Narration scripts for the 6 core acts
SCENES = [
    {
        "id": "scene1_intro",
        "title": "PENTACTOPUS | Autonomous Computer-Use AI & Remote Mesh",
        "subtitle": "Next-Generation Autonomous Computer Control for Windows & Android",
        "bg_image": os.path.join(BASE_DIR, "reports", "ui_screenshots", "web_landing.png"),
        "script": (
            "Welcome to Pentactopus — the next-generation autonomous computer-use AI and high-performance remote desktop mesh. "
            "Control your Windows PC from Android, automate complex desktop tasks, and deploy intelligent agents that see, act, and verify."
        )
    },
    {
        "id": "scene2_architecture",
        "title": "CORE ARCHITECTURE | Sub-10ms WebRTC & Perceptual Vision",
        "subtitle": "Sub-10ms Latency • Native Hardware Injection • Multi-Model Gateway",
        "bg_image": os.path.join(ARTIFACT_DIR, "full_page_capture_1789681826644.png"),
        "script": (
            "At the heart of Pentactopus is our sub-ten-millisecond WebRTC streaming mesh and autonomous cognitive vision engine. "
            "Our AI perceives UI elements pixel-by-pixel, plans multi-step workflows, and injects hardware events with zero perceptible latency."
        )
    },
    {
        "id": "scene3_installation",
        "title": "CROSS-PLATFORM INSTALLATION | Windows & Android Binaries",
        "subtitle": "Native Win32 Executables • Genuine APKs • Zero Heavy Runtimes",
        "bg_image": os.path.join(BASE_DIR, "reports", "ui_screenshots", "desktop_agent_ui.png"),
        "script": (
            "Deploying Pentactopus is completely seamless. Download lightweight native binaries for Windows and Android with zero bloated dependencies. "
            "On Windows, our installer configures your local command center in seconds, running local tasks with full hardware acceleration."
        )
    },
    {
        "id": "scene4_remote_control",
        "title": "BI-DIRECTIONAL MESH | Remote Viewport & AI Co-Pilot",
        "subtitle": "Phone-to-PC & PC-to-Phone • Touch Mapping • Autonomous Task Runner",
        "bg_image": os.path.join(BASE_DIR, "reports", "ui_screenshots", "web_user_dashboard.png"),
        "script": (
            "Pairing remote nodes takes just seconds. Command your Windows desktop from your smartphone, or steer an Android fleet right from your workstation. "
            "Simply dispatch an objective, and your AI co-pilot executes it autonomously across the mesh."
        )
    },
    {
        "id": "scene5_pricing",
        "title": "TRANSPARENT UNIT ECONOMICS | Pricing & Subscription Plans",
        "subtitle": "Dynamic Cost Calculator • Free Starter • Pro at $12/month",
        "bg_image": os.path.join(ARTIFACT_DIR, "scrolled_view_1789681822204.png"),
        "script": (
            "We provide crystal-clear, transparent unit economics. Calculate exact token and bandwidth costs dynamically with our built-in slider. "
            "Get started free today, or upgrade to Pentactopus Pro for just twelve dollars a month for unlimited cloud relays and vision inference."
        )
    },
    {
        "id": "scene6_enterprise",
        "title": "ENTERPRISE READY | Custom Integrations & Governance",
        "subtitle": "RBAC Administration • Custom Agent Buses • Deploy at pentactopus.com",
        "bg_image": os.path.join(BASE_DIR, "reports", "ui_screenshots", "admin_dashboard.png"),
        "script": (
            "Need custom on-premise deployments, multi-agent organization buses, or bespoke enterprise integrations? "
            "Contact our engineering team today at contact at pentactopus dot com. "
            "Pentactopus: Your computer. Controlled by you, or your AI."
        )
    }
]


async def generate_voiceovers():
    print("=" * 65)
    print("  [STAGE 1/4] GENERATING NEURAL NARRATION VOICEOVERS")
    print("=" * 65)
    voice = "en-US-ChristopherNeural"
    for i, scene in enumerate(SCENES):
        out_mp3 = os.path.join(ASSETS_DIR, f"{scene['id']}.mp3")
        print(f"--> Synthesizing Act {i+1}: {scene['title'][:35]}...")
        comm = edge_tts.Communicate(scene["script"], voice, rate="+4%")
        await comm.save(out_mp3)
        print(f"    Saved: {out_mp3}")


def get_audio_duration(file_path):
    cmd = [FFMPEG, "-i", file_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    for line in res.stderr.split("\n"):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 10.0


def create_visual_slide(scene, duration, out_path):
    # Base 1920x1080 16:9 canvas
    canvas = Image.new("RGB", (1920, 1080), (9, 9, 11))
    
    # Load background screenshot
    if os.path.isfile(scene["bg_image"]):
        bg = Image.open(scene["bg_image"]).convert("RGB")
        # Resize maintaining aspect ratio to fit center
        bg_w, bg_h = bg.size
        scale = min(1800 / bg_w, 800 / bg_h)
        new_w, new_h = int(bg_w * scale), int(bg_h * scale)
        bg_resized = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center in upper 80% of canvas
        paste_x = (1920 - new_w) // 2
        paste_y = 60 + (800 - new_h) // 2
        canvas.paste(bg_resized, (paste_x, paste_y))
        
        # Outer subtle card border
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([paste_x - 1, paste_y - 1, paste_x + new_w + 1, paste_y + new_h + 1], outline=(39, 39, 42), width=1)
    else:
        draw = ImageDraw.Draw(canvas)

    # Top Brand Bar
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, 1920, 50], fill=(14, 14, 17))
    draw.line([0, 50, 1920, 50], fill=(39, 39, 42), width=1)
    draw.text((40, 16), "PENTACTOPUS | OFFICIAL PRODUCT DEMO & ARCHITECTURE WALKTHROUGH", fill=(161, 161, 170))
    draw.text((1680, 16), "PENTACTOPUS.COM", fill=(59, 130, 246))

    # Bottom Lower-Third Banner
    draw.rectangle([0, 880, 1920, 1080], fill=(14, 14, 17))
    draw.line([0, 880, 1920, 880], fill=(59, 130, 246), width=2)

    # Accent Dot & Title
    draw.ellipse([40, 915, 52, 927], fill=(59, 130, 246))
    draw.text((64, 910), scene["title"], fill=(244, 244, 245))
    draw.text((64, 950), scene["subtitle"], fill=(161, 161, 170))
    draw.text((64, 990), "Autonomous Computer-Use AI Mesh • Sub-10ms WebRTC Streaming • PBKDF2 Enterprise RBAC", fill=(113, 113, 122))

    canvas.save(out_path, "JPEG", quality=95)


def render_scene_videos():
    print("\n" + "=" * 65)
    print("  [STAGE 2/4] RENDERING SCENE CLIPS (1080p Full HD)")
    print("=" * 65)
    scene_clips = []
    
    for i, scene in enumerate(SCENES):
        audio_file = os.path.join(ASSETS_DIR, f"{scene['id']}.mp3")
        slide_img = os.path.join(ASSETS_DIR, f"{scene['id']}.jpg")
        clip_mp4 = os.path.join(ASSETS_DIR, f"{scene['id']}.mp4")

        # Get exact audio duration + 0.5s padding
        duration = get_audio_duration(audio_file) + 0.5
        create_visual_slide(scene, duration, slide_img)

        print(f"--> Encoding Scene {i+1}: duration={duration:.2f}s...")
        # FFmpeg: loop image for duration, sync with voiceover
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-i", slide_img,
            "-i", audio_file,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-shortest",
            clip_mp4
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        scene_clips.append(clip_mp4)
        print(f"    Rendered: {clip_mp4}")

    return scene_clips


def assemble_final_video(scene_clips):
    print("\n" + "=" * 65)
    print("  [STAGE 3/4] CONCATENATING SCENES & MIXING AUDIO")
    print("=" * 65)

    concat_list = os.path.join(ASSETS_DIR, "concat_list.txt")
    with open(concat_list, "w") as f:
        for clip in scene_clips:
            clean_path = clip.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    unmixed_video = os.path.join(ASSETS_DIR, "unmixed_video.mp4")
    print("--> Concatenating scene video clips...")
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        unmixed_video
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    # Mix background music under voiceover
    theme_music = os.path.join(ASSETS_DIR, "theme_music.wav")
    print("--> Mixing background theme soundtrack (-22dB volume)...")

    cmd_mix = [
        FFMPEG, "-y",
        "-i", unmixed_video,
        "-i", theme_music,
        "-filter_complex",
        "[1:a]volume=0.10,afade=t=in:st=0:d=3,afade=t=out:st=100:d=5[bgm];"
        "[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    # Copy to artifacts directory
    artifact_copy = os.path.join(ARTIFACT_DIR, "Pentactopus_Commercial_Demo.mp4")
    shutil.copy2(OUTPUT_VIDEO, artifact_copy)

    video_size = os.path.getsize(OUTPUT_VIDEO)
    total_duration = get_audio_duration(OUTPUT_VIDEO)

    print("\n" + "=" * 65)
    print("  [STAGE 4/4] COMMERCIAL DEMO VIDEO GENERATION COMPLETE!")
    print("=" * 65)
    print(f"  Target File:    {OUTPUT_VIDEO}")
    print(f"  Artifact Copy:  {artifact_copy}")
    print(f"  File Size:      {video_size:,} bytes ({video_size / (1024*1024):.2f} MB)")
    print(f"  Total Duration: {total_duration:.1f} seconds")
    print("=" * 65 + "\n")


def run():
    asyncio.run(generate_voiceovers())
    clips = render_scene_videos()
    assemble_final_video(clips)


if __name__ == "__main__":
    run()
