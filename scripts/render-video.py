"""Render reviewed footage with subtitles and optional speech-aligned narration."""
import argparse, json, pathlib, subprocess, textwrap, wave

def clock(seconds, separator=','):
    ms=round(seconds*1000); h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{separator}{ms:03}'

def captions(scenes):
    result=[];cursor=0
    for scene in scenes:
        if 'speech' in scene:
            for start,end,part in scene['speech']['cues']:
                result.append((cursor+.35+start,cursor+.35+end,part))
        else:
            parts=scene['captions']; slot=scene['duration']/len(parts)
            for i,part in enumerate(parts): result.append((cursor+i*slot+.3,cursor+(i+1)*slot-.2,part))
        cursor+=scene['duration']
    return result

def write_srt(path, cues):
    path.write_text('\n\n'.join(f'{i+1}\n{clock(a)} --> {clock(b)}\n'+ '\n'.join(textwrap.wrap(text,76)) for i,(a,b,text) in enumerate(cues))+'\n')

def run(args):
    result=subprocess.run(args,capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stderr[-2400:])
    return result.stdout

def render_scene_audio(audio, duration, output):
    samples=round(duration*48000)
    # loudnorm can leave a timestamp offset. Reset it after resampling so
    # every scene retains its opening delay and exact place on the timeline.
    filters=f'loudnorm=I=-18:TP=-2:LRA=7,aresample=48000,asetpts=N/SR/TB,adelay=350:all=1,apad,atrim=end_sample={samples}'
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(audio),'-af',filters,'-ar','48000','-ac','1','-c:a','pcm_s16le',str(output)])
    with wave.open(str(output)) as wav:
        if wav.getframerate()!=48000 or wav.getnframes()!=samples:
            raise RuntimeError('Scene audio does not match its timeline duration')

def render(plan, assets, output, draft=False):
    output.mkdir(parents=True,exist_ok=True)
    name=plan['id']+('-draft' if draft else '')
    cues=captions(plan['scenes']);write_srt(output/(plan['id']+'.srt'),cues)
    missing=[s['asset'] for s in plan['scenes'] if s['asset'] not in assets]
    if missing and not draft: raise RuntimeError('Missing footage: '+', '.join(sorted(set(missing))))
    work=output/('.render-'+name);work.mkdir(exist_ok=True)
    segments=[];audio_segments=[];cursor=0
    narrated=bool(plan.get('audio'))
    if narrated and any('speech' not in s for s in plan['scenes']):raise RuntimeError('Generate speech timings before rendering narrated scenes')
    for index,scene in enumerate(plan['scenes']):
        asset=assets.get(scene['asset'],assets.get('pending-hosted'))
        if not asset: raise RuntimeError('No footage or pending-footage card for '+scene['asset'])
        source=pathlib.Path(asset).resolve()
        if not source.is_file(): raise RuntimeError('Source file missing: '+str(source))
        duration=scene['duration'];segment=work/f'{index:02}.mp4';ass=work/f'{index:02}.ass'
        def ass_time(t): return clock(t,'.')[:-1].lstrip('0') if t>=3600 else '0'+clock(t,'.')[2:-1]
        header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Arial,34,&H00FFFFFF,&H00FFFFFF,&H00132D24,&H00132D24,0,0,0,0,100,100,0,0,1,1,0,2,110,110,20,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
        events=[]
        for start,end,text in cues:
            if start>=cursor and end<=cursor+duration:
                safe=text.replace('\\','/').replace('{','(').replace('}',')')
                line='\\N'.join(textwrap.wrap(safe,87))
                events.append(f'Dialogue: 0,{ass_time(start-cursor)},{ass_time(end-cursor)},Default,,0,0,0,,{line}')
        ass.write_text(header+'\n'.join(events)+'\n')
        still=source.suffix.lower() in ['.png','.jpg','.jpeg']
        inputs=['-loop','1','-i',str(source)] if still else ['-i',str(source)]
        speed=1
        if not still:
            seconds=float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(source)]))
            speed=min(1,(duration-4)/max(seconds,.1))
        # Short takes pause on their final frame; long takes are edited to fit.
        filters=f'setpts={speed}*(PTS-STARTPTS),fps=24,scale=1728:972:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:color=0x132d24,tpad=stop_mode=clone:stop_duration={duration},trim=duration={duration},setsar=1,ass={ass.resolve()}'
        run(['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-vf',filters,'-t',str(duration),'-an','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-threads','2',str(segment)])
        segments.append(segment)
        if narrated:
            speech=scene['speech'];audio=pathlib.Path(speech['audio']).resolve()
            if speech['duration']+.35>duration:raise RuntimeError('Narration exceeds scene duration')
            wav=work/f'{index:02}.wav'
            render_scene_audio(audio,duration,wav)
            audio_segments.append(wav)
        cursor+=duration
        print(plan['id'],f'{index+1}/{len(plan["scenes"])}',flush=True)
    listing=work/'concat.txt';listing.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in segments))
    movie=output/(name+'.mp4')
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing)]
    if narrated:
        audio_listing=work/'audio-concat.txt';audio_listing.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in audio_segments))
        command+=['-f','concat','-safe','0','-i',str(audio_listing),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(cursor)]
    else:command+=['-map','0:v:0','-c','copy','-an']
    run(command+['-movflags','+faststart',str(movie)])
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    if any(s['codec_type']=='audio' for s in info['streams'])!=narrated:raise RuntimeError('Unexpected audio stream configuration')
    if abs(float(info['format']['duration'])-cursor)>.15:raise RuntimeError('Unexpected video duration')
    if narrated:
        audio_stream=next(s for s in info['streams'] if s['codec_type']=='audio')
        if abs(float(audio_stream['duration'])-cursor)>.03:raise RuntimeError('Narration duration does not match the video')
    (output/(name+'.json')).write_text(json.dumps({'title':plan['title'],'durationSeconds':cursor,'audio':narrated,'voice':plan.get('voice'), 'narrationTiming':'ElevenLabs character alignment' if narrated else None,'subtitles':'burned in and separate SRT','status':'draft' if draft else 'ready for review','missingFootage':sorted(set(missing)),'video':movie.name,'sourceAssets':[{ 'role':s['asset'],'file':pathlib.Path(assets.get(s['asset'],assets.get('pending-hosted'))).name} for s in plan['scenes']]},indent=2))
    for p in segments+audio_segments:p.unlink()
    print('Saved',movie,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('assets');parser.add_argument('output');parser.add_argument('--draft',action='store_true');args=parser.parse_args()
    render(json.loads(pathlib.Path(args.plan).read_text()),json.loads(pathlib.Path(args.assets).read_text()),pathlib.Path(args.output),args.draft)
