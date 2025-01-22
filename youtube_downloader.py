import yt_dlp
import os
import sys
import subprocess

class YouTubeDownloader:
    def __init__(self, output_path="downloads"):
        """
        Initialize YouTubeDownloader
        :param output_path: Directory where videos will be saved
        """
        self.output_path = output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # ffmpeg 위치 설정
        self.ffmpeg_path = self.get_ffmpeg_path()
        if not self.ffmpeg_path:
            print("Error: ffmpeg를 찾을 수 없습니다.")
            sys.exit(1)

    def get_ffmpeg_path(self):
        """Get ffmpeg path for both development and production environments"""
        # 1. 개발 환경: 시스템에 설치된 ffmpeg 확인
        try:
            if sys.platform == "win32":
                result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
        except:
            pass

        # 2. 배포 환경: PyInstaller 임시 디렉토리에서 ffmpeg 확인
        try:
            base_path = sys._MEIPASS
            ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")
            if os.path.exists(ffmpeg_path):
                return os.path.dirname(ffmpeg_path)
        except:
            pass

        # 3. 현재 디렉토리에서 ffmpeg 확인
        current_dir = os.path.abspath(".")
        ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            return current_dir

        return None

    def download_video(self, url, resolution="best"):
        """
        Download a single YouTube video
        :param url: YouTube video URL
        :param resolution: Video resolution ("best", "720p", "480p", etc.)
        :return: Path to downloaded file
        """
        try:
            format_spec = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b'
            if resolution != "best":
                format_spec = f'bv*[height<={resolution[:-1]}][ext=mp4]+ba[ext=m4a]/b[height<={resolution[:-1]}][ext=mp4]'

            ydl_opts = {
                'format': format_spec,
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'ffmpeg_location': self.ffmpeg_path,
                'nocheckcertificate': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'extract_flat': True,
                'quiet': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("\nGetting video information...")
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Failed to get video information")
                
                print(f"\nDownloading: {info['title']}")
                ydl.download([url])
                
                # Get the output path (항상 .mp4 확장자 사용)
                video_path = os.path.join(
                    self.output_path,
                    f"{info['title']}.mp4"
                )
                print(f"\nDownload completed: {info['title']}")
                return video_path
                
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None

    def download_playlist(self, playlist_url):
        """
        Download all videos from a YouTube playlist
        :param playlist_url: YouTube playlist URL
        :return: List of downloaded video paths
        """
        try:
            ydl_opts = {
                'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'ffmpeg_location': self.ffmpeg_path,
                'nocheckcertificate': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'extract_flat': True,
                'quiet': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("\nGetting playlist information...")
                info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' not in info:
                    raise Exception("Not a valid playlist URL")
                
                print(f"\nDownloading playlist: {info.get('title', 'Unknown')}")
                downloaded_videos = []
                
                for entry in info['entries']:
                    video_path = os.path.join(
                        self.output_path,
                        f"{entry['title']}.mp4"  # 항상 .mp4 확장자 사용
                    )
                    downloaded_videos.append(video_path)
                
                ydl.download([playlist_url])
                print(f"\nPlaylist download completed. Total videos: {len(downloaded_videos)}")
                return downloaded_videos
                
        except Exception as e:
            print(f"Error downloading playlist: {str(e)}")
            return []

    def _progress_hook(self, d):
        """Progress hook for download status"""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes:
                percent = (downloaded_bytes / total_bytes) * 100
                print(f"\rProgress: {percent:.1f}% of {total_bytes/1024/1024:.1f}MB", end='')
            else:
                print(f"\rDownloaded: {downloaded_bytes/1024/1024:.1f}MB", end='')

# User Interface
def main():
    downloader = YouTubeDownloader()
    
    while True:
        print("\n=== YouTube 다운로더 ===")
        print("1. 단일 동영상 다운로드")
        print("2. 재생목록 다운로드")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ")
        
        if choice == "1":
            url = input("\nYouTube 동영상 URL을 입력하세요: ")
            print("\n해상도 선택:")
            print("1. 최고 화질")
            print("2. 1080p")
            print("3. 720p")
            print("4. 480p")
            
            res_choice = input("\n선택하세요 (1-4): ")
            resolution = {
                "1": "best",
                "2": "1080p",
                "3": "720p",
                "4": "480p"
            }.get(res_choice, "best")
            
            print("\n다운로드를 시작합니다...")
            downloader.download_video(url, resolution)
            input("\n계속하려면 Enter를 누르세요...")
            
        elif choice == "2":
            url = input("\nYouTube 재생목록 URL을 입력하세요: ")
            print("\n다운로드를 시작합니다...")
            downloader.download_playlist(url)
            input("\n계속하려면 Enter를 누르세요...")
            
        elif choice == "3":
            print("\n프로그램을 종료합니다.")
            break
        
        else:
            print("\n잘못된 선택입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
