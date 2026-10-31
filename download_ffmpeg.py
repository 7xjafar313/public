import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil

# حل مشكلة ترميز الحروف والرموز التعبيرية في ويندوز
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

def download_and_extract_ffmpeg():
    print("=" * 60)
    print("📥 Starting FFmpeg Auto-Downloader...")
    print("=" * 60)
    
    dest_ffmpeg = "ffmpeg.exe"
    dest_ffprobe = "ffprobe.exe"
    
    if os.path.exists(dest_ffmpeg) and os.path.exists(dest_ffprobe):
        print("[✓] FFmpeg and FFprobe are already present in the bot directory!")
        return True
        
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")
    
    try:
        print(f"Downloading FFmpeg from Gyan.dev...")
        print("This might take a couple of minutes depending on your internet speed (size ~90MB)...")
        
        # Simple progress bar reporter
        def progress_reporter(block_num, block_size, total_size):
            read_so_far = block_num * block_size
            if total_size > 0:
                percent = min(100, (read_so_far * 100) // total_size)
                sys.stdout.write(f"\rDownloading: [{percent}%] ({read_so_far // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\rDownloading: {read_so_far // (1024*1024)}MB")
                sys.stdout.flush()

        urllib.request.urlretrieve(URL, zip_path, progress_reporter)
        print("\n\n[✓] Download completed. Extracting files...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extracted_count = 0
            for file_info in zip_ref.infolist():
                filename = os.path.basename(file_info.filename)
                if filename in ["ffmpeg.exe", "ffprobe.exe"]:
                    # Open the file inside zip and write to root folder
                    with zip_ref.open(file_info.filename) as source, open(filename, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    print(f"[✓] Extracted: {filename} directly to bot folder.")
                    extracted_count += 1
            
            if extracted_count == 2:
                print("\n🎉 FFmpeg & FFprobe installed successfully in your bot folder!")
                return True
            else:
                print("\n[X] Error: Could not find ffmpeg.exe and ffprobe.exe inside the downloaded zip.")
                return False
                
    except Exception as e:
        print(f"\n[X] Error occurred: {e}")
        return False
    finally:
        # Clean up temporary dir
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    success = download_and_extract_ffmpeg()
    if not success:
        sys.exit(1)
