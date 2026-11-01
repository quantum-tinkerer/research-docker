// Inspect actual standalone and optimized AMD bytes, not package metadata.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=process.argv[2];
const source=fs.readFileSync(path.join(root,'static/components/underscore/underscore-min.js'),'utf8');
const context={module:{exports:{}},exports:{}};
vm.runInNewContext(source,context,{timeout:5000});
const u=context.module.exports;
if(typeof u.flatten!=='function'||typeof u.isEqual!=='function')throw Error('REVIEW nbclassic AMD API');
let fixed=false;
try{let nested=[1];for(let i=0;i<12000;i++)nested=[nested];let a={},b={};for(let i=0;i<2000;i++){a={next:a};b={next:b};}fixed=u.flatten(nested)[0]===1&&u.isEqual(a,b);}
catch(e){if(e.name!=='RangeError')throw e;}
const bundles=['notebook','edit','tree','terminal','auth'].map(n=>path.join(root,`static/${n}/js/main.min.js`)).filter(p=>fs.existsSync(p)).map(p=>({path:p,text:fs.readFileSync(p,'utf8')})).filter(x=>x.text.includes('Underscore.js'));
if(!bundles.length)throw Error('REVIEW nbclassic: optimized AMD definitions not found');
console.log(JSON.stringify({version:u.VERSION,standalone_fixed:fixed,bundle_fixed:fixed&&bundles.every(x=>x.text.includes(source.trim())),bundles:bundles.map(x=>x.path)}));
