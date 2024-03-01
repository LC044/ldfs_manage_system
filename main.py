# app.py
import os
from flask import Flask, render_template, request, redirect, url_for
from pyecharts import options as opts
from pyecharts.charts import Line
import pandas as pd
import numpy as np
app = Flask(__name__)

# 设置上传文件的保存路径
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查文件是否存在于请求中
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    # 如果用户未选择文件，浏览器会发送一个空的文件
    if file.filename == '':
        return redirect(request.url)

    # 检查文件类型
    if file and allowed_file(file.filename):
        # 保存上传的文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # 读取文件数据
        data = pd.read_csv(file_path, header=None, names=['value'])

        # 使用pyecharts画折线图

        print(len(list(data.index)),list(data.index))
        x_data = np.array(list(data.index))

        x_data = list(x_data)
        print(len(x_data),x_data)
        # print(data['value'].tolist())
        x=['{:.1f}'.format(i / 60) for i in x_data]
        print(x)
        print(type(x),type(x[0]))
        line_chart0 = (
            Line()
            .add_xaxis(list(data.index))
            .add_yaxis('数据', data['value'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="折线图")
            )
        )
        line_chart = (
            Line(init_opts=opts.InitOpts())
            .add_xaxis(xaxis_data=x)
            .add_yaxis(
                series_name="数据",
                y_axis=data['value'].tolist(),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值", value=int(10)),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="数据", subtitle=None),
                # datazoom_opts=opts.DataZoomOpts(),
                toolbox_opts=opts.ToolboxOpts(),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=False
                )
            )
        )
        # 渲染图表并保存为HTML文件
        chart_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.html')
        chart_html = line_chart.render(chart_filename)
        url = url_for('static', filename='uploads/chart.html')
        return render_template('result.html', chart_path=url)

    else:
        return "不支持的文件类型，请上传txt文件。"


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0',port=8081,debug=True)
