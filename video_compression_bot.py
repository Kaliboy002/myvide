import os
import time
import ffmpeg
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# Set up the client and bot details
api_id = '15787995'  # Your API ID
api_hash = 'e51a3154d2e0c45e5ed70251d68382de'  # Your API Hash
bot_token = '7628087790:AAFADZ1UQ1II7ECu2zwnctkbCbziDKW0QsA'  # Your Bot Token

# Initialize Telegram client
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# Folder where the videos will be stored and processed
VIDEO_FOLDER = "videos"
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)

# Function to compress video
def compress_video(input_file, output_file):
    try:
        # Start the compression process
        print(f"Compressing video: {input_file}")
        
        # FFmpeg command to reduce video size, adjust bitrate and resolution
        ffmpeg.input(input_file).output(output_file, vcodec='libx264', preset='fast', crf=28).run()

        print(f"Video compressed successfully: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error during video compression: {e}")
        return None

# Function to handle incoming messages
@client.on(events.NewMessage())
async def handle_video(event):
    if event.video:
        sender = event.sender_id
        video = await event.download_media(file=VIDEO_FOLDER)

        # Get the file size of the original video
        original_size = os.path.getsize(video) / (1024 * 1024)  # in MB
        print(f"Received video of size {original_size:.2f} MB")

        # Calculate the output video path
        output_video = os.path.join(VIDEO_FOLDER, f"compressed_{int(time.time())}.mp4")

        # Compress the video
        compressed_video = compress_video(video, output_video)

        if compressed_video:
            # Send back the compressed video
            await event.respond("Here is your compressed video:", file=compressed_video)
            
            # Clean up the original and compressed files
            os.remove(video)
            os.remove(compressed_video)
        else:
            await event.respond("An error occurred during the compression process.")
        
        return

    # Handle other cases if needed
    await event.respond("Please send a video file for compression.")

# Function to start the bot
async def start_bot():
    print("Bot started...")
    await client.start()
    await client.run_until_disconnected()

# Main entry point
if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
