import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import time    #time.time()函数可以记录程序运行到当前的时间


app = Flask(__name__)

# 配置文件
UPLOAD_FOLDER = "static/uploads"  # 上传图片或者视频的存储路径
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif","mp4"}  # 允许的文件类型
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 加载 YOLO 模型
model = YOLO("yolov8n.pt")  # 替换成你的模型路径


def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 检查是否有文件上传

        '''获取任务的时间节点'''
        get_time=time.time()

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # 检查文件名是否合法
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            # 保存上传的文件
            filename = secure_filename(file.filename)  #保证文件名安全性
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            #记录开始时间
            start_time = time.time()

            #判断文件是图片还是视频，并进行不同的检测策略
            if filename.rsplit(".", 1)[1].lower() != "mp4":

                # 对图片内容进行检测
                results = model(filepath)

                # 保存检测结果
                output_path = os.path.join(app.config["UPLOAD_FOLDER"], f"detected_{filename}")
                results[0].save(output_path)


            else:

                # 打开视频
                cap = cv2.VideoCapture(filepath)

                # 获取视频属性
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # 设置输出视频路径
                output_video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"detected_{filename}")

                # 使用更兼容的编码格式（尝试不同的编码器）
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 首选h264编码
                if fourcc == -1:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 备用mp4v编码

                out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

                # 逐帧处理

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # 使用YOLO检测当前帧
                    results = model(frame)
                    annotated_frame = results[0].plot()

                    # 写入输出视频
                    out.write(annotated_frame)

                # 释放资源
                cap.release()
                out.release()
                cv2.destroyAllWindows()

            #获取程序运行结束的时间
            end_time = time.time()

            # 返回检测后的图片路径
            return jsonify({
                "original": f"static/uploads/{filename}",
                "detected": f"static/uploads/detected_{filename}",
                "get_time":f"{get_time}",
                "detected_time":f"{round(end_time-start_time,2)}s"
            })

        return jsonify({"error": "Invalid file type"}), 400

    return render_template("index.html")




if __name__ == "__main__":
    app.run(debug=True)