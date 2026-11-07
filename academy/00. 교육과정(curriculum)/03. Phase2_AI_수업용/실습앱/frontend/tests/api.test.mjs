import test from 'node:test';
import assert from 'node:assert/strict';
import { askChat, getHealth, ApiError } from '../src/api.js';

function mockResponse(status, body) {
  globalThis.fetch = async () => ({status,ok:status>=200&&status<300,json:async()=>body});
}

test('기본 Chat 요청은 기존 message 필드를 사용한다', async () => {
  let call;
  globalThis.fetch = async (path, options) => {
    call = {path,options};
    return {ok:true,status:200,json:async()=>({provider:'fixture',model:'no-model',answer:'모의 답변'})};
  };
  const result=await askChat('안녕하세요');
  assert.equal(call.path,'/ai/chat');
  assert.equal(call.options.method,'POST');
  assert.deepEqual(JSON.parse(call.options.body),{message:'안녕하세요'});
  assert.equal(result.answer,'모의 답변');
});

test('health는 생성 요청이 아니다',async()=>{
  mockResponse(200,{status:'ok',provider:'fixture',model:'no-model'});
  assert.equal((await getHealth()).status,'ok');
});

for(const status of [422,502,503,504]) {
  test(`HTTP ${status} 사용자 오류`,async()=>{
    mockResponse(status,{detail:'fake error'});
    await assert.rejects(askChat('질문'),e=>e instanceof ApiError&&e.status===status);
  });
}

test('통신 자체 실패는 연결 오류로 안내한다',async()=>{
  globalThis.fetch=async()=>{throw new Error('socket closed');};
  await assert.rejects(askChat('질문'),e=>e instanceof ApiError&&e.status===null&&e.message.includes('연결'));
});

test('유효하지 않은 응답 JSON 거부',async()=>{
  globalThis.fetch=async()=>({status:200,ok:true,json:async()=>{throw new Error('bad json');}});
  await assert.rejects(askChat('질문'),e=>e instanceof ApiError&&e.status===200);
});
