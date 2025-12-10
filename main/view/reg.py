import pickle
from datetime import datetime
import os
import cv2
import imutils
import numpy as np
import tensorflow as tf
from imutils.video import VideoStream
from main.src.anti_spoof_predict import AntiSpoofPredict
from main.src.generate_patches import CropImage
from main.src.utility import parse_model_name
from main import facenet
from main.align import detect_face
from main.models import Classroom, Attendance, StudentInfo, StudentClassDetails, ClassSession
import warnings
import re
from difflib import SequenceMatcher

# ...

# Trước khi gọi hàm có cảnh báo
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

model_test = AntiSpoofPredict(0)
image_cropper = CropImage()
model_dir = "main/resources/anti_spoof_models"


def normalize_student_id(student_id):
    """
    Chuẩn hóa mã sinh viên: loại bỏ khoảng trắng, ký tự đặc biệt
    """
    if not student_id:
        return ""
    # Loại bỏ khoảng trắng, lowercase, chỉ giữ lại chữ số
    return re.sub(r'[^a-zA-Z0-9]', '', str(student_id)).strip().upper()


def fuzzy_match_student(recognized_name, threshold=0.85):
    """
    Tìm sinh viên khớp với tên được nhận diện (fuzzy matching)
    
    Args:
        recognized_name: Tên từ model (có thể là MSSV hoặc tên)
        threshold: Ngưỡng độ tương đồng (0-1)
    
    Returns:
        StudentInfo object hoặc None
    """
    normalized_input = normalize_student_id(recognized_name)
    
    # Thử tìm chính xác trước
    try:
        return StudentInfo.objects.get(id_student=normalized_input)
    except StudentInfo.DoesNotExist:
        pass
    
    # Fuzzy matching với tất cả sinh viên
    all_students = StudentInfo.objects.all()
    best_match = None
    best_score = 0
    
    for student in all_students:
        # So sánh với MSSV
        score_id = SequenceMatcher(None, normalized_input, 
                                   normalize_student_id(student.id_student)).ratio()
        
        # So sánh với tên (chuẩn hóa)
        normalized_name = normalize_student_id(student.student_name)
        score_name = SequenceMatcher(None, normalized_input, normalized_name).ratio()
        
        # Lấy score cao hơn
        score = max(score_id, score_name)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = student
    
    if best_match:
        print(f"⚠️ Fuzzy match: '{recognized_name}' → {best_match.id_student} ({best_match.student_name}) - Score: {best_score:.2f}")
    
    return best_match


def enhance_image(image):
    """
    Cải thiện chất lượng ảnh để nhận diện tốt hơn
    - Tăng độ sáng nếu quá tối
    - Tăng độ tương phản
    - Giảm noise
    """
    # Chuyển sang LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Áp dụng CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge lại và chuyển về BGR
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Giảm noise
    enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
    
    return enhanced


# Function to draw a progress bar


