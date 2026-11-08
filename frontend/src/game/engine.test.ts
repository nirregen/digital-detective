import {describe,it,expect} from 'vitest';
import {freshState,collect,decrypt,available,optionsFor,interview,verifyTimeline,submitVerdict} from './engine';

describe('static investigation engine',()=>{
  it('starts with only public files',()=>{
    const s=freshState();expect(available(s)).toEqual(['e01','e03','e04','e07']);
    expect(optionsFor(s,'alex').some(x=>x.id==='badge')).toBe(false);
  });
  it('requires Maya desk note to solve cipher and gates encrypted logs',()=>{
    const s=freshState();expect(()=>decrypt(s,'CHECK THE BACKUP')).toThrow();
    const withNote=collect(s,'e04');expect(decrypt(withNote,'WRONG').correct).toBe(false);
    const result=decrypt(withNote,'check the backup');expect(result.correct).toBe(true);
    expect(available(result.state)).toContain('e02');
  });
  it('only permits an evidence-led contradiction',()=>{
    const s=freshState();expect(()=>interview(s,'alex','badge')).toThrow();
    const decoded=decrypt(collect(s,'e04'),'CHECK THE BACKUP').state;
    const found=collect(decoded,'e02');expect(optionsFor(found,'alex').some(x=>x.id==='badge')).toBe(true);
    const x=interview(found,'alex','badge');expect(x.contradiction).toBe(true);
    expect(x.state.character_states.alex.revealed).toContain('late_return');
    expect(optionsFor(x.state,'alex').some(x=>x.id==='badge')).toBe(false);
  });
  it('has a path to solve the full case',()=>{
    let s=freshState();for(const e of ['e01','e03','e04','e07'])s=collect(s,e);
    s=decrypt(s,'CHECK THE BACKUP').state;
    for(const e of ['e02','e05','e06'])s=collect(s,e);
    s=verifyTimeline(s,['audit','email','camera','badge']).state;
    s=collect(s,'e08');
    expect(submitVerdict(s,'alex',['e02','e06','e08']).correct).toBe(false);
    expect(submitVerdict(s,'leon',['e02','e06','e08']).state.finished).toBe(true);
  });
});
