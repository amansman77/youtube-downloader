FROM ubuntu:20.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine64

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wine64 \
    wget \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Windows용 Python 설치
RUN wget https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe && \
    wine64 python-3.8.10-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.8.10-amd64.exe

# 작업 디렉토리 설정
WORKDIR /src

# 필요한 파일 복사
COPY youtube_downloader.py .
COPY requirements.txt .

# Windows Python으로 패키지 설치
RUN wine64 python -m pip install --upgrade pip && \
    wine64 python -m pip install -r requirements.txt && \
    wine64 python -m pip install pyinstaller

# exe 파일 생성
RUN wine64 python -m PyInstaller --onefile --clean youtube_downloader.py

# 결과물을 /dist 디렉토리에 복사
CMD cp -r dist/* /dist/ 