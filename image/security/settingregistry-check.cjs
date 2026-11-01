// Execute the shipped compiled validator class without the DOM-dependent app.
const fs=require('fs'),path=require('path'),vm=require('vm');
const directory=process.argv[2],source=fs.readFileSync(path.join(directory,'lib/settingregistry.js'),'utf8');
const start=source.indexOf('export class DefaultSchemaValidator'),end=source.indexOf('export class SettingRegistry',start);
if(start<0||end<0)throw Error('REVIEW settingregistry: compiled class/API layout changed');
const optionsStart=source.indexOf('const AJV_DEFAULT_OPTIONS ='),optionsEnd=source.indexOf('\n};',optionsStart)+3;
if(optionsStart<0||optionsEnd<3)throw Error('REVIEW settingregistry: validator options layout changed');
const code=source.slice(optionsStart,optionsEnd)+'\n'+source.slice(start,end).replace('export class','class')+'\nDefaultSchemaValidator';
const Ajv=require(require.resolve('ajv',{paths:[directory]}));
const json5=require(require.resolve('json5',{paths:[directory]}));
const Validator=vm.runInNewContext(code,{Ajv,json5,SCHEMA:JSON.parse(fs.readFileSync(path.join(directory,'lib/plugin-schema.json'))),copy:x=>JSON.parse(JSON.stringify(x))},{timeout:5000});
let fixed=false;
try{
 const v=new Validator(),plugin={id:'jupyterlab_code_formatter:settings',schema:{type:'object',properties:{enabled:{type:'boolean',default:true}}},raw:'{}',data:{user:{},composite:{}}};
 if(v.validateData(plugin)||v.validateData(plugin)||plugin.data.composite.enabled!==true)throw Error('unexpected validation result');
 plugin.raw='{"enabled":"bad"}';if(!v.validateData(plugin)?.some(e=>e.keyword==='type'))throw Error('type validation weakened');
 let strict=false;try{v.validateData({...plugin,id:'probe:bad',schema:{$id:'bad_scheme:settings',type:'object'},raw:'{}'});}catch(e){strict=String(e).includes('URI scheme is malformed');}
 if(!strict)throw Error('URI validation weakened');fixed=true;
}catch(e){if(!String(e).includes('URI scheme is malformed'))throw e;}
console.log(JSON.stringify({fixed}));
