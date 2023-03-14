import time
import pyaudio
import wave
import numpy as np
import openai
import os

# OpenAI APIのセットアップ
openai.api_key = os.environ["OPENAI_API_KEY"]

# マイク入力の設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 500  # 閾値（音量がこの値以上なら録音開始）
SILENT_CHUNKS = 100  # 無音が続くチャンク数
WAVE_OUTPUT_FILENAME = "output.wav"

# 録音した音声データを格納するためのリスト
frames = []

# ChatGPTの入力履歴を格納するためのリスト
chat_history = []

# PyAudioのインスタンスを生成
p = pyaudio.PyAudio()

# ストリームを開始して録音を開始する
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# 録音開始のメッセージを表示する
print("Please start speaking.")

# 会話の開始時間を設定
start_time = time.time()

# ループを開始する
while True:
    # マイクから音声データを読み取る
    data = stream.read(CHUNK)
    # 音声データをnumpyの配列に変換する
    audio_data = np.frombuffer(data, dtype=np.int16)
    # 音量の平均値を計算する
    volume = np.abs(audio_data).mean()
    # 閾値を超える音量が検出されたら録音を開始する
    if volume > THRESHOLD:
        print("* recording")
        # 閾値を超える音量が続く限り音声データを読み取り、リストに追加する
        while True:
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            frames.append(data)
            # 無音が続いた場合は録音を停止する
            if volume < THRESHOLD:
                silent_chunks += 1
                if silent_chunks > SILENT_CHUNKS:
                    print("* done recording")
                    break
            else:
                silent_chunks = 0
        # 録音した音声データをWAVファイルとして保存する
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        # 録音した音声データを削除する
        frames.clear()

        # 音声認識APIにより音声データを文字列に変換する
        with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            print("user: "+transcript["text"])

            chat_history.append({"role": "user", "content": transcript["text"]})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
            )

            output = response.choices[0]["message"]["content"].strip()
            print("ChatGPT: " + output)
            # 入力履歴に追加する
            chat_history.append({"role": "assistant", "content": output})

            # 録音再開のメッセージを表示する
            print("Please start speaking again.")

            # 録音開始時間を更新する
            start_time = time.time()

    # マイクからの入力が一定時間なかった場合は終了する
    if time.time() - start_time > 60:
        print("No input for 60 seconds. Exiting...")
        break

# ストリームを停止し、PyAudioのインスタンスを破棄する
stream.stop_stream()
stream.close()
p.terminate()
