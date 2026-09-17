"""Create cached ElevenLabs narration and speech-aligned subtitle timings.

The API key is read only from ELEVENLABS_API_KEY. Audio stays in the supplied
local output directory; no credential is written into plans or cache records.
"""
import argparse,base64,fcntl,concurrent.futures,hashlib,json,math,os,pathlib,re,time,urllib.request,urllib.error

MODEL='eleven_multilingual_v2'
SETTINGS={'stability':0.6,'similarity_boost':0.75,'style':0.1,'use_speaker_boost':True,'speed':1.0}

def subtitle_cues(alignment):
    chars=alignment['characters'];starts=alignment['character_start_times_seconds'];ends=alignment['character_end_times_seconds']
    text=''.join(chars);words=list(re.finditer(r'\S+',text));cues=[];group=[]
    for word in words:
        group.append(word)
        phrase=text[group[0].start():word.end()].strip()
        if len(phrase)>=76 or len(group)>=14 or (re.search(r'[.!?]$',word.group()) and len(phrase)>=32):
            cues.append([starts[group[0].start()],ends[word.end()-1],phrase]);group=[]
    if group:cues.append([starts[group[0].start()],ends[group[-1].end()-1],text[group[0].start():group[-1].end()].strip()])
    return cues

def synthesize(text,voice,cache):
    payload={'voice':voice,'text':text,'model_id':MODEL,'voice_settings':SETTINGS}
    key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    # Separate renders can share narration. Lock the audio/timing pair across
    # processes so they cannot pay twice or pair one take with another's cues.
    with (cache/(key+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _synthesize_locked(text,voice,cache)

def _synthesize_locked(text,voice,cache):
    body={'text':text,'model_id':MODEL,'voice_settings':SETTINGS}
    key=hashlib.sha256(json.dumps({'voice':voice,**body},sort_keys=True).encode()).hexdigest()
    meta=cache/(key+'.json');audio=cache/(key+'.mp3')
    if meta.exists() and audio.exists():return json.loads(meta.read_text())
    token=os.environ.get('ELEVENLABS_API_KEY')
    if not token:raise RuntimeError('Set ELEVENLABS_API_KEY in your environment before generating narration.')
    request=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps',data=json.dumps(body).encode(),headers={'xi-api-key':token,'Content-Type':'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request,timeout=120) as response:data=json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code not in (429,502,503) or attempt==2:raise RuntimeError(f'ElevenLabs request failed: HTTP {error.code}') from None
            time.sleep(2**(attempt+1))
    audio.write_bytes(base64.b64decode(data['audio_base64']))
    alignment=data.get('normalized_alignment') or data['alignment']
    record={'audio':str(audio.resolve()),'duration':alignment['character_end_times_seconds'][-1], 'cues':subtitle_cues(alignment),'voiceId':voice,'model':MODEL,'textHash':hashlib.sha256(text.encode()).hexdigest()}
    meta.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    return record

def narrate(plan,output,cache):
    cache.mkdir(parents=True,exist_ok=True);output.mkdir(parents=True,exist_ok=True)
    voice=plan['voice']['voiceId']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda scene:synthesize(scene['narration'],voice,cache),plan['scenes']))
    if plan.get('pacing')=='speech-led':
        # A short lead-in and exit hold, rounded to an exact video frame.
        # Do not pad a presentation to an arbitrary target running time.
        durations=[math.ceil((r['duration']+.65)*24)/24 for r in records]
        target=sum(durations)
        plan['durationSeconds']=target
    else:
        minimum=[math.ceil(r['duration']+1.1) for r in records]
        target=plan['durationSeconds']
        if sum(minimum)>target:raise RuntimeError(f'Narration requires at least {sum(minimum)}s, exceeding the {target}s plan; shorten the script.')
        durations=[max(scene['duration'],least) for scene,least in zip(plan['scenes'],minimum)]
        while sum(durations)>target:
            index=max(range(len(durations)),key=lambda i:durations[i]-minimum[i])
            durations[index]-=1
        while sum(durations)<target:
            index=max(range(len(durations)),key=lambda i:plan['scenes'][i]['duration']-durations[i])
            durations[index]+=1
    for scene,record,duration in zip(plan['scenes'],records,durations):
        scene['duration']=duration;scene['speech']=record
    (output/'narrated-plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
    print(plan['id'],f'{len(records)} narrated scenes, {sum(r["duration"] for r in records):.1f}s speech / {target}s video',flush=True)
    return plan

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('output');parser.add_argument('--cache',default='artifacts/local/narration-cache');args=parser.parse_args()
    narrate(json.loads(pathlib.Path(args.plan).read_text()),pathlib.Path(args.output),pathlib.Path(args.cache))
