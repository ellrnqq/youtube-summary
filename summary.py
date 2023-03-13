import config
import openai
import os
import sys

from pytube import YouTube
from moviepy.editor import *

dir = "res/"

# YouTubeから動画をダウンロード
def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download()
    return stream.default_filename


# 動画ファイルをmp3形式に変換
def convert_to_mp3(video_filename):
    clip = AudioFileClip(video_filename)
    mp3_filename = video_filename.replace(".mp4", ".mp3")
    clip.write_audiofile(dir+mp3_filename)
    os.remove(video_filename)
    return mp3_filename

def downloadMP3(url):
    print("downloadMP3: start")
    video_filename = download_youtube_video(url)
    mp3_filename = convert_to_mp3(video_filename)
    print("downloadMP3: done")

    return mp3_filename

def translate(mp3_filename):
    translate_filename = mp3_filename.replace('.mp3', '.txt')
    file = open(dir+mp3_filename, "rb")
    print("voiceToText: start.")
    openai.Audio.translate
    transcription = openai.Audio.translate("whisper-1", file)
    with open(dir+translate_filename, 'w', encoding="utf_8") as f:
        f.write(transcription["text"])
    file.close()
    os.remove(dir+mp3_filename)
    print("voiceToText: done.")

    return translate_filename
    
def optimize(translate_filename):
    f = open(dir+translate_filename, 'r', encoding="utf-8")
    data = f.read()
    f.close()
    messages=[
            {
                "role": "system",
                "content": f"あなたは情報整理のプロです。次の情報を日本語にしてうまくまとめてmd形式で提出してください。。\n {data}"
            },
        ]
    #
    print("optimize: start.")
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)
    r = res["choices"][0]["message"]["content"]
    optimize_filename = translate_filename.replace('.txt', '.md')
    with open(dir+optimize_filename, 'w', encoding="utf_8") as f:
        f.write(r)
    messages.append({"role": "assistant", "content": r})
    os.remove(dir+translate_filename)
    print("optimize: done.")
    return optimize_filename

def main(argv):
    openai.api_key = config.OPENAPI_KEY
    print(f"url = {argv[1]}")
    mp3_filename = downloadMP3(argv[1])
    translate_filename = translate(mp3_filename)
    optimize_filename = optimize(translate_filename)
    print(f"created. - {optimize_filename}")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
