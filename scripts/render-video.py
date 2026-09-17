"""Render an edited, subtitled walkthrough from a reviewed shot list; no audio."""
import argparse, json, pathlib, subprocess, textwrap

def clock(seconds, separator=','):
    ms=round(seconds*1000); h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{separator}{ms:03}'

def captions(scenes):
    result=[];cursor=0
    for scene in scenes:
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

def render(plan, assets, output, draft=False):
    output.mkdir(parents=True,exist_ok=True)
    name=plan['id']+('-draft' if draft else '')
    cues=captions(plan['scenes']);write_srt(output/(plan['id']+'.srt'),cues)
    missing=[s['asset'] for s in plan['scenes'] if s['asset'] not in assets]
    if missing and not draft: raise RuntimeError('Missing footage: '+', '.join(sorted(set(missing))))
    work=output/('.render-'+name);work.mkdir(exist_ok=True)
    segments=[];cursor=0
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
        segments.append(segment);cursor+=duration
        print(plan['id'],f'{index+1}/{len(plan["scenes"])}',flush=True)
    listing=work/'concat.txt';listing.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in segments))
    movie=output/(name+'.mp4')
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(movie)])
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    if any(s['codec_type']=='audio' for s in info['streams']):raise RuntimeError('Unexpected audio stream')
    if abs(float(info['format']['duration'])-cursor)>.15:raise RuntimeError('Unexpected video duration')
    (output/(name+'.json')).write_text(json.dumps({'title':plan['title'],'durationSeconds':cursor,'audio':False,'subtitles':'burned in and separate SRT','status':'draft' if draft else 'ready for review','missingFootage':sorted(set(missing)),'video':movie.name,'sourceAssets':[{ 'role':s['asset'],'file':pathlib.Path(assets.get(s['asset'],assets.get('pending-hosted'))).name} for s in plan['scenes']]},indent=2))
    for p in segments:p.unlink()
    print('Saved',movie,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('assets');parser.add_argument('output');parser.add_argument('--draft',action='store_true');args=parser.parse_args()
    render(json.loads(pathlib.Path(args.plan).read_text()),json.loads(pathlib.Path(args.assets).read_text()),pathlib.Path(args.output),args.draft)
