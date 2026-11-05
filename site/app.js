(function(){
"use strict";
const data=window.HGC_DATA, alg=window.HGCAlgorithms;
let mode="locations", selected=0, stage="improved", shuffled=false;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const rows=data.rows.concat({...data.uncertainty_example,public_name:"Unknown-scope example",metadata_only:true});
const field=(label,value,wide=false)=>'<div'+(wide?' class="wide"':'')+'><dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd></div>';
function renderRecords(){
 document.getElementById("records").innerHTML=rows.map((r,i)=>'<button class="record-button '+(i===selected?'selected':'')+'" data-record="'+i+'" aria-pressed="'+(i===selected)+'"><span class="record-number">'+String(i+1).padStart(2,"0")+'</span><span><b>'+esc(r.public_name)+'</b><small>License '+esc(r.license_number)+' · '+esc(r.metadata_only?'metadata only':r.observed_redemption_scope)+'</small></span><span class="record-arrow" aria-hidden="true">→</span></button>').join("");
 document.querySelectorAll("[data-record]").forEach(b=>b.addEventListener("click",()=>{selected=Number(b.dataset.record);renderRecords();document.querySelector('[data-record="'+selected+'"]').focus();}));
 const r=rows[selected],loc=mode==="locations",source=data.sources[loc?"directory":"birthday"],unknown=!!r.metadata_only;
 const record=unknown?data.uncertainty_example:loc?{license_number:r.license_number,observed_license_type:r.observed_license_type,observed_license_status:r.observed_license_status,license_evidence_class:r.license_evidence_class,license_source_version:r.license_source_version}:{location_id:r.location_id,license_number:r.license_number,public_name:r.public_name,observed_claim_text:r.observed_claim_text,claim_text_sha256:r.claim_text_sha256,observed_redemption_scope:r.observed_redemption_scope,redemption_group_id:r.redemption_group_id,observed_publication_eligible:r.observed_publication_eligible,deal_validation:data.deal_validation};
 let facts='';
 if(unknown){facts=field('Source scope','unknown')+field('Group relationship','Not supplied')+field('Claim evidence','Not copied in this metadata example',true);}
 else if(loc){facts=field('License type',r.observed_license_type)+field('Recorded status',r.observed_license_status+' (historical)')+field('Source exported',source.exportedAt,true)+field('Bridge captured',source.capturedAt,true);}
 else{facts=field('Recorded scope',r.observed_redemption_scope)+field('Deal status','Current known valid deals')+field('Last validated','August 2026')+field('File generated',source.generated_at,true)+field('Validation source','HGC owner · list validation',true);}
 const note=unknown?'The full export has 21 unknown-scope records. The redemption scope is unknown; this does not make the deal invalid.':loc?'The displayed name is a label from the birthday export. This tab shows license fields from the January directory export. Deal validation was in August 2026; shop or license status can change separately. Street addresses and provider-derived fields are not projected.':'HGC’s owner confirms these are current known valid deals, last validated August 2026. The source terms are preserved verbatim. No independent shop check was performed for this showcase. The source publication flag is retained as provenance, separate from deal validation.';
 const terms=!loc&&!unknown?'<details class="terms-detail"><summary>Inspect original claim text</summary><p class="terms-label">Verbatim deal terms</p><p class="exact-terms">'+esc(r.observed_claim_text)+'</p></details>':'';
 document.getElementById("record-detail").innerHTML='<p class="detail-kicker">'+(unknown?'UNCERTAINTY EXAMPLE':loc?'DIRECTORY SNAPSHOT':'BIRTHDAY SOURCE RECORD')+'</p><h3>'+esc(r.public_name)+'</h3><p class="join-label">Join key: license_number = '+esc(r.license_number)+'</p><div class="badges"><span class="badge">'+(loc&&!unknown?'Directory export January 2026':'Last validated August 2026')+'</span>'+(unknown?'<span class="badge amber">Unknown scope</span>':'')+'</div><dl class="facts">'+facts+'</dl><div class="source-file">'+esc(unknown?'birthday-public.json · metadata projection':source.file)+'</div><p class="scope-note">'+esc(note)+'</p>'+terms+'<details><summary>View projected record JSON</summary><pre>'+esc(JSON.stringify(record,null,2))+'</pre></details>';
}
function renderProvenance(){
 const m=data.metrics;
 document.getElementById('stat-directory').textContent=m.directory_rows;
 document.getElementById('stat-birthday').textContent=m.birthday_rows;
 document.getElementById('stat-matched').textContent=m.birthday_joined_rows+' / '+m.birthday_rows;
 document.getElementById('stat-unknown').textContent=m.scope_counts.unknown;
 document.getElementById('sample-caption').textContent=m.sample_rows+' non-representative source-order records with explicit scope, plus one unknown-scope metadata example. Switch tabs to follow the same license.';
 const projection={schema_version:data.schema_version,reviewed_at:data.reviewed_at,deal_validation:data.deal_validation,sources:data.sources,metrics:data.metrics,selection:data.selection,adapter_evidence:data.adapter_evidence,exclusions:data.exclusions,unknowns:data.unknowns,source_review_sha256:data.source_review_sha256};
 document.getElementById('bridge-provenance').innerHTML='<p><strong>Coverage, not a quality score.</strong> The directory includes multiple license types; 540 rows does not mean 540 retail stores. Of 41 birthday records, '+m.scope_counts.group_wide+' are group-wide, '+m.scope_counts.per_location+' are per-location, and '+m.scope_counts.unknown+' remain unknown. There are '+m.birthday_unmatched_rows+' unmatched birthday keys and '+m.directory_duplicate_license_keys+' duplicate directory license keys. The '+m.directory_not_in_birthday+' directory rows outside the birthday export are not evidence of “no offer.”</p><p>The existing <strong>licenseSeedDirectory</strong> adapter hashes raw input, validates counts and dates, rejects invalid rows and duplicate identifiers, and preserves a historical evidence class. This view adds a narrower field allowlist; it does not run enrichment or production publishing.</p><pre>'+esc(JSON.stringify(projection,null,2))+'</pre>';
}
function setTab(next,focus){
 mode=next;
 ['locations','observations'].forEach(t=>{const el=document.getElementById('tab-'+t);el.classList.toggle('active',t===mode);el.setAttribute('aria-selected',t===mode);el.tabIndex=t===mode?0:-1;});
 document.getElementById('record-panel').setAttribute('aria-labelledby','tab-'+mode);
 renderRecords();if(focus)document.getElementById('tab-'+mode).focus();
}
['locations','observations'].forEach(t=>{const b=document.getElementById('tab-'+t);b.addEventListener('click',()=>setTab(t,false));b.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();setTab(e.key==='Home'?'locations':e.key==='End'?'observations':mode==='locations'?'observations':'locations',true);}});});
function renderLab(){
 const points=alg.fixture.slice();const incoming=shuffled?[points[0],points[3],points[7],points[1],points[5],points[2],points[6],points[4]]:points;
 const nearest=alg.nearest(incoming), improved=alg.improve(nearest), route=stage==="input"?incoming:stage==="nearest"?nearest:improved;
 const xy=p=>[(p.x/100)*460+50,350-(p.y/100)*300];
 const path=route.concat(route[0]).map((p,i)=>{const [x,y]=xy(p);return(i?"L":"M")+x.toFixed(2)+" "+y.toFixed(2)}).join(" ");
 document.getElementById("route-lines").innerHTML='<path d="'+path+'" fill="none" stroke="#d9f18b" stroke-width="2.2" stroke-linejoin="round" opacity=".9"/>';
 document.getElementById("route-points").innerHTML=points.map(p=>{const[x,y]=xy(p),origin=p.id==="A";return '<g><circle cx="'+x+'" cy="'+y+'" r="'+(origin?12:6)+'" fill="'+(origin?'#d9f18b':'#f5f4ec')+'" stroke="#103f32" stroke-width="2"/><text x="'+(x+(p.id==="G"?14:p.id==="B"?14:-14))+'" y="'+(y+(p.id==="F"?25:p.id==="A"?-18:-10))+'" fill="#f5f4ec" font-family="monospace" font-size="12" font-weight="bold">'+p.id+'</text></g>'}).join("");
 document.getElementById("route-cost").textContent=alg.cost(route).toFixed(1);
 document.getElementById("route-order").textContent=route.map(p=>p.id).concat("A").join(" → ");
 document.getElementById("stage-name").textContent={input:"Input-order result",nearest:"Nearest-neighbor result",improved:"2-opt result"}[stage];
 document.getElementById("route-desc").textContent="Synthetic points. "+document.getElementById("stage-name").textContent+": "+document.getElementById("route-order").textContent+". Cost "+alg.cost(route).toFixed(1)+" abstract units.";
 document.querySelectorAll("[data-stage]").forEach(b=>{b.classList.toggle("active",b.dataset.stage===stage);b.setAttribute("aria-pressed",b.dataset.stage===stage)});
 document.getElementById("reverse").innerHTML=(shuffled?"Restore input order":"Shuffle input order")+" <span aria-hidden='true'>↔</span>";
 document.getElementById("determinism-note").textContent=shuffled?"Input order shuffled. The nearest-neighbor and 2-opt results are unchanged for this fixture.":"Try changing input order. The fixed-origin nearest-neighbor and 2-opt results remain stable for this fixture.";
}
document.querySelectorAll("[data-stage]").forEach(b=>b.addEventListener("click",()=>{stage=b.dataset.stage;renderLab();}));
document.getElementById("reverse").addEventListener("click",()=>{shuffled=!shuffled;renderLab();});
renderRecords();renderProvenance();renderLab();
})();

