import {createServer} from 'node:http';
import {createReadStream} from 'node:fs';
import {stat} from 'node:fs/promises';
import {resolve,extname,sep} from 'node:path';
const root=resolve(process.argv[2]??'delivery'),port=Number(process.env.VIDEO_PORT??65213);
try{await stat(resolve(root,'index.html'));}catch{throw new Error('The local recording package is missing. Place it in delivery/ before opening the library.');}
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.png':'image/png','.json':'application/json','.srt':'text/plain; charset=utf-8','.md':'text/plain; charset=utf-8','.pdf':'application/pdf','.zip':'application/zip'};
createServer(async(req,res)=>{
 try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const file=resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
  if(!file.startsWith(root+sep)){res.writeHead(403);res.end();return;}
  const info=await stat(file);if(!info.isFile()){res.writeHead(404);res.end();return;}
  const headers={'Content-Type':types[extname(file)]??'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
  let start=0,end=info.size-1,status=200;
  if(req.headers.range){
   const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
   if(!m||(!m[1]&&!m[2])){res.writeHead(416,{'Content-Range':`bytes */${info.size}`});res.end();return;}
   if(m[1]){start=Number(m[1]);end=m[2]?Math.min(Number(m[2]),end):end;}else start=Math.max(0,info.size-Number(m[2]));
   if(start>end||start>=info.size){res.writeHead(416,{'Content-Range':`bytes */${info.size}`});res.end();return;}
   status=206;headers['Content-Range']=`bytes ${start}-${end}/${info.size}`;
  }
  headers['Content-Length']=String(end-start+1);res.writeHead(status,headers);
  if(req.method==='HEAD'||info.size===0){res.end();return;}
  const stream=createReadStream(file,{start,end});stream.on('error',()=>res.destroy());res.on('close',()=>stream.destroy());stream.pipe(res);
 }catch{if(!res.headersSent)res.writeHead(404);res.end();}
}).listen(port,'127.0.0.1',()=>console.log(`Agent Assurance — ROOK: http://127.0.0.1:${port}`));
