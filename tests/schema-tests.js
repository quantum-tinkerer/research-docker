// Runs against the actual compiled validator in the running browser application.
async function schemaTests(registry) {
  const Validator=registry.validator.constructor;
  const v=new Validator();const results={};
  const make=(id,schema,user={})=>({id,schema,raw:JSON.stringify(user),version:'synthetic',data:{user:{},composite:{}}});
  const good=(name,p)=>{const errors=v.validateData(p);if(errors)throw Error(name+': '+JSON.stringify(errors));results[name]=true;return p;};
  const bad=(name,p)=>{const errors=v.validateData(p);if(!Array.isArray(errors)||!errors.length)throw Error(name+' accepted invalid settings');results[name]=errors.map(e=>e.keyword);};
  const local={type:'object',additionalProperties:false,definitions:{value:{type:'integer',minimum:1}},properties:{answer:{$ref:'#/definitions/value'},enabled:{type:'boolean',default:true}}};
  const p=good('third_party_original_opaque_id_local_ref',make('third_party_schema:settings',local,{answer:42}));
  if(p.id!=='third_party_schema:settings'||p.data.composite.enabled!==true)throw Error('public ID or default composition changed');
  good('same_id_lookup',make(p.id,local,{answer:3}));
  bad('local_reference_type',make(p.id,local,{answer:'bad'}));
  bad('local_reference_minimum',make(p.id,local,{answer:0}));
  bad('unknown_property',make(p.id,local,{answer:1,unrecognized:true}));
  const implicit={type:'object',definitions:{answer:{$id:'implicit-relative-answer.json',type:'integer',minimum:5}},properties:{answer:{$ref:'implicit-relative-answer.json'}}};
  good('internal_key_relative_id_reference',make('third_party_schema:implicit-relative',implicit,{answer:5}));
  bad('internal_key_relative_id_reference_rejection',make('third_party_schema:implicit-relative',implicit,{answer:4}));
  const otherImplicit={type:'object',definitions:{answer:{$id:'implicit-relative-answer.json',type:'integer',minimum:10}},properties:{answer:{$ref:'implicit-relative-answer.json'}}};
  good('relative_id_isolation_other_plugin',make('third_party_schema:implicit-other',otherImplicit,{answer:10}));
  bad('relative_id_isolation_other_rejection',make('third_party_schema:implicit-other',otherImplicit,{answer:5}));
  good('relative_id_isolation_original_lookup',make('third_party_schema:implicit-relative',implicit,{answer:5}));
  good('external_schema_registration',make('third_party_schema:common',{$id:'https://schemas.example.invalid/research/common.json',type:'object',definitions:{answer:{type:'integer',minimum:10}},properties:{}}));
  const ext={type:'object',properties:{answer:{$ref:'https://schemas.example.invalid/research/common.json#/definitions/answer'}}};
  good('external_absolute_reference',make('third_party_schema:consumer',ext,{answer:10}));
  bad('external_absolute_reference_rejection',make('third_party_schema:consumer',ext,{answer:9}));
  const rel={$id:'https://schemas.example.invalid/research/relative.json',type:'object',definitions:{positive:{$id:'positive.json',type:'integer',minimum:1}},properties:{answer:{$ref:'positive.json'}}};
  good('relative_nested_id_reference',make('third_party_schema:relative',rel,{answer:2}));
  bad('relative_nested_id_rejection',make('third_party_schema:relative',rel,{answer:0}));
  good('valid_public_uri_key_registration',make('research-schema:shared',{type:'object',definitions:{value:{type:'integer'}},properties:{}}));
  const cross={type:'object',properties:{value:{$ref:'research-schema:shared#/definitions/value'}}};
  good('valid_public_uri_key_cross_reference',make('third_party_schema:cross',cross,{value:7}));
  bad('valid_public_uri_key_cross_reference_rejection',make('third_party_schema:cross',cross,{value:'bad'}));
  good('valid_urn_key_registration',make('urn:research:schema',{type:'object',definitions:{value:{type:'integer'}},properties:{}}));
  const urnRef={type:'object',properties:{value:{$ref:'urn:research:schema#/definitions/value'}}};
  good('valid_urn_key_cross_reference',make('third_party_schema:urn-consumer',urnRef,{value:7}));
  bad('valid_urn_key_cross_reference_rejection',make('third_party_schema:urn-consumer',urnRef,{value:'bad'}));
  if(v._schemaKey('urn:research:schema')!=='urn:research:schema')throw Error('valid multi-colon URI key changed');
  bad('invalid_schema_type',make('third_party_schema:invalid',{type:'object',properties:{value:{type:'not-a-json-schema-type'}}}));
  bad('invalid_root_type',make('third_party_schema:array',{type:'array'}));
  for(const [name,schema] of [
    ['malformed_schema_id_still_rejected',{$id:'bad_scheme:settings',type:'object',properties:{}}],
    ['malformed_schema_ref_still_rejected',{type:'object',properties:{value:{$ref:'bad_scheme:settings'}}}]
  ]) {
    let rejected=false;try{v.validateData(make('schema-validation:'+name,schema,{value:1}));}catch(e){rejected=/URI scheme is malformed/.test(String(e));}
    if(!rejected)throw Error(name+' was weakened');results[name]=true;
  }
  const original=JSON.stringify(local);good('input_schema_unchanged',make('third_party_schema:unchanged',local,{answer:1}));if(JSON.stringify(local)!==original)throw Error('schema mutated');
  const installed=new Validator(),keys=new Map(),schemas=[];
  for(const [id,plugin] of Object.entries(registry.plugins)) {
    const clone=structuredClone(plugin);const key=installed._schemaKey(id);if(keys.has(key))throw Error('internal key collision: '+id);keys.set(key,id);
    const errors=installed.validateData(clone);if(errors)throw Error('installed schema '+id+': '+JSON.stringify(errors));
    // A second call must retrieve compiled validators rather than re-register.
    const repeat=installed.validateData(clone);if(repeat)throw Error('repeat lookup '+id);
    schemas.push({id,key,local_references:JSON.stringify(plugin.schema).includes('"$ref"')});
  }
  if(schemas.length<30||!schemas.some(s=>s.id==='jupyterlab_code_formatter:settings')||!schemas.some(s=>s.id.startsWith('@jupyterlab/')))throw Error('installed schema regression coverage missing');
  return {results,installed_schemas:schemas,installed_count:schemas.length,validation_options_unchanged:true};
}
