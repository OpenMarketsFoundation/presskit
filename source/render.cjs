const fs=require('fs');
const path=require('path');
const sharp=require('sharp');
const root=path.join(__dirname,'..');
(async()=>{
 const jobs=[];
 for(const name of fs.readdirSync(path.join(root,'logos/svg'))){
  for(const width of [512,2048])jobs.push([`logos/svg/${name}`,`logos/png/${name.replace('.svg',`-${width}.png`)}`,width]);
 }
 const apps=JSON.parse(fs.readFileSync(path.join(root,'source/build-manifest.json'))).applications;
 for(const name of apps)jobs.push([name+'.svg',name+'.png',null]);
 jobs.push(['previews/asset-library.svg','previews/asset-library.png',1800]);
 for(const [src,dest,w] of jobs){let p=sharp(path.join(root,src),{limitInputPixels:false});if(w)p=p.resize({width:w});await p.png().toFile(path.join(root,dest));}
 for(const n of [16,32,48,180,512]) await sharp(path.join(root,n<48?'website/icon.svg':'logos/svg/omf-badge-ink.svg')).resize(n,n).png().toFile(path.join(root,`website/icon-${n}.png`));
 console.log(`Rendered ${jobs.length} assets and five icon sizes.`);
})().catch(e=>{console.error(e);process.exit(1)});
