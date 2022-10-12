from time import sleep
from playwright.sync_api import sync_playwright
import os


if __name__ == "__main__":
    url = 'https://qah5.zhihuishu.com/qa.html#/web/home/1000006196?role=2&recruitId=142571&VNK=41d4ba85'
    cookie = 'login_cookie.json'
    need_login = os.path.exists(cookie) == False
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)  # 启动chrome浏览器
    context = browser.new_context(storage_state= cookie if not need_login else None)
    page = context.new_page()
    
    page.goto(url)

    if need_login:
        print('请完成登录并等待页面加载完成，完成后输入任意内容回车开启脚本。')
        input()
        context.storage_state(path = cookie)

    #app > div > div.web-qa-body > div.web-qa-main-left > div > div.infinite-list-wrapper.question-list-container.el-scrollbar > div.el-scrollbar__wrap > div > ul > li:nth-child(2)
    # last_topic = topics.locator('div.el-scrollbar__wrap > div > ul > li:nth-child(1000)').scroll_into_view_if_needed()
    scroll_bar_path = '#app > div > div.web-qa-body > div.web-qa-main-left > div > div.infinite-list-wrapper.question-list-container.el-scrollbar > div.el-scrollbar__bar.is-vertical > div'
    scroll_bar = page.locator(scroll_bar_path)
    page.click('text=最新')
    
    for _ in range(5):
        # 拖拽滚动条加载
        box=scroll_bar.bounding_box()
        page.mouse.move(box['x']+box['width']/2,box['y']+box[ 'height']/2)
        page.mouse.down()
        mov_y=box['y']+box['height']/2+800
        page.mouse.move(box['x']+box['width']/2, mov_y)
        page.mouse.up()
        sleep(1)
    sleep(3)

    topics = page.locator('#app > div > div.web-qa-body > div.web-qa-main-left > div > div.infinite-list-wrapper.question-list-container.el-scrollbar > div.el-scrollbar__wrap > div > ul > li')
    print(f'话题数量：{topics.count()}')
    count = 0
    for i in range(1, topics.count()):
        topic = topics.nth(i)
        #app > div > div.web-qa-body > div.web-qa-main-left > div > div.infinite-list-wrapper.question-list-container.el-scrollbar > div.el-scrollbar__wrap > div > ul > li:nth-child(2) > div.question-bottom > div.qb-left > div.qb-answers.ZHIHUISHU_QZMD
        reply_num = topic.locator('div.question-bottom > div.qb-left > div.qb-answers.ZHIHUISHU_QZMD').inner_text()
        # 选取有回答的问题
        if reply_num[0] == '0':
            continue
        with context.expect_page() as new_page_info:
            #app > div > div.web-qa-body > div.web-qa-main-left > div > div.infinite-list-wrapper.question-list-container.el-scrollbar > div.el-scrollbar__wrap > div > ul > li:nth-child(2) > div.question-content.ZHIHUISHU_QZMD
            topic.locator("div.question-content.ZHIHUISHU_QZMD").click()
        detail_page = new_page_info.value  # 返回一个新页面
        my_reply = detail_page.locator('#app > div > div.question-all.clearfix > div.question-left > div.answer-box > ul > li:nth-child(1) > div.answer-content > p > span').inner_text()
        open_reply = detail_page.locator('#app > div > div.my-answer-btn.ZHIHUISHU_QZMD.tool-show')
        # 已回答过该问题
        if open_reply.count()==0:
            detail_page.close()
            continue
        detail_page.click('#app > div > div.my-answer-btn.ZHIHUISHU_QZMD.tool-show') # 打开回答界面
        sleep(0.1)
        detail_page.fill('#app > div > div.questionDialog.ZHIHUISHU_QZMD > div > div > div.el-dialog__body > div.dialog_body > div.input-box > div > textarea', my_reply)# 填入回复
        sleep(0.5)
        detail_page.click('#app > div > div.questionDialog.ZHIHUISHU_QZMD > div > div > div.el-dialog__body > div.dialog_body > div.dialog-bottom.clearfix > div')# 发布
        sleep(0.5)
        detail_page.close()
        count += 1
        print(f'已回复{count}条')
        sleep(20)


    browser.close()
        