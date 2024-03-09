from requests import get
from json import loads

import pyaudio
import wave
import threading

from bilibili_api import Credential, sync
from bilibili_api.live import LiveDanmaku


from time import sleep


def load_conf():
    with open("./conf.json", "r") as f:
        raw_conf = f.read()
    return loads(raw_conf)

conf = load_conf()

api_server = conf["api_server"]
model = "bert_vits2"

def gen_audio(text: str):
    try:
        print(f"使用 {model} 合成 {text}")
        resp = get(f"{api_server}/gen/{model}/?text={text}")
        return resp.text
    except:
        pass


def play_wav(wav_file_path):
    chunk = 1024
    wf = wave.open(wav_file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

exit_flag = False
voice_seq = []

def play_background_seq():
    global voice_seq
    global exit_flag
    while not exit_flag:
        if voice_seq:
            current = voice_seq[0]
            voice_seq = voice_seq[1:]
            play_wav(current)
        sleep(0.3)



thread = threading.Thread(target=play_background_seq)
thread.start()


def load_conf():
    with open("./config.json", "r") as f:
        conf_raw = f.read()
    
    conf = loads(conf_raw)

    assert "cookie" in conf, "请检查配置中的cookie"
    assert "sessdata" in conf["cookie"], "请检查配置中cookie的sessdata"
    assert "bili_jct" in conf["cookie"], "请检查配置中cookie的bili_jct"
    assert "buvid3" in conf["cookie"], "请检查配置中cookie的"
    assert "tts" in conf, "请检查配置中的tts"
    assert "endpoint" in conf["tts"], "请检查配置中tts的endpoint"

    return conf


conf = load_conf()




credential = Credential(
    sessdata=conf["cookie"]["sessdata"],
    bili_jct=conf["cookie"]["bili_jct"],
    buvid3=conf["cookie"]["buvid3"]
)


monitor = LiveDanmaku(conf["room_id"], credential=credential)


@monitor.on("DANMU_MSG")
async def recv(event):
    username = event["data"]["info"][2][1]
    msg = event["data"]["info"][1]
    text = f"{username}说：{msg}"
    file_name = gen_audio(text)
    voice_seq.append(f"../uni-tts/"+file_name.replace('"', ""))


sync(monitor.connect())