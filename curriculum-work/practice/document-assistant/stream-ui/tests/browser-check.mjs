// node tests/browser-check.mjs BASE_URL OUTPUT_DIR
// Requires Playwright (PLAYWRIGHT_MODULE or installed package), optional BROWSER_EXECUTABLE.
import {createRequire} from 'node:module';
import {mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const [base,output]=process.argv.slice(2);await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:1120,height:900}});const errors=[];
page.on('pageerror',e=>errors.push(e.message));const observations=[];
const phase=p=>page.waitForSelector(`[data-phase="${p}"]`);
async function scenario(value){await page.selectOption('#scenario',value);await page.getByRole('button',{name:'전송 시작'}).click();}
try {
  await page.goto(base);assert.equal(await page.locator('[role=status]').textContent(),'실행 대기');
  assert.equal((await (await fetch(base+'/lab/runs')).json()).length,0);
  await scenario('normal');await phase('completed');assert.match(await page.getByTestId('answer').textContent(),/7일/);observations.push({case:'normal',ui:'completed'});
  await page.screenshot({path:output+'/desktop-completed.png',fullPage:true});
  for(const [value,expected] of [['error','실습 서버에서 오류'],['truncated','최종 판정을 받기 전에'],['refusal','지원하는 경로가 없습니다'],['deadline','시간 한도를 초과']]){
    await scenario(value);await phase('failed');assert.match(await page.getByRole('alert').textContent(),new RegExp(expected));observations.push({case:value,ui:'failed',detail:expected});
  }
  await scenario('slow');await page.waitForFunction(()=>document.querySelector('[data-testid=answer]').textContent.includes('가'));
  await page.getByRole('button',{name:'수신 취소'}).click();await phase('cancelled');
  await page.getByText('서버가 실습 전송의 취소 요청을 접수했습니다.',{exact:false}).waitFor();
  await page.waitForFunction(async()=>{const runs=await (await fetch('/lab/runs')).json();return runs.some(r=>r.scenario==='slow'&&r.status==='cancelled'&&r.cancel_requested);});
  observations.push({case:'cancel',ui:'cancelled',server:'cancelled',ack:true});
  await page.screenshot({path:output+'/desktop-cancelled.png',fullPage:true});
  // Delay only the cancellation acknowledgement; a new run must ignore it.
  let ackDone;const ackFinished=new Promise(resolve=>{ackDone=resolve;});
  await page.route('**/lab/cancel',async route=>{const response=await route.fetch();await new Promise(resolve=>setTimeout(resolve,350));await route.fulfill({response});ackDone();});
  await scenario('slow');await page.waitForFunction(()=>document.querySelector('[data-testid=answer]').textContent.includes('가'));
  await page.getByRole('button',{name:'수신 취소'}).click();await phase('cancelled');
  await scenario('normal');await phase('completed');await ackFinished;await page.unroute('**/lab/cancel');
  await page.waitForTimeout(400);assert.equal(await page.locator('[role=status]').getAttribute('data-phase'),'completed');observations.push({case:'restart_after_cancel_late_ack',ui:'completed'});
  // Malicious-looking text remains React text content, not executable HTML.
  const literal='<img src=x onerror="alert(1)">';
  await page.route('**/lab/stream',async route=>{const {id}=route.request().postDataJSON();const frames=[['start',{fixture:true}],['delta',{text:literal}],['final',{status:'completed',answer:literal}]].map(([event,value],seq)=>`event: ${event}\ndata: ${JSON.stringify({id,seq,...value})}\n\n`).join('');await route.fulfill({status:200,contentType:'text/event-stream',body:frames});});
  await scenario('normal');await phase('completed');assert.equal(await page.getByTestId('answer').textContent(),literal);assert.equal(await page.locator('img').count(),0);observations.push({case:'literal_html',ui:'completed',html_executed:false});await page.unroute('**/lab/stream');
  await page.setViewportSize({width:390,height:844});await scenario('normal');await phase('completed');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.screenshot({path:output+'/mobile-completed.png',fullPage:true});observations.push({case:'mobile_390px',ui:'completed',horizontal_overflow:false});
  assert.deepEqual(errors,[]);
  const runs=await (await fetch(base+'/lab/runs')).json();assert.equal(runs.length,9); // no automatic retry/reconnect
  assert.equal(runs.filter(r=>r.scenario==='normal').length,3);
  await writeFile(output+'/browser.json',JSON.stringify({browser:await browser.version(),cases:observations,server_runs:runs,page_errors:errors,actual_model_calls:0,buffered_fixture_delivery:true},null,2)+'\n');
  console.log(JSON.stringify({browser_cases:observations.length,server_runs:runs.length,page_errors:errors.length}));
}finally{await browser.close();}
