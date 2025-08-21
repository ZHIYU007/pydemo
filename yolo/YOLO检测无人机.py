# from ultralytics import YOLO

# import cv2

# def detect_drones(input_image_path, output_image_path):
#     # 加载预训练的YOLOv8模型
#     model = YOLO('yolov8n.pt')  # 这里使用的是YOLOv8的纳米版本，你可以根据需要选择其他版本，如yolov8s.pt, yolov8m.pt等

#     # 进行目标检测
#     results = model(input_image_path)

#     # 获取检测结果中的第一张图像
#     result = results[0]

#     # 读取原始图像
#     img = cv2.imread(input_image_path)

#     # 遍历检测到的每个目标
#     for box in result.boxes:
#         # 获取目标的边界框坐标
#         bbox = box.xyxy[0].cpu().numpy().astype(int)
#         x1, y1, x2, y2 = bbox

#         # 在图像上绘制边界框
#         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # 获取目标的类别名称和置信度
#         class_id = int(box.cls[0])
#         confidence = float(box.conf[0])
#         class_name = result.names[class_id]

#         # 在边界框上方绘制类别名称和置信度
#         text = f'{class_name}: {confidence:.2f}'
#         cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#     # 保存带有检测结果的图像
#     cv2.imwrite(output_image_path, img)

#     print(f"检测结果已保存到 {output_image_path}")

# if __name__ == "__main__":
#     # 设置输入图片的路径
#     input_image_path = r"D:\BaiduSyncdisk\文件快传\学习\python\data\20250101T015458.jpg"
#     # 设置输出图片的路径
#     output_image_path = r"D:\BaiduSyncdisk\文件快传\学习\python\data\new.jpg"

#     # 调用检测函数
#     detect_drones(input_image_path, output_image_path)

import cv2
from ultralytics import YOLO

def detect_drones_in_video(input_video_path, output_video_path):
    # 加载预训练的 YOLOv8 模型
    model = YOLO('yolov8n.pt')

    # 打开输入视频文件
    cap = cv2.VideoCapture(input_video_path)

    # 获取视频的帧率、宽度和高度
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

.





    while cap.isOpened():
        # 读取一帧视频
        ret, frame = cap.read()

        if ret:
            # 对当前帧进行目标检测
            results = model(frame)

            # 获取检测结果中的第一张图像
            result = results[0]

            # 遍历检测到的每个目标
            for box in result.boxes:
                # 获取目标的边界框坐标
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = bbox

                # 在图像上绘制边界框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 获取目标的类别名称和置信度
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]

                # 在边界框上方绘制类别名称和置信度
                text = f'{class_name}: {confidence:.2f}'
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 将处理后的帧写入输出视频
            out.write(frame)

            # 显示处理后的帧
            cv2.imshow('YOLOv8 Drone Detection', frame)

            # 按 'q' 键退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"检测结果已保存到 {output_video_path}")

if __name__ == "__main__":
    # 设置输入视频的路径
    input_video_path = r"D:\BaiduSyncdisk\文件快传\学习\python\data\1 215.mp4"
    # 设置输出视频的路径
    output_video_path = r"D:\BaiduSyncdisk\文件快传\学习\python\data\new.mp4"

    # 调用检测函数
    detect_drones_in_video(input_video_path, output_video_path)