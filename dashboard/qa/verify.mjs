import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const folder = path.dirname(fileURLToPath(import.meta.url));
const dashboard = path.resolve(folder, '..');
const modulePath = process.env.DASHBOARD_PLAYWRIGHT_MODULE || '/Users/shreyitsinha/code/blitz_landing/node_modules/playwright-core/index.mjs';
const executable = process.env.DASHBOARD_BROWSER_PATH || '/Users/shreyitsinha/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const {chromium} = await import(pathToFileURL(modulePath).href);
const screenshots = path.join(folder, 'screenshots');
fs.mkdirSync(screenshots, {recursive:true});
const cases = [
  {id:'13-inch',width:1280,height:720,dpr:2,label:'13.6-inch MacBook Air reference; conservative content viewport'},
  {id:'14-inch',width:1512,height:850,dpr:2,label:'14.2-inch MacBook Pro reference; conservative content viewport'},
  {id:'15-inch',width:1440,height:800,dpr:2,label:'15.3-inch MacBook Air reference; conservative content viewport'},
  {id:'generic-1366',width:1366,height:768,dpr:1,label:'Additional common laptop content viewport'},
  {id:'compact-height',width:1280,height:640,dpr:1,label:'Reduced vertical space / browser-chrome stress check'},
];
const results=[];
const errors=[];
const browser=await chromium.launch({headless:true,executablePath:executable});
try {
  for(const size of cases){
    const context=await browser.newContext({viewport:{width:size.width,height:size.height},deviceScaleFactor:size.dpr});
    const page=await context.newPage();
    page.on('pageerror',error=>errors.push(String(error)));
    await page.goto(pathToFileURL(path.join(dashboard,'dist/index.html')).href);
    await page.waitForFunction(()=>window.__DASHBOARD_READY__===true);
    await page.evaluate(()=>document.fonts.ready);
    for(const name of ['overview','focus']){
      await page.click('#tab-'+name);
      const geometry=await page.evaluate(()=>{
        const visible=el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
        const violations=[];
        const root=document.documentElement;
        if(root.scrollWidth>innerWidth+1||root.scrollHeight>innerHeight+1)violations.push({type:'document-scroll',width:root.scrollWidth,height:root.scrollHeight});
        for(const el of document.querySelectorAll('.dashboard-page:not([hidden]),.kpi-row,.overview-top-grid,.focus-top-grid,.focus-bottom-grid,[data-panel],.kpi,.panel-heading,.question-row,.group-row,.dimension-row,.action-row,.voice-row,.focus-bar-row,.toolbar,.footer')){
          if(!visible(el))continue;
          const r=el.getBoundingClientRect();
          if(r.left<-.5||r.top<-.5||r.right>innerWidth+.5||r.bottom>innerHeight+.5)violations.push({type:'outside-viewport',tag:el.className,rect:{x:r.x,y:r.y,w:r.width,h:r.height}});
          if(el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2)violations.push({type:'content-overflow',tag:el.className,client:[el.clientWidth,el.clientHeight],scroll:[el.scrollWidth,el.scrollHeight]});
        }
        return {width:innerWidth,height:innerHeight,documentWidth:root.scrollWidth,documentHeight:root.scrollHeight,violations};
      });
      await page.screenshot({path:path.join(screenshots,`${size.id}-${name}.png`),fullPage:false});
      results.push({id:size.id,page:name,viewport:[size.width,size.height],devicePixelRatio:size.dpr,...geometry});
      if(geometry.violations.length) console.log('LAYOUT',size.id,name,JSON.stringify(geometry.violations));
    }
    await context.close();
  }

  // Real browser interaction checks on the smallest requested laptop reference.
  const context=await browser.newContext({viewport:{width:1280,height:720}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(String(error)));
  await page.goto(pathToFileURL(path.join(dashboard,'dist/index.html')).href);
  await page.waitForFunction(()=>window.__DASHBOARD_READY__===true);
  assert.match(await page.locator('#overview-kpis').innerText(),/327/);
  assert.match(await page.locator('#overview-kpis').innerText(),/84\.9%/);
  await page.click('[data-dim="CRE"]');
  assert.equal(await page.locator('#selected-dimension').innerText(),'Credibility');
  assert.equal(await page.locator('#question-rows .question-row').count(),5);
  await page.selectOption('#department','Customer Service');
  assert.match(await page.locator('#scope-label').innerText(),/51 responses/);
  await page.selectOption('#tenure','10 - 15');
  const status=await page.evaluate(()=>window.DASHBOARD_DATA.cohorts['Customer Service|10 - 15'].status);
  if(status!=='ready')assert.match(await page.locator('#question-rows').innerText(),/withheld|No matching/);
  await page.click('#reset');
  assert.match(await page.locator('#scope-label').innerText(),/327 responses/);
  await page.selectOption('#group-by','department');
  assert.equal(await page.locator('#group-chart .group-row').count(),8);
  await page.click('#tab-focus');
  assert.equal(await page.locator('#overview-controls').isVisible(),false);
  assert.equal(await page.locator('#focus-controls').isVisible(),true);
  assert.match(await page.locator('#focus-kpis').innerText(),/137/);
  assert.match(await page.locator('#paired-table').innerText(),/45/);
  assert.equal(await page.locator('#fairness-chart .focus-bar-row').count(),5);
  await page.click('#method-button');
  assert.equal(await page.locator('#method-dialog').isVisible(),true);
  const dialogFits=await page.locator('#method-dialog').evaluate(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&el.scrollHeight<=el.clientHeight+1});
  assert.equal(dialogFits,true);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#method-dialog').isVisible(),false);
  await page.focus('#tab-focus');await page.keyboard.press('ArrowLeft');
  assert.equal(await page.locator('#overview').isVisible(),true);
  await page.reload();
  await page.waitForFunction(()=>window.__DASHBOARD_READY__===true);
  assert.equal(await page.locator('#overview').isVisible(),true);
  // No browser data includes original text responses, names, or individual source rows.
  const privacy=await page.evaluate(()=>{
    const t=JSON.stringify(window.DASHBOARD_DATA);
    return {hasRawField:/"(?:full_name|source_row|oe_leaders_trust|oe_one_change)"/.test(t),
      belowTenLeak:Object.values(window.DASHBOARD_DATA.cohorts).some(c=>c.status==='suppressed'&&(c.n!==null||c.items!==undefined))};
  });
  assert.deepEqual(privacy,{hasRawField:false,belowTenLeak:false});
  // The source entry point used by IDE previews must load the same snapshot.
  await page.goto(pathToFileURL(path.join(dashboard,'src/index.html')).href);
  await page.waitForFunction(()=>window.__DASHBOARD_READY__===true);
  assert.match(await page.locator('#overview-kpis').innerText(),/84\.9%/);
  await page.click('#tab-focus');
  assert.match(await page.locator('#focus-kpis').innerText(),/137/);
  await context.close();
  const failed=results.filter(r=>r.violations.length);
  fs.writeFileSync(path.join(folder,'results.json'),JSON.stringify({browser:'Chromium headless',cases:results,errors,interactionChecks:'passed',notes:'Viewport sizes are assumed content areas, not manufacturer default settings.'},null,2)+'\n');
  assert.equal(errors.length,0,errors.join('\n'));
  assert.equal(failed.length,0,`${failed.length} viewport/page layouts overflow; inspect qa/results.json`);
  console.log(`PASS: ${results.length} viewport/page layouts without document or panel scrolling; filters, suppression, drill-down, navigation, measure notes and privacy checks passed.`);
} finally {await browser.close();}
