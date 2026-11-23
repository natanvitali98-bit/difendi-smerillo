const fs=require('fs'),acorn=require('acorn');
const s=fs.readFileSync(process.argv[2],'utf8');
const re=/<script[^>]*>([\s\S]*?)<\/script>/g;let m,out=[];
while((m=re.exec(s))){const code=m[1],base=m.index+m[0].indexOf(m[1]);
 let ast;try{ast=acorn.parse(code,{ecmaVersion:'latest',sourceType:'script'});}catch(e){console.error('parse',e.message);continue;}
 (function w(n,par){if(!n||typeof n.type!=='string')return;
  if(n.type==='Literal'&&typeof n.value==='string')out.push({k:'s',a:base+n.start,b:base+n.end,v:n.value,p:par&&par.type});
  if(n.type==='TemplateElement')out.push({k:'t',a:base+n.start,b:base+n.end,v:n.value.cooked,p:'tpl'});
  for(const k in n){if(k==='parent')continue;const c=n[k];if(Array.isArray(c))c.forEach(x=>w(x,n));else if(c&&typeof c.type==='string')w(c,n);}
 })(ast,null);}
process.stdout.write(JSON.stringify(out));
