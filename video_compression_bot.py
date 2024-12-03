import os
import math
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
import subprocess
from pathlib import Path
import time
import logging
import random
import string
from PIL import Image
import shutil

# Initialize the bot
API_ID = '15787995'
API_HASH = 'e51a3154d2e0c45e5ed70251d68382de'
BOT_TOKEN = '7628087790:AAFADZ1UQ1II7ECu2zwnctkbCbziDKW0QsA'

bot = TelegramClient('video_compression_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Logging setup for better error handling
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function: Calculate bitrate for target size
def calculate_bitrate(input_path, target_size):
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
         'stream=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    duration = float(probe.stdout.strip())
    target_bitrate = (target_size * 8 * 1024 * 1024) / (duration * 1.048576)  # Convert MB to bits
    return math.floor(target_bitrate)

# Helper function: Compress video
async def compress_video(input_path, output_path, target_size):
    bitrate = calculate_bitrate(input_path, target_size)
    ffmpeg_cmd = [
        'ffmpeg', '-i', input_path, '-b:v', f'{bitrate}k', '-bufsize', f'{bitrate}k', 
        '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', '-strict', '-2', '-y', output_path
    ]
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode()}")
    logger.info(f"Compression finished: {stdout.decode()}")

# Helper function: Add watermark to video
def add_watermark(input_video_path, output_video_path):
    watermark_text = f"Compressed by VideoBot"
    temp_image_path = "watermark.png"
    
    # Create a watermark image using PIL
    img = Image.new('RGBA', (200, 60), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((10, 10), watermark_text, fill=(255, 255, 255), font=font)
    img.save(temp_image_path)
    
    # Add watermark using FFmpeg
    ffmpeg_cmd = [
        'ffmpeg', '-i', input_video_path, '-i', temp_image_path, '-filter_complex', 
        '[0][1]overlay=W-w-10:H-h-10', '-codec:a', 'copy', '-y', output_video_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    os.remove(temp_image_path)  # Clean up the watermark image

# Command handler: Start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Welcome! Send me a video file, and I'll compress it to your desired size.")

# Command handler: Video Compression
@bot.on(events.NewMessage(func=lambda e: e.media))
async def handle_video(event):
    if not event.video:
        return await event.reply("Please send a video file.")

    # Request target size from the user
    await event.reply("Send me the target size in MB (e.g., 20 for 20MB).")
    response = await bot.wait_for(events.NewMessage(from_users=event.sender_id))
    
    try:
        target_size = int(response.text)
    except ValueError:
        return await response.reply("Invalid size. Please send a number in MB.")

    # Download the video
    video_path = await bot.download_media(event.media, file=f"{event.id}_input.mp4")
    compressed_path = f"{event.id}_compressed.mp4"

    try:
        # Add watermark before compressing
        temp_video_path = f"{event.id}_temp_video.mp4"
        add_watermark(video_path, temp_video_path)

        # Compress the video
        await compress_video(temp_video_path, compressed_path, target_size)
        
        # Send the compressed video back to the user
        await bot.send_file(
            event.chat_id,
            compressed_path,
            caption=f"Here's your compressed video ({target_size} MB)."
        )
    except Exception as e:
        await event.reply(f"An error occurred: {e}")
    finally:
        # Clean up temporary files
        os.remove(video_path)
        os.remove(temp_video_path)
        if os.path.exists(compressed_path):
            os.remove(compressed_path)

# Run the bot
logger.info("Bot is running...")
bot.run_until_disconnected()