def insert_attendance(session_id, student_id):
    """
    Cập nhật điểm danh khi nhận diện khuôn mặt thành công
    LOGIC MỚI: Không tạo bản ghi cho tất cả SV, chỉ cập nhật người được nhận diện
    
    Args:
        session_id: ID của buổi học (ClassSession)
        student_id: Mã sinh viên được nhận diện (từ model)
    
    Returns:
        str: Thông báo kết quả
    """
    print(f"\n➡️ insert_attendance called: session_id={session_id}, student_id='{student_id}'")
    
    try:
        session = ClassSession.objects.get(pk=session_id)
    except ClassSession.DoesNotExist:
        return f"ERROR: Không tìm thấy buổi học với ID {session_id}"
    
    # Kiểm tra buổi học có đang mở không
    if session.status != 'OPEN':
        return f"ERROR: Buổi học đã đóng hoặc chưa mở. Không thể điểm danh!"
    
    classroom = session.id_classroom
    current_time = datetime.now()
    begin_time = classroom.begin_time
    
    # Tính toán trạng thái (Muộn nếu check-in > 15 phút sau giờ bắt đầu)
    time_difference = (datetime.combine(datetime.now(), current_time.time())
                       - datetime.combine(datetime.now(), begin_time))
    
    if time_difference.total_seconds() > 900:  # 15 phút = 900 giây
        attendance_status = 3  # Muộn
        status_text = "Muộn"
    else:
        attendance_status = 2  # Có mặt đúng giờ
        status_text = "Có mặt"
    
    # ✅ CẢI TIỆN: Chuẩn hóa và fuzzy match student ID
    normalized_id = normalize_student_id(student_id)
    print(f"🔍 Normalized: '{student_id}' → '{normalized_id}'")
    
    # Thử tìm chính xác trước
    student_info = None
    try:
        student_info = StudentInfo.objects.get(id_student=normalized_id)
        print(f"✅ Exact match: {student_info.id_student} - {student_info.student_name}")
    except StudentInfo.DoesNotExist:
        print(f"⚠️ Exact match failed, trying fuzzy match...")
        # Thử fuzzy matching
        student_info = fuzzy_match_student(student_id, threshold=0.80)
        
        if not student_info:
            # Liệt kê tất cả sinh viên để debug
            all_students = StudentInfo.objects.all()[:10]
            student_list = ", ".join([f"{s.id_student}" for s in all_students])
            return f"ERROR: Không tìm thấy sinh viên '{student_id}' (normalized: '{normalized_id}').\nCó trong DB: {student_list}..."
    
    # Kiểm tra sinh viên có đăng ký lớp này không
    if not StudentClassDetails.objects.filter(
        id_classroom=classroom,
        id_student=student_info
    ).exists():
        return f"ERROR: Sinh viên {student_info.student_name} ({student_info.id_student}) không có trong lớp {classroom.name}"
    
    # Cập nhật hoặc tạo bản ghi điểm danh
    try:
        attendance = Attendance.objects.get(
            id_session=session,
            id_student=student_info
        )
        
        # Kiểm tra đã điểm danh chưa (status != 1 Vắng)
        if attendance.attendance_status != 1:
            return f"INFO: {student_info.student_name} ({student_info.id_student}) đã điểm danh lúc {attendance.check_in_time.strftime('%H:%M:%S')}"
        
        # Cập nhật từ Vắng → Có mặt/Muộn
        attendance.attendance_status = attendance_status
        attendance.check_in_time = current_time
        attendance.check_in_method = 'FACE'
        attendance.save()
        
        print(f"✓ Điểm danh thành công: {student_info.student_name} ({student_info.id_student}) - {status_text}")
        return f"SUCCESS: {student_info.student_name} ({student_info.id_student}) - {status_text}"
        
    except Attendance.DoesNotExist:
        # Trường hợp buổi học chưa khởi tạo bản ghi Vắng
        # Tạo mới bản ghi điểm danh
        attendance = Attendance.objects.create(
            id_session=session,
            id_classroom=classroom,
            id_student=student_info,
            check_in_time=current_time,
            attendance_status=attendance_status,
            check_in_method='FACE'
        )
        print(f"✓ Điểm danh thành công (tạo mới): {student_info.student_name} ({student_info.id_student}) - {status_text}")
        return f"SUCCESS: {student_info.student_name} ({student_info.id_student}) - {status_text}"
        
    except Exception as e:
        print(f"✗ Lỗi khi điểm danh: {e}")
        return f"ERROR: {str(e)}"


