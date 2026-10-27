"""Native workbench retention acceptance, always with isolated DemoPlatform stores."""
import json, subprocess, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[3]
checks=[]
with tempfile.TemporaryDirectory(prefix='workspace-tabs-') as temporary, sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    for index,name in enumerate(['bilibili','kuaishou','jd','weibo','zhihu']):
        port=18871+index;base=f'http://127.0.0.1:{port}'
        with open(Path(temporary)/(name+'.log'),'w') as log:
            server=subprocess.Popen([str(ROOT/name/'.venv/bin/python'),'-m','web','--demo','--no-auth','--port',str(port),'--data-dir',str(Path(temporary)/name)],cwd=ROOT/name,stdout=log,stderr=log)
            try:
                for attempt in range(80):
                    try:
                        meta=json.load(urllib.request.urlopen(base+'/api/meta',timeout=1));break
                    except OSError:time.sleep(.15)
                else:raise AssertionError('Demo failed: '+name)
                assert meta['demo']
                context=browser.new_context(viewport={'width':1440,'height':900})
                page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(base);expect(page.locator('[data-page="drafts"]').first).to_be_visible()
                # Wait for initial local data bootstrap before editing.
                expect(page.locator('#state')).not_to_contain_text('正在读取')
                page.locator('nav [data-page="drafts"]').click()
                form=page.locator('#draft-form');expect(form).to_be_visible()
                form.locator('[name="title"]').fill('切页保留测试 '+name)
                form.locator('[name="text"]').fill('未保存的测试草稿，不发布')
                page.evaluate("window.savedDraft=document.querySelector('#draft-form');window.savedSidebar=document.querySelector('.sidebar')")
                page.locator('nav [data-page="library"]').click()
                page.locator('nav [data-page="drafts"]').click()
                expect(form.locator('[name="title"]')).to_have_value('切页保留测试 '+name)
                assert page.evaluate("savedDraft===document.querySelector('#draft-form')&&savedSidebar===document.querySelector('.sidebar')")
                # Retained form handlers must still submit to this isolated local store.
                form.locator('button[type="submit"],button.primary').first.click()
                expect(page.locator('.draft-list')).to_contain_text('切页保留测试 '+name)
                page.locator('nav [data-page="library"]').click();page.go_back()
                expect(page.locator('#draft-form')).to_be_visible()
                page.locator('nav [data-page="account"]').click()
                page.locator('[data-action="disconnect"]').click()
                expect(page.locator('[data-action="disconnect"]')).to_be_disabled()
                page.locator('nav [data-page="drafts"]').click()
                expect(page.locator('#draft-form [name="title"]')).to_have_value('')
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                assert not errors,errors
                checks.append({'workbench':name,'live_dom':True,'unsaved_draft':True,'events_after_restore':True,'history':True,'account_reset':True,'mobile':True})
                context.close()
            finally:
                server.terminate();server.wait(timeout=10)
    browser.close()
print(json.dumps(checks,ensure_ascii=False))
