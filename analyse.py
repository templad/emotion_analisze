from snownlp import SnowNLP
from asari.api import Sonar
from openai import OpenAI

#清空3类评论文件
def delete_file():
    with open('comment\\positive.txt', 'w', encoding='utf-8') as f:
        f.write('')
        f.close()
    with open('comment\\neutral.txt', 'w', encoding='utf-8') as f:
        f.write('')
        f.close()
    with open('comment\\negative.txt', 'w', encoding='utf-8') as f:
        f.write('')
        f.close()

#将3类评论写入文件
def write_file(positiveList, neutralList, negativeList):
    delete_file()
    with open('comment\\positive.txt', 'a', encoding='utf-8') as f:
        for comment in positiveList:
            f.write(comment + '\n')
        f.close()
    with open('comment\\neutral.txt', 'a', encoding='utf-8') as f:
        for comment in neutralList:
            f.write(comment + '\n')
        f.close()
    with open('comment\\negative.txt', 'a', encoding='utf-8') as f:
        for comment in negativeList:
            f.write(comment + '\n')
        f.close()

#分析中文评论的情感
def analyse_chinese_comments(file_path):
    # 消极的评论列表
    negativeList = []
    # 中性的评论列表
    neutralList = []
    # 积极的评论列表
    positiveList = []
    # 打开文本
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        # 使用 split() 方法按换行符分割文本
        commentList = text.split("\n")

    # 分析
    for comment in commentList:
        # 去除首尾空白字符，如果评论为空则跳过
        comment = comment.strip()
        if comment:
            s = SnowNLP(comment)
            # 获取情感分数
            sentiment_score = s.sentiments
            if sentiment_score < 0.4:
                # 说明是负面评论
                negativeList.append(comment)
            elif sentiment_score <= 0.6:
                # 说明是中性评论
                neutralList.append(comment)
            else:
                # 说明是积极评论
                positiveList.append(comment)

    print('积极的评论有：%d条，中性的评论有：%d条，消极的评论有：%d条'% (len(positiveList), len(neutralList), len(negativeList)))
    write_file(positiveList, neutralList, negativeList)

#分析日文评论的情感
def analyse_japanese_comments(file_path):
    sonar = Sonar()
    # 消极的评论列表
    negativeList = []
    # 中性的评论列表
    neutralList = []
    # 积极的评论列表
    positiveList = []

    # 打开文本
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        # 使用 split() 方法按换行符分割文本
        commentList = text.split("\n")
    # 分析
    for comment in commentList:
        result = sonar.ping(text=comment)
        if result['top_class'] == 'negative':
            # 负面评论
            negativeList.append(comment)
        elif result['top_class'] == 'positive':
            # 积极评论
            positiveList.append(comment)
        else:
            # 中性评论
            neutralList.append(comment)
    print('积极的评论有：%d条，中性的评论有：%d条，消极的评论有：%d条' % (len(positiveList), len(neutralList), len(negativeList)))
    write_file(positiveList, neutralList, negativeList)

#AI分析
def ai_analysis(file_path):
    client = OpenAI(api_key="sk-730b90762a6f4e0287eff8344660cebc", base_url="https://api.deepseek.com")

    # 读取评论文件
    with open(file_path, 'r', encoding='utf-8') as file:
        comments = file.readlines()

    # 将所有评论合并为一个消息，并用 | 分隔
    combined_comments = " | ".join(comment.strip() for comment in comments)

    # 发送请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "请将以下评论分类为积极、中性或消极，返回格式如下：\n积极：...（评论以 | 分隔）\n中性：...（评论以 | 分隔）\n消极：...（评论以 | 分隔）。" + combined_comments}
        ],
        stream=False,
        timeout=60  # 设置超时为60秒
    )
    #如果超时或错误，则重新发送请求,最多重试3次
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "请将以下评论分类为积极、中性或消极，返回格式如下：\n积极：...（评论以 | 分隔）\n中性：...（评论以 | 分隔）\n消极：...（评论以 | 分隔）。" + combined_comments}
                ],
                stream=False,
                timeout=60
            )
            break   
        except Exception as e:
            if i == 2:
                print("所有请求都失败了，请检查网络连接或稍后再试。")
                return 1
   
   
    # 处理分类结果
    response_content = response.choices[0].message.content

    # 分割每个分类部分
    classification_parts = response_content.split("\n")

    # 初始化分类列表
    positiveList = []
    neutralList = []
    negativeList = []

    for part in classification_parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("积极："):
            comments = part[len("积极："):].split(" | ")
            positiveList = [comment.strip() for comment in comments]
        elif part.startswith("中性："):
            comments = part[len("中性："):].split(" | ")
            neutralList = [comment.strip() for comment in comments]
        elif part.startswith("消极："):
            comments = part[len("消极："):].split(" | ")
            negativeList = [comment.strip() for comment in comments]

    print('积极的评论有：%d条，中性的评论有：%d条，消极的评论有：%d条' % (len(positiveList), len(neutralList), len(negativeList)))
    write_file(positiveList, neutralList, negativeList)
    return 0
