# voice-assistant-gpt
音声入力でChatGPTに質問するプログラムです

ChatGPTに質問したいことをマイクで話しかければChatGPTが答えを返してくれます

OpenAIのAPIKeyが必要です

# 試した環境
Machine: Raspberry Pi4 Model B 8GB

OS: Raspberry Pi OS(64bit)

音声入力はUSBマイクを使用

# 環境構築
## USBマイクを優先する
```
cat /proc/asound/modules
```
で
```
0 snd_bcm2835
1 snd_usb_audio
``` 
となっていたら内蔵オーディオデバイスが優先されているので/etc/modprobe.d/alsa-base.confに
```
options snd slots=snd_usb_audio,snd_bcm2835
options snd_usb_audio index=0
options snd_bcm2835 index=1
```
という文字列を書き込む（私の環境ではalsa-base.confは無かったので新規作成した）
## .bashrcに環境変数を追加
```
export OPENAI_API_KEY="sk-xxxx" #自分のAPIKeyを書く
```
を.bashrcの末尾に書き込む
## パッケージなどのインストール
```
sudo apt install portaudio19-dev
pip install pyaudio
pip install numpy #Raspberry Pi OSならデフォルトでついてるので不要
pip install openai
```

# 実行方法
```
python voice-assistant-gpt
```
をコマンドラインで実行するだけ

入力待機状態になるので、マイクに話しかければ自動で録音が始まります

ChatGPTから回答が返ってきたら入力待機状態に戻ります

入力待機状態で1分間無音状態が続くとプログラムが終了します
