##code=utf8
import asyncio
from playwright.async_api import async_playwright
import argparse
import time
import os
import html2text
import platform
import re
from bs4 import BeautifulSoup
import jionlp
async def scroll(page,pausetime):
            # scrollingElement.scrollTop = scrollingElement.scrollHeight;


    await page.evaluate(
        """
        var intervalID = setInterval(function () {
            var scrollingElement = (document.scrollingElement || document.body);
            scrollingElement.scrollTop += 200           
        }, 200);

        """
    )
    prev_height = None
    while True:
        curr_height = await page.evaluate('(window.innerHeight + window.scrollY)')
        if not prev_height:
            prev_height = curr_height
            time.sleep(pausetime)

            print('here1')
        elif prev_height == curr_height:
            await page.evaluate('clearInterval(intervalID)')
            print('here2')

            break
        else:
            prev_height = curr_height
            time.sleep(pausetime)
            print('here3')
            if page.locator('#ember3416'):
                print('find recommendation')
                # break
            elif page.locator('.site-footer__content'):
                print('find footer')
                # break
    return True

def html2Article(html_file):
    #首先去除可能导致误差的script和css，之后再去标签
    tempResult = re.sub('<script([\s\S]*?)</script>','',html_file)
    tempResult = re.sub('<style([\s\S]*?)</style>','',tempResult)
    tempResult = re.sub('(?is)<.*?>','',tempResult)
    tempResult = tempResult.replace(' ','')
    tempResultArray = tempResult.split('\n')
    #print tempResult

    data = []
    string_data = []
    result_data = []
    summ = 0
    count = 0

    #计算长度非零行的行数与总长度
    for oneLine in tempResultArray:
        if(len(oneLine)>0):
            data.append(len(oneLine))
            string_data.append(oneLine)
            summ += len(oneLine)
            count += 1
    #print 'averange is:'+ str(summ/count)
    for oneLine in string_data:
        #if len(oneLine) >= summ/count+180:
        if len(oneLine) >= 180:
            print(oneLine)
            result_data.append(oneLine)

    #画图部分
    #data = np.array(data)
    #x = np.arange(len(data))
    #pl.bar(x, data, alpha = .9, color = 'g')
    #pl.show()

    return result_data

def getindieposttext(html):


    ddd = html.split('<body>')[-1].split('</body>')[0]    
    # print(ddd)
    # ddd = jionlp.remove_html_tag(ddd)
    #  title


    # soup = BeautifulSoup(html)
    # header.post-page__header
    # h1.post-page__title

    # posttext=soup.find('div',{'class':'post-page__content'}).text
    
    # post text
    #comment

    ddd=''.join(ddd)
async def create_pdf_video(url, pdfpath,mobile=True):
    print('==========',url)
    if not 'http://' in url: 
        if not 'https://' in url:
            url='https://'+url
    print('==============',url)
    async with async_playwright() as p:
        start = time.process_time()
        PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
        headless=True
        print('',platform.system())
        if 'Windows' in platform.system():
            headless=True

        browserLaunchOptionDict = {
        "headless": headless,
        # "proxy": {
        #         "server": PROXY_SOCKS5,
        # }
        } 
        browser = await p.chromium.launch(**browserLaunchOptionDict)        
        record_video_dir=pdfpath.split(os.sep)[0]
        viewport=''
        if mobile:
            context = await browser.new_context(record_video_dir=record_video_dir,
            # is_mobile=True,

            record_video_size={"width": 428, "height": 926},
            screen={"width": 428, "height": 926},
            viewport={"width": 428, "height": 926}
            )
        else:
            context = await browser.new_context(record_video_dir=record_video_dir,

            record_video_size={"width": 1920, "height": 1080},
            screen={"width": 1920, "height": 1080},

            viewport={"width": 1920, "height": 1080})
        print('setting')
        page = await context.new_page()
        res =await page.goto(url
        )
        # ,timeout=0)
        # , wait_until="networkidle")
        # time.sleep(10)
        if not res is None:
            # print(await res.text())
            # text=html2Article(await res.text())
            # print(text)
            # html=await res.text()

                # header.post-page__header
    # h1.post-page__title

    # posttext=soup.find('div',{'class':'post-page__content'}).text
    
            header=await page.locator('.post-page__header').text_content()
            title=header.split('by')[0]
            author=header.split('by')[-1]
            posttext=await page.locator('.post-page__content').inner_text()

            with open(pdfpath.replace('.pdf','.txt'),'w',encoding='utf8')as f:
                f.write(header)

                f.write('\n\r===================\r\n')

                f.write(posttext)
                f.write('\n\r===================\r\n')
                # f.write(h.handle(data))
                # f.write('\n\r===================\r\n')
                
        await page.screenshot(path=pdfpath.replace('.pdf','.png'))        
        await page.pdf(path=pdfpath)
        print('==========',page.viewport_size['height'])
        print('pdf ok')
        # await scroll_to_bottom_of_page1(page)


        await context.tracing.start(screenshots=True, snapshots=True)
        isend=await scroll(page,1)
        await context.tracing.stop(path = pdfpath.replace('.pdf','.zip'))        

        # if isend:
        await context.close()
        await page.close()

        await page.video.save_as(path=pdfpath.replace('.pdf','.mp4'))

        os.remove(await page.video.path())

        await browser.close()
        print(f"playwright: Took {time.process_time()-start} seconds")

async def create_video(url, path):
    async with async_playwright() as p:
        start = time.process_time()
        browser = await p.chromium.launch()
        record_video_dir=path.split(os.sep)[0]
        filename=path.split(os.sep)[-1]
        context = await browser.new_context(record_video_dir=record_video_dir)

        page = await context.new_page()
        await page.goto(url)
        await page.video(path=filename)
        await browser.close()
        print(f"playwright: Took {time.process_time()-start} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL to convert", type=str)
    parser.add_argument("-p", "--pdf", help="Path to PDF output", type=str)
    # parser.add_argument("-v", "--video", help="Path to video output", type=str)

    args = parser.parse_args()
    print('start job')
    asyncio.run(create_pdf_video(args.url, args.pdf,True))
    # asyncio.run(create_video(args.url, args.video))