def draw_progress_bar(frame, progress, x, y, w, h, confidence=0):
    """Vẽ thanh tiến trình và hiển thị thông tin debug"""
    bar_width = 200
    bar_height = 25
    bar_x = x
    bar_y = y - 35
    
    # Vẽ nền thanh
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
    
    # Vẽ tiến độ
    filled_width = int(bar_width * min(progress, 1.0))
    color = (0, 255, 0) if progress < 1.0 else (0, 255, 255)  # Xanh lá -> Vàng khi đủ
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), color, -1)
    
    # Hiển thị %
    percent_text = f"{int(progress * 100)}%"
    cv2.putText(frame, percent_text, (bar_x + bar_width + 10, bar_y + 18), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Hiển thị confidence nếu có
    if confidence > 0:
        conf_text = f"Conf: {confidence:.2f}"
        cv2.putText(frame, conf_text, (bar_x, bar_y - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)


def main(session_id):
    """
    Hàm chính xử lý nhận diện khuôn mặt và điểm danh (Optimized Version)
    
    Args:
        session_id: ID của buổi học (ClassSession) thay vì id_classroom
    """

    INPUT_IMAGE_SIZE = 160
    CLASSIFIER_PATH = 'main/Models/facemodel.pkl'
    FACENET_MODEL_PATH = 'main/Models/20180402-114759.pb'

    # Kiểm tra model tồn tại
    if not os.path.exists(CLASSIFIER_PATH):
        print("=" * 70)
        print("❌ LỖI: Model chưa được train!")
        print("=" * 70)
        print("File không tồn tại:", CLASSIFIER_PATH)
        print("\n📋 HƯỚNG DẪN KHẮC PHỤC:")
        print("1. Thêm ảnh sinh viên vào: main/Dataset/FaceData/MSSV/")
        print("   - Mỗi sinh viên cần 20-30 ảnh")
        print("2. Chạy lệnh: python train_face_model.py")
        print("3. Sau khi train xong, quay lại điểm danh")
        print("\n📖 Chi tiết: Đọc file SETUP_FACE_RECOGNITION.md")
        print("=" * 70)
        
        # Tạo frame thông báo lỗi
        while True:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "MODEL CHUA DUOC TRAIN!", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "Vui long chay: python train_face_model.py", (20, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(frame, "Chi tiet: SETUP_FACE_RECOGNITION.md", (50, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    with open(CLASSIFIER_PATH, 'rb') as file:
        model, class_names = pickle.load(file)
    print("Custom Classifier, Successfully loaded")

    # Load feature extraction model outside the session
    facenet.load_model(FACENET_MODEL_PATH)
    graph = tf.compat.v1.get_default_graph()
    images_placeholder = graph.get_tensor_by_name("input:0")
    embeddings = graph.get_tensor_by_name("embeddings:0")
    phase_train_placeholder = graph.get_tensor_by_name("phase_train:0")

    # ✅ OPTIMIZATION: Tăng FPS và giảm buffer delay
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)  # Tăng FPS
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Giảm buffer lag

    global justscanned
    global pause_cnt
    justscanned = False
    pause_cnt = 0
    current_face_name = ""
    current_face_progress = 0

    # Initialize an empty list to store recognized names
    recognized_names = []
    sess = tf.compat.v1.Session(graph=graph)
    
    # ✅ OPTIMIZATION: Frame skipping counter
    frame_count = 0
    skip_frames = 2  # Chỉ xử lý mỗi frame thứ 2 (tăng 50% tốc độ)

    while cap.isOpened():
        isSuccess, frame = cap.read()
        if isSuccess:
            frame_count += 1
            
            # ✅ OPTIMIZATION: Skip frames để tăng tốc độ xử lý
            # Chỉ xử lý face detection mỗi 2 frames
            if frame_count % skip_frames != 0:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                continue
            
            image_bbox = model_test.get_bbox(frame)
            if image_bbox is not None:
                x, y, w, h = (image_bbox[0]), (image_bbox[1] - 50), (image_bbox[0] + image_bbox[2]), (
                        image_bbox[1] + image_bbox[3])
                height, width, _ = frame.shape

                # ✅ OPTIMIZATION: Chỉ dùng 1 anti-spoof model thay vì loop qua 3 models
                # Tăng tốc độ xử lý gấp 3 lần phần anti-spoof
                prediction = np.zeros((1, 3))
                
                # Chỉ sử dụng model 2.7_80x80_MiniFASNetV2.pth (model tốt nhất)
                best_model = "2.7_80x80_MiniFASNetV2.pth"
                if os.path.exists(os.path.join(model_dir, best_model)):
                    h_input, w_input, model_type, scale = parse_model_name(best_model)
                    param = {
                        "org_img": frame,
                        "bbox": image_bbox,
                        "scale": scale,
                        "out_w": w_input,
                        "out_h": h_input,
                        "crop": True,
                    }
                    if scale is None:
                        param["crop"] = False
                    img = image_cropper.crop(**param)
                    prediction = model_test.predict(img, os.path.join(model_dir, best_model)) * 3  # Nhân 3 để bù trừ việc chỉ dùng 1 model
                else:
                    # Fallback: nếu không tìm thấy model tốt nhất, dùng model đầu tiên
                    model_name = os.listdir(model_dir)[0]
                    h_input, w_input, model_type, scale = parse_model_name(model_name)
                    param = {
                        "org_img": frame,
                        "bbox": image_bbox,
                        "scale": scale,
                        "out_w": w_input,
                        "out_h": h_input,
                        "crop": True,
                    }
                    if scale is None:
                        param["crop"] = False
                    img = image_cropper.crop(**param)
                    prediction = model_test.predict(img, os.path.join(model_dir, model_name)) * 3

                label = np.argmax(prediction)
                value = prediction[0][label] / 2
                if label == 1:
                    cropped = frame[y:h, x:w, :]
                    # Check if the cropped image is not empty
                    if cropped is not None and cropped.size > 0:
                        # ✅ CẢI TIỆN: Tăng chất lượng ảnh trước khi nhận diện
                        enhanced_crop = enhance_image(cropped)
                        
                        scaled = cv2.resize(enhanced_crop, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),
                                            interpolation=cv2.INTER_CUBIC)
                        scaled = facenet.prewhiten(scaled)
                        scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
                        feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
                        emb_array = sess.run(embeddings, feed_dict=feed_dict)
                        
                        # ✅ XỬ LÝ TRƯỜNG HỢP CHỈ CÓ 1 SINH VIÊN
                        if model is None:
                            # Single-class mode: luôn trả về sinh viên duy nhất với confidence cao
                            best_name = class_names[0]
                            best_class_probabilities = np.array([0.95])  # High confidence
                            predictions = np.array([[0.95]])
                            top_3_names = [best_name]
                            top_3_probs = [0.95]
                        else:
                            # Multi-class mode: dùng SVM classifier
                            predictions = model.predict_proba(emb_array)
                            best_class_indices = np.argmax(predictions, axis=1)
                            best_class_probabilities = predictions[
                                np.arange(len(best_class_indices)), best_class_indices]
                            best_name = class_names[best_class_indices[0]]
                            
                            # Lấy top 3 predictions để hiển thị
                            top_3_idx = np.argsort(predictions[0])[-3:][::-1]
                            top_3_names = [class_names[i] for i in top_3_idx]
                            top_3_probs = [predictions[0][i] for i in top_3_idx]

                        # ✅ CẢI TIỆN: Giảm threshold từ 0.85 → 0.50 để dễ nhận diện hơn
                        # Và kiểm tra khoảng cách giữa top 1 và top 2 (margin)
                        confidence_threshold = 0.50
                        margin_threshold = 0.15  # Top 1 phải hơn top 2 ít nhất 15%
                        
                        is_confident = (best_class_probabilities[0] > confidence_threshold and 
                                      (len(top_3_probs) < 2 or (top_3_probs[0] - top_3_probs[1]) > margin_threshold))
                        
                        if is_confident:
                            if best_name not in recognized_names:
                                if current_face_name != best_name:
                                    current_face_name = best_name
                                    current_face_progress = 0
                                    justscanned = False
                                elif not justscanned:
                                    current_face_progress += skip_frames
                                    # ✅ GIẢM xuống 10 frames (nhanh hơn nữa)
                                    progress = current_face_progress / 10
                                    draw_progress_bar(frame, progress, x, y, w, h, best_class_probabilities[0])

                                # Vẽ khung xanh lá
                                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 3)
                                
                                # Hiển thị tên và confidence
                                text_x = x
                                text_y = h + 25
                                
                                # Tên sinh viên và MSSV (chữ lớn, màu vàng)
                                display_text = f"{best_name}"
                                # Thử lấy thông tin đầy đủ từ DB
                                try:
                                    student_info = fuzzy_match_student(best_name, threshold=0.70)
                                    if student_info:
                                        display_text = f"{student_info.id_student} - {student_info.student_name}"
                                except:
                                    pass
                                
                                cv2.putText(frame, display_text, (text_x, text_y), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                                
                                # Confidence score
                                conf_text = f"{best_class_probabilities[0]:.1%}"
                                cv2.putText(frame, conf_text, (text_x, text_y + 25), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                
                                # Hiển thị top 3 predictions (debug info)
                                debug_y = text_y + 50
                                for i, (name, prob) in enumerate(zip(top_3_names[:3], top_3_probs[:3])):
                                    debug_text = f"{i+1}. {name}: {prob:.1%}"
                                    color = (0, 255, 255) if i == 0 else (200, 200, 200)
                                    cv2.putText(frame, debug_text, (text_x, debug_y + i*20), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

                                # ✅ Giảm xuống 10 frames
                                if current_face_progress >= 10:
                                    justscanned = True
                                    recognized_names.append(best_name)
                                    insert = insert_attendance(session_id, best_name)
                                    print(insert)
                                    if current_face_name != "SUCCESS":
                                        print("Success: Face Recognized as", insert)
                            else:
                                # Đã điểm danh rồi
                                message = f"{best_name} - DA DIEM DANH"
                                cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 3)
                                cv2.putText(frame, message, (x, y - 10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        else:
                            # Không đủ confidence - hiển thị thông tin debug
                            current_face_name = "LOW_CONFIDENCE"
                            current_face_progress = 0
                            justscanned = False
                            
                            # Vẽ khung vàng (cảnh báo)
                            cv2.rectangle(frame, (x, y), (w, h), (0, 165, 255), 3)
                            
                            # Hiển thị top prediction và confidence
                            text_x = x
                            text_y = h + 25
                            
                            warning_text = "KHONG CHAC CHAN"
                            cv2.putText(frame, warning_text, (text_x, text_y), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                            
                            # Hiển thị top 3 để debug
                            debug_y = text_y + 25
                            for i, (name, prob) in enumerate(zip(top_3_names[:3], top_3_probs[:3])):
                                debug_text = f"{i+1}. {name}: {prob:.1%}"
                                cv2.putText(frame, debug_text, (text_x, debug_y + i*20), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                            
                            # Hướng dẫn
                            guide_text = "Dung gan camera, nhin thang"
                            cv2.putText(frame, guide_text, (text_x, debug_y + 70), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                else:
                    result_text = "Gia mao !!!".format(value)
                    color = (0, 255, 255)
                    cv2.rectangle(
                        frame,
                        (image_bbox[0], image_bbox[1] - 50),
                        (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]),
                        # Increase the height by 20 pixels
                        color, 2)

                    cv2.putText(
                        frame,
                        result_text,
                        (image_bbox[0], image_bbox[1]),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, color, thickness=1,
                        lineType=2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    sess.close()
    cap.release()
    cv2.destroyAllWindows()
