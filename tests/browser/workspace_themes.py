"""Offline theme acceptance against real entry assets and synthetic APIs only."""
import json,os,re
from pathlib import Path
from playwright.sync_api import expect
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.local/workspace-themes';OUT.mkdir(parents=True,exist_ok=True)
RESULTS=[]
CONTRAST=r'''() => {
 const rgb=value=>{const n=value.match(/[\d.]+/g)?.map(Number)||[0,0,0,0];return [n[0],n[1],n[2],n[3]??1]};
 const over=(a,b)=>{const alpha=a[3]+b[3]*(1-a[3]);return [0,1,2].map(i=>(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/(alpha||1)).concat(alpha)};
 const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,n,i)=>s+n*[.2126,.7152,.0722][i],0);
 const rows=[];
 for(const node of document.querySelectorAll('body *')){
  const text=[...node.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).map(n=>n.textContent).join('').trim();
  if(!text||!node.getClientRects().length||node.closest('button:disabled,[aria-disabled=true],[aria-hidden=true],script,style,.avatar,.brandmark,.brand-icon,.ant-avatar,.ant-btn-loading'))continue;
  const style=getComputedStyle(node);if(style.visibility==='hidden'||Number(style.opacity)===0)continue;
  let bg=[255,255,255,1],chain=[];
  for(let p=node;p;p=p.parentElement)chain.push(p);
  if(chain.some(p=>getComputedStyle(p).backgroundImage!=='none'))continue;
  for(const p of chain.reverse())bg=over(rgb(getComputedStyle(p).backgroundColor),bg);
  const fg=over(rgb(node instanceof SVGElement&&node.tagName==='text'?style.fill:style.color),bg);
  const l1=lum(fg),l2=lum(bg),ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
  const large=parseFloat(style.fontSize)>=24||(parseFloat(style.fontSize)>=18.66&&Number(style.fontWeight)>=700);
  if(ratio<(large?3:4.5)-.05)rows.push({text:text.slice(0,55),tag:node.tagName,cls:node.className?.baseVal??node.className,ratio:+ratio.toFixed(2),color:style.color,bg:bg.slice(0,3)});
 }
 return rows;
}'''
def audit(page,name):
 page.set_viewport_size({'width':1440,'height':1000})
 is_hub=name.startswith('ops-hub');attr='data-theme' if is_hub else 'data-workspace-theme'
 toggle=page.locator('[data-workspace-action="theme"],[data-theme-toggle],button[aria-label="切换主题"],button[title="切换为浅色模式"],button[title="切换为暗色模式"],button[title="切换为深色模式"]').first
 expect(toggle).to_be_visible()
 modes={}
 for mode in ['light','dark']:
  if page.locator('html').get_attribute(attr)!=mode:toggle.click()
  expect(page.locator('html')).to_have_attribute(attr,mode)
  page.wait_for_timeout(350)
  modes[mode]=page.evaluate(CONTRAST)
  page.screenshot(path=str(OUT/(name+'-'+mode+'.png')),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(name,mode,'mobile overflow')
  page.screenshot(path=str(OUT/(name+'-'+mode+'-mobile.png')),full_page=True)
  page.set_viewport_size({'width':1440,'height':1000})
  # Actual form controls and major surfaces must follow the selected palette.
  field=page.locator('input:not([type=checkbox]):not([type=file]):visible,textarea:visible,select:visible').first
  if field.count():
   background=field.evaluate('node=>getComputedStyle(node).backgroundColor')
   values=[float(v) for v in re.findall(r'[\d.]+',background)]
   if len(values)<4 or values[3]>0:
    assert (sum(values[:3])/3>180)==(mode=='light'),(name,mode,background)
 second=page.context.new_page()
 second.goto(page.url,wait_until='domcontentloaded')
 expect(second.locator('html')).to_have_attribute(attr,'dark')
 second.close()
 RESULTS.append({'workbench':name,'modes':modes,'stored_preference':True,'mobile':True})
 print(name,{key:len(value) for key,value in modes.items()},flush=True)

def run_mocked():
 source=ROOT/'agent-tools/tests/browser/workspace_cache_mocked.py'
 code=source.read_text().replace('    context.close()','    audit(page,checks[-1][\'workbench\'])\n    context.close()')
 exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'__main__','audit':audit})

def run_demos():
 source=ROOT/'agent-tools/tests/browser/workspace_tabs.py'
 code=source.read_text().replace('                context.close()', '                audit(page,name)\n                context.close()')
 exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'__main__','audit':audit})

if __name__=='__main__':
 run_mocked();run_demos()
 (OUT/'results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2))
 print('Theme audit saved:',OUT/'results.json')
 failures=[(row['workbench'],mode,issue) for row in RESULTS for mode,issues in row['modes'].items() for issue in issues]
 assert not failures,failures
