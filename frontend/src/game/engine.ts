import case001 from '../data/case001.json';
import characters from '../data/characters.json';

export type CharacterId = 'alex' | 'dana' | 'leon';
export type Evidence = {id:string;title:string;kind:string;content:string;requires:string[];needs_evidence?:string[]};
export type Character = {id:string;name:string;role:string;opening:string};
export type CaseData = {id:string;title:string;tagline:string;intro:string;characters:Character[];evidence:Evidence[];puzzles:{decrypt:{name:string;instruction:string;answer:string};timeline:{name:string;instruction:string;events:{id:string;label:string}[];answer:string[]}};solution:{responsible:string;required_evidence:string[];summary:string}};
export type CharacterState={trust:number;pressure:number;mood:string;interactions:number;revealed:string[]};
export type InterviewTurn={character:string;question:string;reply:string;evidence?:string|null;optionId:string};
export type State={version:number;character_states:Record<string,CharacterState>;collected:string[];solved:string[];interviews:InterviewTurn[];finished:boolean;result:string|null;events:{type:string;id?:string;correct?:boolean}[]};
export type DialogueOption={id:string;text:string;reply:string;requires?:string[];requiresSolved?:string[];requiresRevealed?:string[];repeatable?:boolean;trustDelta?:number;pressureDelta?:number;reveals?:string;contradiction?:boolean};
export const caseData:CaseData=case001;
const config=characters as Record<string,{starting_trust:number;starting_pressure:number}>;
const clamp=(v:number)=>Math.max(0,Math.min(100,v));
export function freshState():State {return {version:1,collected:[],solved:[],interviews:[],character_states:Object.fromEntries(Object.entries(config).map(([id,c])=>[id,{trust:c.starting_trust,pressure:c.starting_pressure,mood:'guarded',interactions:0,revealed:[]}])),finished:false,result:null,events:[]};}
const KEY='dd-static-case001-v1';
export function loadState():State {try {const raw=localStorage.getItem(KEY);if(!raw)return freshState();const data=JSON.parse(raw) as State;if(data.version!==1||!Array.isArray(data.collected)||!Array.isArray(data.solved)||!Array.isArray(data.interviews)||!data.character_states||typeof data.finished!=='boolean')return freshState();return data;}catch{return freshState();}}
export function saveState(s:State) {try {localStorage.setItem(KEY,JSON.stringify(s));}catch{ /* storage might be unavailable */ }}
export function available(s:State):string[] {return caseData.evidence.filter(e=>e.requires.every(id=>s.solved.includes(id)) && (e.needs_evidence||[]).every(id=>s.collected.includes(id))).map(e=>e.id);}
export function collect(s:State,id:string):State {if(!available(s).includes(id))throw Error('Evidence is locked');if(s.collected.includes(id))return s;return {...s,collected:[...s.collected,id],events:[...s.events,{type:'evidence_collected',id}]};}
export function decrypt(s:State,answer:string):{correct:boolean;state:State} {if(!s.collected.includes('e04'))throw Error('Find Maya\'s desk note first');const norm=(v:string)=>v.toUpperCase().replace(/[^A-Z]/g,'');const correct=norm(answer)===norm(caseData.puzzles.decrypt.answer);return {correct,state:correct&&!s.solved.includes('decrypt')?{...s,solved:[...s.solved,'decrypt'],events:[...s.events,{type:'puzzle_solved',id:'decrypt'}]}:s};}
export function verifyTimeline(s:State,order:string[]):{correct:boolean;state:State}{if(!['e01','e02','e03','e06'].every(id=>s.collected.includes(id)))throw Error('Collect E01, E02, E03 and E06 first');const correct=JSON.stringify(order)===JSON.stringify(caseData.puzzles.timeline.answer);return {correct,state:correct&&!s.solved.includes('timeline')?{...s,solved:[...s.solved,'timeline'],events:[...s.events,{type:'puzzle_solved',id:'timeline'}]}:s};}
export const dialogues:Record<CharacterId,DialogueOption[]>={
 alex:[
  {id:'last_seen',text:'When did you last see Maya?',reply:'Before eight. She was at her desk when I left. I had no reason to check on her.',trustDelta:0},
  {id:'left',text:'Are you sure you never returned?',reply:'I told you I went home. Do you have something that says otherwise?',pressureDelta:3},
  {id:'reassure',text:'I know you were trying to protect someone.',reply:'You think this is easy? I have a job, a family. People can get hurt if I say the wrong thing.',trustDelta:9,pressureDelta:-3},
  {id:'accuse',text:'You are lying about that night.',reply:'Careful. You can call me a liar when you have proof.',trustDelta:-7,pressureDelta:10},
  {id:'badge',text:'Your badge entered the server room at 22:14. Explain.',reply:'...Yes. I came back. I helped make a backup. I should have told you that sooner.',requires:['e02'],reveals:'late_return',pressureDelta:15,contradiction:true},
  {id:'backup',text:'I have the backup manifest. What were you copying?',reply:'An encrypted snapshot of the audit records. I didn\'t look inside it. I just made sure the copy was safe.',requires:['e05'],reveals:'backup',trustDelta:2},
  {id:'who',text:'Who asked you to make that backup?',reply:'I won\'t put another person at risk on your word alone. Look at the audit changes first.',requiresRevealed:['late_return'],pressureDelta:3},
  {id:'audit',text:'The records were changed using Leon\'s account.',reply:'Then you understand why the backup mattered. Keep looking at the original records.',requires:['e06'],trustDelta:4}
 ],
 dana:[
  {id:'maya',text:'How well did you know Maya?',reply:'We worked closely. She was careful, almost annoyingly so. She wouldn\'t just vanish without a reason.',trustDelta:3},
  {id:'audit',text:'What worried Maya about the audit reports?',reply:'Numbers weren\'t matching what we had approved. She kept comparing the current reports with older exports.',trustDelta:3},
  {id:'email',text:'Do you believe Maya wrote the resignation email?',reply:'No. That isn\'t how she writes. And she wouldn\'t leave a project unfinished without warning us.',requires:['e01'],trustDelta:2},
  {id:'camera',text:'Who was in the service stairwell?',reply:'I can\'t tell from that image. Please don\'t guess who it was.',requires:['e03'],pressureDelta:5},
  {id:'support',text:'I only want to make sure Maya is safe.',reply:'Then follow the records, not the rumours. That\'s what Maya would have wanted.',trustDelta:10,pressureDelta:-4},
  {id:'audit-proof',text:'The audit diff shows Leon\'s privileged account.',reply:'I saw it too. That was the change Maya was investigating. She was right to be worried.',requires:['e06'],reveals:'audit_changes',pressureDelta:4},
  {id:'voice',text:'I recovered Maya\'s voice note. You helped her?',reply:'Yes. I helped find somewhere safe. She wanted time to preserve the evidence before anyone erased it.',requires:['e08'],reveals:'maya_safe',trustDelta:7}
 ],
 leon:[
  {id:'resignation',text:'Why did Maya resign so suddenly?',reply:'I cannot speak for her personal decisions. Her email was explicit.',trustDelta:0},
  {id:'last_contact',text:'When did you last speak to her?',reply:'We spoke during the workday. This line of questioning seems rather speculative.',pressureDelta:2},
  {id:'email',text:'The resignation email does not sound like Maya.',reply:'Personal impressions are not evidence, detective. The message is in writing.',requires:['e01'],pressureDelta:4},
  {id:'camera',text:'Two people left through the service stairwell.',reply:'And? You have a blurry image of two people leaving a building. That proves nothing.',requires:['e03'],pressureDelta:4},
  {id:'accuse',text:'You have something to hide.',reply:'An accusation without supporting records is not an investigation.',trustDelta:-8,pressureDelta:8},
  {id:'diff',text:'Your privileged account changed the audit records at 19:52.',reply:'It shows my account was used. It does not establish who was at the keyboard. Be precise.',requires:['e06'],reveals:'privileged_account',pressureDelta:18,contradiction:true},
  {id:'voice',text:'Maya says you were erasing evidence.',reply:'An allegation made in a recording does not replace a proper forensic audit.',requires:['e08'],pressureDelta:15}
 ]
};
export function optionsFor(s:State,id:CharacterId):DialogueOption[]{const cs=s.character_states[id];return dialogues[id].filter(o=>(o.requires||[]).every(e=>s.collected.includes(e)) && (o.requiresSolved||[]).every(p=>s.solved.includes(p)) && (o.requiresRevealed||[]).every(r=>cs.revealed.includes(r)) && (o.repeatable||!s.interviews.some(t=>t.character===id&&t.optionId===o.id)));}
export function interview(s:State,id:CharacterId,optionId:string):{state:State;reply:string;contradiction:boolean}{const option=optionsFor(s,id).find(o=>o.id===optionId);if(!option)throw Error('This question is not available yet');const current=s.character_states[id];const next:CharacterState={...current,trust:clamp(current.trust+(option.trustDelta||0)),pressure:clamp(current.pressure+(option.pressureDelta||0)),interactions:current.interactions+1,revealed:option.reveals&&!current.revealed.includes(option.reveals)?[...current.revealed,option.reveals]:[...current.revealed]};next.mood=next.pressure>=70&&next.trust<45?'defensive':next.trust>=60?'cooperative':next.pressure>=45?'tense':'guarded';const reply=option.reply;return {state:{...s,character_states:{...s.character_states,[id]:next},interviews:[...s.interviews,{character:id,question:option.text,reply,optionId:option.id,evidence:option.requires?.[0]}],events:[...s.events,{type:'interview',id}]},reply,contradiction:Boolean(option.contradiction)};}
export function submitVerdict(s:State,responsible:string,evidenceIds:string[]):{correct:boolean;message:string;state:State}{if(!['e02','e06','e08'].every(id=>s.collected.includes(id)))throw Error('Investigate further before submitting your verdict');if(!evidenceIds.every(id=>s.collected.includes(id)))throw Error('Select only collected evidence');const correct=responsible===caseData.solution.responsible&&caseData.solution.required_evidence.every(id=>evidenceIds.includes(id));return {correct,message:correct?caseData.solution.summary:'The evidence does not support that conclusion. Review the audit trail and Maya’s note.',state:{...s,finished:correct,result:correct?'solved':'incorrect',events:[...s.events,{type:'verdict',correct}]}};}
