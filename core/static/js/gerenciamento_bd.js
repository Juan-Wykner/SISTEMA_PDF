const state={module:'pessoas',data:[],page:1,limit:20,search:'',status:'ATIVO',editing:null}
const endpoints={
  pessoas:{base:'/api/gbd/pessoas/'},
  classificacao:{base:'/api/gbd/classificacao/'},
  contas:{base:'/api/gbd/contas/'}
}
const columns={
  pessoas:[{k:'id',t:'ID'},{k:'tipo',t:'Tipo'},{k:'nome',t:'Nome'},{k:'cnpj_cpf',t:'CPF/CNPJ'},{k:'email',t:'Email'},{k:'telefone',t:'Telefone'},{k:'status',t:'Status'},{k:'actions',t:'Ações'}],
  classificacao:[{k:'id',t:'ID'},{k:'tipo',t:'Tipo'},{k:'descricao',t:'Descrição'},{k:'status',t:'Status'},{k:'actions',t:'Ações'}],
  contas:[{k:'id',t:'ID'},{k:'tipo',t:'Tipo'},{k:'descricao',t:'Descrição'},{k:'valor_total',t:'Valor'},{k:'status',t:'Status'},{k:'actions',t:'Ações'}]
}
function qs(x){return document.querySelector(x)}
function renderHead(){const thead=qs('#thead');thead.innerHTML='<tr>'+columns[state.module].map(c=>`<th>${c.t}</th>`).join('')+'</tr>'}
function renderRows(){const tbody=qs('#tbody');const start=(state.page-1)*state.limit;const rows=state.data.slice(start,start+state.limit);tbody.innerHTML=rows.map(r=>{
  const cells=columns[state.module].map(c=>{
    if(c.k==='actions')return `<td><div class="row-actions">${r.status==='ATIVO'?`<button data-act="edit" data-id="${r.id}">Editar</button><button data-act="del" data-id="${r.id}">Excluir</button>`:`<button data-act="react" data-id="${r.id}">Reativar</button>`}</div></td>`
    if(c.k==='status')return `<td><span class="badge ${r.status.toLowerCase()}">${r.status}</span></td>`
    return `<td>${r[c.k]??''}</td>`
  }).join('');
  return `<tr>${cells}</tr>`
}).join('')}
function renderPagination(){const total=Math.ceil(state.data.length/state.limit)||1;const el=qs('#pagination');let html='';for(let i=1;i<=total;i++){html+=`<button data-page="${i}" ${i===state.page?'class="primary"':''}>${i}</button>`}el.innerHTML=html}
async function fetchData(){const ep=endpoints[state.module].base;const url=`${ep}?status=${encodeURIComponent(state.status)}&search=${encodeURIComponent(state.search)}`;const r=await fetch(url);const j=await r.json();state.data=j.data||[];state.page=1;renderHead();renderRows();renderPagination()}
function openModal(title,fields){qs('#modalTitle').textContent=title;const f=qs('#formFields');f.innerHTML=fields.map(field=>{
  return `<label>${field.label}<input name="${field.name}" type="${field.type||'text'}" value="${field.value||''}" ${field.hidden?'style="display:none"':''}></label>`
}).join('');qs('#modal').classList.remove('hidden')}
function closeModal(){qs('#modal').classList.add('hidden');state.editing=null;qs('#form').reset()}
async function createRecord(){const ep=endpoints[state.module].base;const fd=new FormData(qs('#form'));const obj={};fd.forEach((v,k)=>obj[k]=v);let payload=obj
  if(state.module==='pessoas'){payload={nome:obj.nome,cnpj_cpf:obj.cnpj_cpf,email:obj.email,telefone:obj.telefone,tipo:obj.tipo||'FORNECEDOR'}}
  if(state.module==='classificacao'){payload={descricao:obj.descricao,tipo:obj.tipo||'DESPESA'}}
  if(state.module==='contas'){payload={descricao:obj.descricao,valor_total:parseFloat(obj.valor_total||'0'),tipo:obj.tipo||'PAGAR',data_emissao:obj.data_emissao||''}}
  const r=await fetch(ep,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':GBD.csrfToken},body:JSON.stringify(payload)});
  const j=await r.json();if(j.sucesso){closeModal();fetchData()}
}
async function updateRecord(id){const ep=endpoints[state.module].base+id+'/';const fd=new FormData(qs('#form'));const obj={};fd.forEach((v,k)=>obj[k]=v);const r=await fetch(ep,{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRFToken':GBD.csrfToken},body:JSON.stringify(obj)});const j=await r.json();if(j.sucesso){closeModal();fetchData()}
}
async function deleteRecord(id){const ep=endpoints[state.module].base+id+'/';const r=await fetch(ep,{method:'DELETE',headers:{'X-CSRFToken':GBD.csrfToken}});const j=await r.json();if(j.sucesso){fetchData()}}
async function reactivateRecord(id){const ep=endpoints[state.module].base+id+'/reativar/';const r=await fetch(ep,{method:'POST',headers:{'X-CSRFToken':GBD.csrfToken}});const j=await r.json();if(j.sucesso){fetchData()}}
function setup(){document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',e=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));e.currentTarget.classList.add('active');state.module=e.currentTarget.dataset.module;fetchData()}));
qs('#btnBuscar').addEventListener('click',()=>{state.search=qs('#search').value.trim();fetchData()});
const statusSel=document.querySelector('#statusFilter'); if(statusSel){statusSel.addEventListener('change',()=>{state.status=statusSel.value;});}
qs('#btnTodos').addEventListener('click',()=>{state.search=qs('#search').value.trim();state.status=(statusSel?statusSel.value:'ATIVO');fetchData()});
qs('#btnNovo').addEventListener('click',()=>{
  if(state.module==='pessoas')openModal('Nova Pessoa',[{label:'Nome',name:'nome'},{label:'CPF/CNPJ',name:'cnpj_cpf'},{label:'Email',name:'email'},{label:'Telefone',name:'telefone'},{label:'Tipo',name:'tipo'}])
  if(state.module==='classificacao')openModal('Nova Classificação',[{label:'Descrição',name:'descricao'},{label:'Tipo',name:'tipo'}])
  if(state.module==='contas')openModal('Nova Conta',[{label:'Descrição',name:'descricao'},{label:'Valor',name:'valor_total'},{label:'Tipo',name:'tipo'},{label:'Data Emissão',name:'data_emissao',type:'date'}])
});
qs('#btnCancelar').addEventListener('click',closeModal);
qs('#form').addEventListener('submit',e=>{e.preventDefault();if(state.editing){updateRecord(state.editing)}else{createRecord()}});
qs('#tbody').addEventListener('click',e=>{const t=e.target;const id=t.dataset.id;const act=t.dataset.act;if(!act)return;if(act==='edit'){state.editing=id;const row=state.data.find(x=>String(x.id)===String(id));const fields=[];Object.keys(row).forEach(k=>{if(['id','status'].includes(k))return;fields.push({label:k,name:k,value:row[k]})});openModal('Editar',fields)}if(act==='del'){deleteRecord(id)}if(act==='react'){reactivateRecord(id)}});
document.addEventListener('click',e=>{const p=e.target.closest('#pagination button');if(p){state.page=parseInt(p.dataset.page);renderRows();renderPagination()}})
fetchData()}
document.addEventListener('DOMContentLoaded',setup)
