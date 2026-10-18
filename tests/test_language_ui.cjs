'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const bank=JSON.parse(fs.readFileSync(path.join(root,'web/survey-bn.json'),'utf8'));

function browser() {
  const listeners={}, events=[], stored=new Map();
  const control={tagName:'FIELDSET',disabled:false,querySelectorAll:()=>buttons};
  const buttons=['en','bn'].map(language=>({dataset:{language},disabled:false,attributes:{},
    setAttribute(name,value){this.attributes[name]=value;},closest:()=>control}));
  const document={documentElement:{lang:'en'},body:{hasAttribute:()=>false},
    createTreeWalker:()=>({nextNode:()=>null}),querySelectorAll:()=>[],getElementById:()=>control,
    addEventListener:(type,listener)=>{listeners[type]=listener;}};
  let calls=0;
  const context={document,window:{dispatchEvent:event=>events.push(event)},
    NodeFilter:{SHOW_TEXT:4},MutationObserver:class{observe(){}disconnect(){}},
    URL,URLSearchParams,Event,location:{href:'http://localhost/?lang=en',search:'?lang=en'},history:{replaceState(){}},
    localStorage:{getItem:key=>stored.get(key),setItem:(key,value)=>stored.set(key,value)},
    fetch:async()=>{calls++;return {ok:true,json:async()=>bank};}};
  vm.runInNewContext(fs.readFileSync(path.join(root,'web/language.js'),'utf8'),context);
  return {...context,buttons,control,listeners,events,stored,get calls(){return calls;}};
}

test('all 321 Bangla options replace English API text by ID without changing order or values',async()=>{
  const runtime=browser();
  let count=0;
  for(const [mode,questions] of Object.entries(bank)) {
    const english={mode,seed:'keep-seed',version:'keep-version',language:'en',questions:Object.entries(questions).reverse()
      .map(([id,q])=>({id,trait:'keep-trait',text:'English question',options:Object.keys(q.options).reverse()
        .map(id=>({id:Number(id),text:'English option',value:Number(id)}))}))};
    const original=JSON.stringify(english);
    const translated=await runtime.window.MovieLocale.localizeSurvey(english,'bn');
    assert.equal(JSON.stringify(english),original);
    assert.equal(translated.seed,english.seed);
    assert.equal(translated.version,english.version);
    assert.equal(translated.language,'bn');
    assert.equal(translated.questions.length,english.questions.length);
    translated.questions.forEach((q,index)=>{
      const source=english.questions[index];
      assert.equal(q.id,source.id);
      assert.equal(q.trait,source.trait);
      assert.equal(q.text,questions[q.id].text);
      q.options.forEach((option,position)=>{
        assert.equal(option.id,source.options[position].id);
        assert.equal(option.value,source.options[position].value);
        assert.equal(option.text,questions[q.id].options[option.id]);
        assert.match(option.text,/[\u0980-\u09ff]/);
        assert.doesNotMatch(option.text,/[A-Za-z]/);
        count++;
      });
    });
    assert.equal(await runtime.window.MovieLocale.localizeSurvey(english,'en'),english);
  }
  assert.equal(count,321);
  assert.equal(runtime.calls,1);
});

test('the language toggle updates its selected state, persists choice, and respects disabled sharing controls',()=>{
  const runtime=browser();
  const click=button=>runtime.listeners.click({target:{closest:()=>button}});
  assert.equal(runtime.buttons[0].attributes['aria-pressed'],'true');
  click(runtime.buttons[1]);
  assert.equal(runtime.window.MovieLocale.lang,'bn');
  assert.equal(runtime.buttons[1].attributes['aria-pressed'],'true');
  assert.equal(runtime.buttons[0].attributes['aria-pressed'],'false');
  assert.equal(runtime.stored.get('moviegame-language'),'bn');
  assert.equal(runtime.events.length,1);
  click(runtime.buttons[1]);
  assert.equal(runtime.events.length,1);
  runtime.control.disabled=true;
  click(runtime.buttons[0]);
  assert.equal(runtime.window.MovieLocale.lang,'bn');
  runtime.control.disabled=false;
  click(runtime.buttons[0]);
  assert.equal(runtime.window.MovieLocale.lang,'en');
});
