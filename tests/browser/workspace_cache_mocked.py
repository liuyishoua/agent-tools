"""Offline acceptance: serve repository assets and fulfill every API with synthetic data."""
import base64,json,mimetypes,os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[3]
checks=[]

def setup(browser,assets,entry='index.html'):
    context=browser.new_context(viewport={'width':1440,'height':1000})
    def static(route):
        relative=urlsplit(route.request.url).path.lstrip('/')
        file=assets/(relative[7:] if relative.startswith('static/') else relative)
        if not file.is_file():file=assets/entry
        if file.suffix=='.html':
            route.fulfill(body=file.read_text().replace('<head>','<head><base href="/">',1),content_type='text/html')
        else:route.fulfill(path=str(file),content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
    context.route('**/*',lambda route:route.abort())
    context.route('https://cache.test/**',static)
    page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    return context,page,errors

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    # XHS: routes newly included in React keep-alive; synthetic account and local status only.
    context,page,errors=setup(browser,Path(os.environ.get('XHS_BUILD',ROOT/'xhs/frontend/dist')))
    owner={'id':901,'username':'缓存测试'};polls=[]
    def xhs_api(route):
        path=urlsplit(route.request.url).path
        if '/auth/' in path:value={'user':owner,'access_token':'synthetic','refresh_token':'synthetic'}
        elif path.endswith('/accounts'):value={'items':[{'id':101,'platform':'xhs','sub_type':'pc','status':'active','nickname':'测试账号'}]}
        elif path.endswith('/comments/monitoring'):
            polls.append(path);value={'configured':True,'items':[],'enabled':False,'state':'stopped','agent_id':'a','auto_reply':False,'control_mode':'full_access'}
        elif path.endswith('/comments/routes'):value={'connected':True,'agents':[{'id':'a','name':'测试助手A'},{'id':'b','name':'测试助手B'}]}
        else:value={'items':[],'total':0,'page':1,'page_size':20}
        route.fulfill(json=value)
    context.route('**/api/**',xhs_api)
    page.goto('https://cache.test/platforms/xhs/keywords')
    field=page.get_by_placeholder('关键词组名称');expect(field).to_be_visible()
    field.fill('未保存关键词组')
    page.evaluate("window.savedField=document.querySelector('input[placeholder=关键词组名称]')")
    def xhs_tab(name):page.locator(f'.ant-menu [data-page-route="/platforms/xhs/{name}"]').first.click()
    xhs_tab('discovery');expect(page.get_by_placeholder('低卡早餐、通勤穿搭')).to_be_visible()
    xhs_tab('keywords');expect(field).to_have_value('未保存关键词组')
    assert page.evaluate("savedField===document.querySelector('input[placeholder=关键词组名称]')")
    xhs_tab('comments')
    page.get_by_role('combobox',name='评论回复 Agent').click()
    page.locator('.ant-select-item-option-content').filter(has_text='测试助手B').click()
    xhs_tab('keywords');before=len(polls);page.wait_for_timeout(5300);assert len(polls)==before
    xhs_tab('comments');expect(page.locator('.ant-select').filter(has=page.get_by_role('combobox',name='评论回复 Agent'))).to_contain_text('测试助手B')
    page.wait_for_timeout(5300);assert len(polls)>before
    expect(page.locator('.ant-select').filter(has=page.get_by_role('combobox',name='评论回复 Agent'))).to_contain_text('测试助手B')
    page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert not errors,errors
    checks.append({'workbench':'xhs','new_routes_retain_dom_and_edits':True,'hidden_polling_paused':True,'visible_polling_resumes':True,'controls_not_overwritten':True,'mobile':True})
    context.close()

    # Application center: retain the actual React chat root, selected conversation, images and draft.
    context,page,errors=setup(browser,ROOT/'ops-hub/frontend/dist')
    owner={'id':901,'username':'缓存测试'}
    def hub_api(route):
        path=urlsplit(route.request.url).path
        if '/auth/' in path:value={'user':owner,'access_token':'synthetic'}
        elif path.endswith('/chat/config'):value={'available':True,'project':'tmp'}
        elif path.endswith('/chat/conversations'):value=[{'id':'test-chat','title':'测试对话','updated_at':'now'}]
        elif path.endswith('/chat/conversations/test-chat'):value={'id':'test-chat','title':'测试对话','messages':[],'busy':False,'status':'completed','has_older':False}
        else:raise AssertionError(path)
        route.fulfill(json=value)
    context.route('**/api/**',hub_api)
    page.goto('https://cache.test/platform-select?view=chat')
    page.locator('.ai-history-item').first.click()
    field=page.get_by_role('textbox',name='发送给 AI 的消息');expect(field).to_be_enabled();field.fill('未发送的 AI 对话内容')
    png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j3ioAAAAASUVORK5CYII=')
    page.locator('input[type=file]').set_input_files({'name':'缓存测试.png','mimeType':'image/png','buffer':png})
    expect(page.locator('.ai-image-attachment')).to_have_count(1)
    page.evaluate("window.savedChat=document.querySelector('.ai-chat')||document.querySelector('.ai-chat-panel');window.savedComposer=document.querySelector('textarea')")
    page.get_by_role('button',name='全部工作台',exact=True).click()
    page.get_by_role('textbox',name='搜索工作台').fill('小红书')
    page.get_by_role('button',name='和 AI 对话开始',exact=True).click()
    expect(field).to_have_value('未发送的 AI 对话内容')
    expect(page.locator('.ai-image-attachment')).to_have_count(1)
    assert page.evaluate("savedComposer===document.querySelector('textarea')")
    page.get_by_role('button',name='全部工作台',exact=True).click()
    expect(page.get_by_role('textbox',name='搜索工作台')).to_have_value('小红书')
    page.get_by_role('button',name='和 AI 对话开始',exact=True).click()
    owner={'id':902,'username':'另一账号'};page.evaluate("window.dispatchEvent(new Event('focus'))")
    expect(page.get_by_role('textbox',name='发送给 AI 的消息')).to_have_value('')
    assert not errors,errors
    checks.append({'workbench':'ops-hub','chat_root_retained':True,'draft_and_directory_filter_retained':True,'owner_switch_clears_cache':True})
    context.close()

    # Douyin automatic operations: stable shell/filters, same-data polling and account scope.
    context,page,errors=setup(browser,ROOT/'douyin/web/static','workbench.html')
    snapshot={'plans':[],'events':[],'jobs':[],'drafts':[],'audit':[],'counts':{}}
    def douyin_api(route):
        path=urlsplit(route.request.url).path
        if path.endswith('/workspace-identity'):value={'owner':{'id':901,'username':'缓存测试'},'hub_url':'https://cache.test/'}
        elif path.endswith('/accounts'):value={'items':[{'id':'a','name':'账号A'},{'id':'b','name':'账号B'}]}
        elif path.endswith('/operations'):value=snapshot
        else:raise AssertionError(path)
        route.fulfill(json=value)
    context.route('**/api/**',douyin_api)
    page.goto('https://cache.test/inbox')
    expect(page.locator('#account')).to_have_value('a')
    page.locator('[data-filter="failed"]').click()
    page.evaluate("window.savedInbox=document.querySelector('[data-filter=failed]')")
    page.locator('#nav [data-nav="plans"]').click();page.locator('#nav [data-nav="inbox"]').click()
    expect(page.locator('[data-filter="failed"]')).to_have_class('active')
    assert page.evaluate("savedInbox===document.querySelector('[data-filter=failed]')")
    page.wait_for_timeout(5300)
    assert page.evaluate("savedInbox===document.querySelector('[data-filter=failed]')")
    page.locator('#account').select_option('b')
    expect(page.locator('#account')).to_have_value('b')
    page.wait_for_timeout(200)
    assert page.evaluate("savedInbox!==document.querySelector('[data-filter=failed]')")
    assert not errors,errors
    checks.append({'workbench':'douyin','filters_and_dom_retained':True,'unchanged_poll_does_not_rebuild':True,'account_switch_clears_cache':True})
    context.close()

    context,page,errors=setup(browser,ROOT/'headquarters/headquarters/static')
    def headquarters_api(route):
        path=urlsplit(route.request.url).path
        value={'goals':[]} if path.endswith('/autonomy') else {'missions':[],'accounts':[],'channels':[],'audit':[]}
        route.fulfill(json=value)
    context.route('**/api/**',headquarters_api)
    page.goto('https://cache.test/')
    expect(page.locator('[data-act="new-goal"]').first).to_be_visible()
    page.evaluate("window.savedGoal=document.querySelector('#content [data-act=new-goal]')")
    page.locator('[data-tab="accounts"]').click();page.locator('[data-tab="autonomy"]').click()
    assert page.evaluate("savedGoal===document.querySelector('#content [data-act=new-goal]')")
    page.wait_for_timeout(5300)
    assert page.evaluate("savedGoal===document.querySelector('#content [data-act=new-goal]')")
    assert not errors,errors
    checks.append({'workbench':'headquarters','tab_dom_retained':True,'unchanged_poll_does_not_rebuild':True})
    context.close()

    context,page,errors=setup(browser,ROOT/'channel/channel_service/static')
    def channel_api(route):
        path=urlsplit(route.request.url).path
        if path.endswith('/meta'):value={'demo':True,'connected':False,'agents':[],'categories':['reply_draft'],'multica_url':'https://cache.test','workspace_slug':'demo'}
        elif path.endswith('/overview'):value={'counts':{},'messages':0}
        else:value={'items':[]}
        route.fulfill(json=value)
    context.route('**/api/**',channel_api)
    page.goto('https://cache.test/')
    page.locator('nav [data-page="compose"]').click()
    field=page.locator('#compose-form [name="text"]');field.fill('尚未提交给模型的消息')
    page.evaluate("window.savedCompose=document.querySelector('#compose-form')")
    page.locator('nav [data-page="messages"]').click();page.locator('nav [data-page="compose"]').click()
    expect(field).to_have_value('尚未提交给模型的消息')
    assert page.evaluate("savedCompose===document.querySelector('#compose-form')")
    assert not errors,errors
    checks.append({'workbench':'channel','composer_dom_and_draft_retained':True})
    context.close()

    context,page,errors=setup(browser,ROOT/'douyin-send/web/static')
    task_polls=[]
    def send_api(route):
        path=urlsplit(route.request.url).path
        if path.endswith('/meta'):value={'demo':True}
        elif path.endswith('/accounts'):value={'items':[]}
        elif path.endswith('/user-tags'):value={'items':[]}
        elif path.endswith('/message-templates'):value={'items':[]}
        elif path.endswith('/tasks'):task_polls.append(path);value={'items':[],'total':0,'page':1,'page_size':20}
        else:value={'items':[],'total':0,'page':1,'page_size':20}
        route.fulfill(json=value)
    context.route('**/api/**',send_api)
    page.goto('https://cache.test/search')
    field=page.locator('#search-form [name="query"]');expect(field).to_be_visible();field.fill('未提交的抖音搜索')
    page.evaluate("window.savedSearch=document.querySelector('#search-form')")
    page.locator('a.navlink[href="message-templates"]').click()
    expect(page.locator('.content h1')).to_be_visible()
    page.locator('a.navlink[href="search"]').click()
    expect(field).to_have_value('未提交的抖音搜索')
    assert page.evaluate("savedSearch===document.querySelector('#search-form')")
    page.go_back();page.go_forward();expect(field).to_have_value('未提交的抖音搜索')
    assert not errors,errors
    page.locator('a.navlink[href="tasks"]').click()
    expect(page.locator('#task-filters')).to_be_visible()
    page.locator('#task-filters [name="query"]').fill('保留任务筛选')
    page.evaluate("window.savedTasks=document.querySelector('#task-filters')")
    page.locator('a.navlink[href="message-templates"]').click()
    before=len(task_polls);page.wait_for_timeout(5300);assert len(task_polls)==before
    page.locator('a.navlink[href="tasks"]').click()
    expect(page.locator('#task-filters [name="query"]')).to_have_value('保留任务筛选')
    assert page.evaluate("savedTasks===document.querySelector('#task-filters')")
    page.wait_for_timeout(5300);assert len(task_polls)>before
    checks.append({'workbench':'douyin-send','search_dom_and_input_retained':True,'history':True,'task_polling_pauses_and_resumes':True})
    context.close()
    # Existing hidden-panel implementations already retain controls; verify rather than replace them.
    context,page,errors=setup(browser,ROOT/'ticket/web/static')
    context.route('**/api/**',lambda route:route.fulfill(json={'accounts':[],'tasks':[],'today':'2026-10-24','max_date':'2026-11-08'}))
    page.goto('https://cache.test/')
    field=page.locator('#train-filter');field.fill('G123')
    page.evaluate("window.savedFilter=document.querySelector('#train-filter')")
    page.locator('[data-page="tasks"]').click();page.locator('[data-page="query"]').click()
    expect(field).to_have_value('G123')
    assert page.evaluate("savedFilter===document.querySelector('#train-filter')")
    assert not errors,errors
    checks.append({'workbench':'ticket','existing_panel_retention_verified':True})
    context.close()

    context,page,errors=setup(browser,ROOT/'account-maintenance/maintenance/static')
    context.route('**/api/**',lambda route:route.fulfill(json={'accounts':[],'schedules':[],'jobs':[],'work_orders':[]}))
    page.goto('https://cache.test/')
    expect(page.locator('#main')).to_be_visible()
    page.locator('[data-tab="recovery"]').click()
    page.locator('[data-ticket-filter]').last.click()
    page.evaluate("window.savedTickets=document.querySelector('#tickets')")
    page.locator('[data-tab="accounts"]').click();page.locator('[data-tab="recovery"]').click()
    assert page.evaluate("savedTickets===document.querySelector('#tickets')")
    expect(page.locator('[data-ticket-filter]').last).to_have_class('primary')
    assert not errors,errors
    checks.append({'workbench':'account-maintenance','existing_panel_and_filter_retention_verified':True})
    context.close()
    browser.close()
print(json.dumps(checks,ensure_ascii=False))
