import {build} from 'esbuild';
import {mkdir,copyFile} from 'node:fs/promises';
await mkdir('dist',{recursive:true});
await build({entryPoints:['src/App.jsx'],bundle:true,outfile:'dist/app.js',minify:true,define:{'process.env.NODE_ENV':'"production"'},legalComments:'linked'});
await copyFile('index.html','dist/index.html');
