from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import os
from colorPic import color, color_video  # 假设 DeOldify 的 color 和 color_video 函数
import threading
import time
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 Flash 消息
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['RESULT_FOLDER'] = 'static/results/'

# 确保文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# 简单的任务状态存储
task_status = {}

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """
    根据时间戳生成唯一文件名，保留原始文件的扩展名
    """
    timestamp = int(time.time())
    extension = os.path.splitext(original_filename)[1]
    return f"{timestamp}{extension}"

def process_video_task(task_id, file_path, result_folder):
    """
    视频处理任务，运行在后台线程
    """
    try:
        result_path = color_video(file_path)
        result_filename = generate_unique_filename(os.path.basename(result_path))
        result_file_path = os.path.join(result_folder, result_filename)
        os.rename(result_path, result_file_path)
        task_status[task_id] = {"status": "completed", "result": result_filename}
    except Exception as e:
        print(f"Error processing video: {e}")
        task_status[task_id] = {"status": "failed", "error": str(e)}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            task_id = str(int(time.time()))
            filename = generate_unique_filename(file.filename)
            
            if filename.endswith('mp4'):
                file_path = os.path.join('video/source/', filename)
                os.makedirs('video/source/', exist_ok=True)
            else:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
            file.save(file_path)
            task_status[task_id] = {"status": "processing"}

            if filename.endswith('mp4'):
                threading.Thread(target=process_video_task, args=(task_id, filename, app.config['RESULT_FOLDER'])).start()
                return redirect(url_for('video_status', task_id=task_id))
            else:
                try:
                    print("start color")
                    result_path = color(file_path)
                    # result_filename = generate_unique_filename(os.path.basename(result_path))
                    # result_file_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                    # os.rename(result_path, result_file_path)
                    result_filename = generate_unique_filename(os.path.basename(result_path))
                    result_file_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                    os.rename(result_path, result_file_path)
                    return redirect(url_for('show_image', filename=result_filename))
                except Exception as e:
                    print(f"Error: {e}")
                    flash("图片处理失败，请重试！")
                    return redirect(url_for('index'))
        else:
            flash("请上传支持的图片或视频文件！")
            return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/status/<task_id>')
def video_status(task_id):
    task = task_status.get(task_id, {"status": "unknown"})
    if task["status"] == "processing":
        return render_template('processing.html', task_id=task_id)
    elif task["status"] == "completed":
        return redirect(url_for('show_video', filename=task["result"]))
    elif task["status"] == "failed":
        flash("视频处理失败，请重试！")
        return redirect(url_for('index'))
    else:
        flash("任务不存在！")
        return redirect(url_for('index'))


@app.route('/result/<filename>')
def show_image(filename):
    return render_template('result.html', filename=filename)


@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)


@app.route('/video/<filename>')
def show_video(filename):
    return render_template('video_result.html', filename=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
