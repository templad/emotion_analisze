from flask import Flask, request, jsonify, render_template, redirect
import os
import shutil
from paqu import main_paqu as crawl_main
from analyse import analyse_chinese_comments, analyse_japanese_comments, ai_analysis
from pyecharts.charts import Pie, Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType

app = Flask(__name__)

# 确保评论目录存在
os.makedirs('comment', exist_ok=True)

# 评论文件路径
COMMENTS_FILE = 'comment/comments.txt'
POSITIVE_FILE = 'comment/positive.txt'
NEUTRAL_FILE = 'comment/neutral.txt'
NEGATIVE_FILE = 'comment/negative.txt'

@app.route('/')
def index():
    return redirect('/app.html')

@app.route('/home')
def home():
    return redirect('/app.html')

# 统一的API入口点
@app.route('/api_handler', methods=['GET', 'POST'])
def api_handler():
    action = request.args.get('action')
    
    # 爬取评论
    if action == 'crawl' and request.method == 'POST':
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': '无效的URL'})
        
        try:
            # 调用爬虫函数
            crawl_main(url)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # 上传文件
    elif action == 'upload' and request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        try:
            # 保存上传的文件到评论文件
            file.save(COMMENTS_FILE)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # 获取评论
    elif action == 'get_comments' and request.method == 'GET':
        try:
            if not os.path.exists(COMMENTS_FILE):
                return jsonify({'success': False, 'error': '评论文件不存在'})
            
            with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                comments = [line.strip() for line in f.readlines()]
            
            return jsonify({'success': True, 'comments': comments})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # 中文分析
    elif action == 'analyze_chinese' and request.method == 'POST':
        try:
            analyse_chinese_comments(COMMENTS_FILE)
            # 生成可视化页面
            generate_visualization_html()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # 日语分析
    elif action == 'analyze_japanese' and request.method == 'POST':
        try:
            analyse_japanese_comments(COMMENTS_FILE)
            # 生成可视化页面
            generate_visualization_html()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # AI分析
    elif action == 'analyze_ai' and request.method == 'POST':
        try:
            status = ai_analysis(COMMENTS_FILE)
            if status == 0:
                # 生成可视化页面
                generate_visualization_html()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'status': status})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # 获取分析结果
    elif action == 'get_analysis_results' and request.method == 'GET':
        try:
            # 读取分析结果
            positive = read_file_if_exists(POSITIVE_FILE)
            neutral = read_file_if_exists(NEUTRAL_FILE)
            negative = read_file_if_exists(NEGATIVE_FILE)
            
            return jsonify({
                'success': True,
                'positive': positive,
                'neutral': neutral,
                'negative': negative
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    else:
        return jsonify({'success': False, 'error': '无效的操作'})

# 保留原来的API路由进行兼容
@app.route('/api/crawl', methods=['POST'])
def crawl():
    return api_handler()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    return api_handler()

@app.route('/api/get_comments', methods=['GET'])
def get_comments():
    return api_handler()

@app.route('/api/analyze_chinese', methods=['POST'])
def analyze_chinese():
    return api_handler()

@app.route('/api/analyze_japanese', methods=['POST'])
def analyze_japanese():
    return api_handler()

@app.route('/api/analyze_ai', methods=['POST'])
def analyze_ai():
    return api_handler()

@app.route('/api/get_analysis_results', methods=['GET'])
def get_analysis_results():
    return api_handler()

def read_file_if_exists(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    return []

# 生成静态化的可视化页面
def generate_visualization_html():
    # 读取分析结果
    positive = read_file_if_exists(POSITIVE_FILE)
    neutral = read_file_if_exists(NEUTRAL_FILE)
    negative = read_file_if_exists(NEGATIVE_FILE)
    
    positive_count = len(positive)
    neutral_count = len(neutral)
    negative_count = len(negative)
    
    # 生成饼图
    pie = (
        Pie(init_opts=opts.InitOpts(width="800px", height="400px", theme=ThemeType.LIGHT))
        .add(
            "",
            [
                ["积极评论", positive_count],
                ["中性评论", neutral_count],
                ["消极评论", negative_count],
            ],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评论情感分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_right="2%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
    )
    
    # 生成条形图
    bar = (
        Bar(init_opts=opts.InitOpts(width="800px", height="400px", theme=ThemeType.LIGHT))
        .add_xaxis(["积极评论", "中性评论", "消极评论"])
        .add_yaxis("评论数量", [positive_count, neutral_count, negative_count])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评论数量对比"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(name="数量"),
        )
    )
    
    # 生成并保存静态HTML文件
    content = render_template(
        "visualization.html", 
        pie_chart=pie.render_embed(),
        bar_chart=bar.render_embed(),
    )
    with open('visualization.html', 'w', encoding='utf-8') as f:
        f.write(content)

# 数据可视化路由
@app.route('/visualization')
def visualization():
    try:
        # 生成可视化页面
        generate_visualization_html()
        return render_template(
            "visualization.html", 
            pie_chart=pie.render_embed(),
            bar_chart=bar.render_embed(),
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 确保评论目录存在
    os.makedirs('comment', exist_ok=True)
    # 确保评论文件存在
    if not os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            pass
    
    # 将HTML文件复制到templates目录
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    shutil.copy('app.html', os.path.join(templates_dir, 'app.html'))
    shutil.copy('index.html', os.path.join(templates_dir, 'index.html'))
    
    # 复制为静态文件
    shutil.copy('app.html', 'app.html')
    
    # 生成初始静态页面
    try:
        generate_visualization_html()
    except:
        pass
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 