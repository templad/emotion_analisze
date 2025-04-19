from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time


def extract_comments(dp, url):# 提取评论函数
    dp.listen.start('top=0')
    dp.get(url)
    resp = dp.listen.wait()
    json_data = resp.response.body
    
    # 提取content字段并保存到文件
    with open('comment\\comments.txt', 'a', encoding='utf-8') as f:
        for item in json_data['data']['datas']:
            content = item['content']
            f.write(content + '\n')  # 写入文件，每条内容占一行
    
#主爬取函数
def main_paqu(url):
    # 从主页面获取url列表
    dp = ChromiumPage()
    # 设置请求头，使用实际的浏览器请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Host': 'groupweb.chaoxing.com',
        'Referer': 'https://groupweb.chaoxing.com/course/topic/topicList?courseid=228053910&clazzid=62217808&cpi=281181307&ut=s&t=1744627438254&stuenc=fb2a74e82bdaaf86ae4d2d723b78e434&bbsid=d9cc17534a33be75dee2c0d924ee9dd6&learnSilverStartTime=&learnSilverEndTime=&enc=fb2a74e82bdaaf86ae4d2d723b78e434',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest'
    }

    # 设置请求头
    dp._headers = headers

    # 设置cookies
    cookies = {
        'uname': '2022217386',
        'fid': '434',
        'xxtenc': '9880ecfe18ea9f334275903d2491d93c',
        '_uid': '251471596',
        '_d': '1744593048334',
        'UID': '251471596',
        'vc3': 'SSKSIHGFXEsHMigIkJHJ7DTC92buW3e7p2phrsE6c5jO82rnYfw4BpgsKoKgDeZcJwNUXLk7fBvXw38OgGSNtmHAh8FIrSaKU2Z9D5CUqvoY0cMfLweyZp2PCq32aWbg3jYIseM4zYfK5UgGSG1BgdB58uYU7cqxrWPTwKFNRKc%3D1ebd2a6fa4031636a8cc47f59909230a',
        'uf': 'd9387224d3a6095b4be4216df09500b8bb09a5d0cf7ec6a6663f50fca28813c350b7da84b85549a625e446b13375f739c49d67c0c30ca5043ad701c8b4cc548c0234d89f51c3dccffb6a0ec401f7c9b8713028f1ec42bf71b1188854805578ccce71fc6e59483dd337d05cd3d27339e9925618849ca7be3427b679a51a54d69be9fdc681bdf07734',
        'cx_p_token': 'a317e9135d47feb9e5f83b80a6ee5bd3',
        'p_auth_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyNTE0NzE1OTYiLCJsb2dpblRpbWUiOjE3NDQ1OTMwNDgzMzUsImV4cCI6MTc0NTE5Nzg0OH0.SoWLHYKdDGG04PKRMWeCNCQL0iNDqEp-5fd5Okb6Yow',
        'DSSTASH_LOG': 'C_38-UN_482-US_251471596-T_1744593048335',
        'thirdRegist': '0',
        'fanyamoocs': 'ACB5AE956E84AF416454D22CDA617420',
        '_industry': '5',
        '251544643cpi': '281181307',
        '251544643ut': 's',
        '251544643t': '1744593056786',
        '251544643enc': 'f7be5e167ce0a68bb6e65da6221985f2',
        'route': 'b0c381e8d0ae5368be4dce472f741d17',
        '_dd251471596': '1744627438227',
        '228053910cpi': '281181307',
        '228053910ut': 's',
        '228053910t': '1744627438254',
        '228053910enc': 'fb2a74e82bdaaf86ae4d2d723b78e434',
        'JSESSIONID': 'E81E88C844376E64914E4D67D621801C.GroupTopic_WEB'
    }

    # 设置cookies
    dp._cookies = cookies

    # 主页面URL
    main_url = url

    # 请求网站URL
    timestamp = int(time.time() * 1000)
    request_url = f'https://groupweb.chaoxing.com/course/topic/d9cc17534a33be75dee2c0d924ee9dd6/getTopicList?folder_uuid=&page=1&pageSize=20&kw=&tags=classId0000001,classId62217808,courseId228053910&courseId=228053910&isSetTop=&selectedStartTime=&selectedEndTime=&selectedType=0&learnSilverStartTime=&learnSilverEndTime=&lastAuxValue=&_={timestamp}'

    # 先访问主页面
    dp.get(main_url)
    dp.listen.start('groupweb.chaoxing.com/course/topic/d9cc17534a33be75d')
    dp.get(request_url)
    resp = dp.listen.wait()
    json_data = resp.response.body

    # 提取shareUrl
    urls = []
    for item in json_data['datas']:
        if 'shareUrl' in item:
            urls.append(item['shareUrl'])
            print(f"找到URL: {item['shareUrl']}")

    # 清空comments.txt文件
    with open('comment\\comments.txt', 'w', encoding='utf-8') as f:
        f.write('')

    # 根据url列表提取分别提取每个页面的评论
    for url in urls:
        extract_comments(dp, url)

    print("所有评论已提取完成")
    dp.close()

#main('https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/stu?courseid=228053910&clazzid=62217808&cpi=281181307&enc=fb2a74e82bdaaf86ae4d2d723b78e434&t=1744627438254&pageHeader=2&v=0&hideHead=0')