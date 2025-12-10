"""
Script tự động train face recognition model từ ảnh sinh viên
Sử dụng: python train_face_model.py
"""

import os
import pickle
import cv2
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from main import facenet
from main.align import detect_face
import warnings

warnings.filterwarnings('ignore')

# Configuration
INPUT_IMAGE_SIZE = 160
FACENET_MODEL_PATH = 'main/Models/20180402-114759.pb'
OUTPUT_CLASSIFIER_PATH = 'main/Models/facemodel.pkl'
FACE_DATA_DIR = 'main/Dataset/FaceData'
MIN_FACE_SIZE = 20
CONFIDENCE_THRESHOLD = 0.95

def load_and_align_data(image_paths, image_size=160, margin=44, gpu_memory_fraction=1.0):
    """
    Load và align faces từ images
    """
    minsize = 20
    threshold = [0.6, 0.7, 0.7]
    factor = 0.709
    
    print('Creating networks and loading parameters')
    with tf.Graph().as_default():
        gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, None)
    
    nrof_samples = len(image_paths)
    img_list = []
    
    for i, image_path in enumerate(image_paths):
        img = cv2.imread(image_path)
        if img is None:
            print(f'⚠️ Cannot read: {image_path}')
            continue
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect face
        bounding_boxes, _ = detect_face.detect_face(img_rgb, minsize, pnet, rnet, onet, threshold, factor)
        
        if len(bounding_boxes) < 1:
            print(f'⚠️ No face detected: {image_path}')
            continue
            
        det = np.squeeze(bounding_boxes[0, 0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0] - margin / 2, 0)
        bb[1] = np.maximum(det[1] - margin / 2, 0)
        bb[2] = np.minimum(det[2] + margin / 2, img.shape[1])
        bb[3] = np.minimum(det[3] + margin / 2, img.shape[0])
        
        cropped = img_rgb[bb[1]:bb[3], bb[0]:bb[2], :]
        aligned = cv2.resize(cropped, (image_size, image_size), interpolation=cv2.INTER_CUBIC)
        
        prewhitened = facenet.prewhiten(aligned)
        img_list.append(prewhitened)
        
        if (i + 1) % 10 == 0:
            print(f'Processed {i + 1}/{nrof_samples} images')
    
    return np.stack(img_list) if img_list else np.array([])

def train_classifier(data_dir, model_path, classifier_filename):
    """
    Train SVM classifier từ face embeddings
    """
    print(f'\n🚀 Bắt đầu training face recognition model...')
    print(f'📁 Data directory: {data_dir}')
    
    # Load facenet model
    print('\n📦 Loading FaceNet model...')
    facenet.load_model(model_path)
    
    # Get image paths và labels
    dataset = []
    image_paths = []
    labels = []
    
    if not os.path.exists(data_dir):
        print(f'❌ Thư mục {data_dir} không tồn tại!')
        print(f'💡 Vui lòng tạo thư mục và thêm ảnh sinh viên theo cấu trúc:')
        print(f'   {data_dir}/MSSV_1/anh1.jpg')
        print(f'   {data_dir}/MSSV_1/anh2.jpg')
        print(f'   {data_dir}/MSSV_2/anh1.jpg')
        return False
    
    class_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    if not class_dirs:
        print(f'❌ Không tìm thấy thư mục nào trong {data_dir}!')
        return False
    
    print(f'\n📊 Tìm thấy {len(class_dirs)} sinh viên:')
    
    for class_name in class_dirs:
        class_dir = os.path.join(data_dir, class_name)
        images = [f for f in os.listdir(class_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f'   - {class_name}: {len(images)} ảnh')
        
        for img in images:
            img_path = os.path.join(class_dir, img)
            image_paths.append(img_path)
            labels.append(class_name)
    
    if not image_paths:
        print('❌ Không tìm thấy ảnh nào!')
        return False
    
    print(f'\n🖼️ Tổng cộng: {len(image_paths)} ảnh')
    
    # Load and align faces
    print('\n🔍 Detecting và aligning faces...')
    images = load_and_align_data(image_paths, INPUT_IMAGE_SIZE)
    
    if len(images) == 0:
        print('❌ Không detect được khuôn mặt nào!')
        return False
    
    print(f'✅ Detected {len(images)} faces')
    
    # Get embeddings
    print('\n🧠 Extracting face embeddings...')
    graph = tf.compat.v1.get_default_graph()
    images_placeholder = graph.get_tensor_by_name("input:0")
    embeddings_tensor = graph.get_tensor_by_name("embeddings:0")
    phase_train_placeholder = graph.get_tensor_by_name("phase_train:0")
    
    sess = tf.compat.v1.Session(graph=graph)
    
    batch_size = 90
    nrof_images = len(images)
    nrof_batches = int(np.ceil(1.0 * nrof_images / batch_size))
    emb_array = np.zeros((nrof_images, 512))
    
    for i in range(nrof_batches):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, nrof_images)
        paths_batch = images[start_index:end_index]
        feed_dict = {images_placeholder: paths_batch, phase_train_placeholder: False}
        emb_array[start_index:end_index, :] = sess.run(embeddings_tensor, feed_dict=feed_dict)
        
        if (i + 1) % 10 == 0:
            print(f'Processed {i + 1}/{nrof_batches} batches')
    
    # Train SVM classifier
    print('\n🎓 Training SVM classifier...')
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels[:len(images)])
    
    # Check if only 1 class (1 student)
    unique_classes = len(set(labels_encoded))
    
    if unique_classes == 1:
        print(f'\n⚠️ CHÚ Ý: Chỉ có 1 sinh viên trong dữ liệu!')
        print(f'   → Tạo "dummy classifier" cho single-class recognition')
        print(f'   → Model sẽ luôn nhận diện là: {labels[0]}')
        
        # Tạo dummy classifier - không train SVM
        model = None  # Sẽ xử lý riêng trong recognition code
    else:
        # Sử dụng probability=True để có predict_proba
        print(f'   Số lượng sinh viên: {unique_classes}')
        model = SVC(kernel='linear', probability=True, C=1.0)
        model.fit(emb_array, labels_encoded)
    
    class_names = label_encoder.classes_
    
    # Save model
    print(f'\n💾 Saving classifier to {classifier_filename}...')
    with open(classifier_filename, 'wb') as outfile:
        pickle.dump((model, class_names), outfile)
    
    print(f'\n✅ Training hoàn tất!')
    print(f'📊 Thống kê:')
    print(f'   - Số sinh viên: {len(class_names)}')
    print(f'   - Tổng số ảnh: {len(images)}')
    print(f'   - Trung bình: {len(images)/len(class_names):.1f} ảnh/sinh viên')
    print(f'\n👥 Danh sách sinh viên đã train:')
    for i, name in enumerate(class_names, 1):
        count = labels[:len(images)].count(name)
        print(f'   {i}. {name} ({count} ảnh)')
    
    return True

def create_sample_structure():
    """
    Tạo cấu trúc thư mục mẫu
    """
    print('\n📁 Tạo cấu trúc thư mục mẫu...')
    
    sample_students = ['2011003929', '2011010091', '2011010708', '2011020456', '2011030789']
    
    for student in sample_students:
        student_dir = os.path.join(FACE_DATA_DIR, student)
        os.makedirs(student_dir, exist_ok=True)
    
    print(f'✅ Đã tạo thư mục tại: {FACE_DATA_DIR}')
    print(f'\n💡 Hướng dẫn thêm ảnh:')
    print(f'   1. Vào thư mục {FACE_DATA_DIR}/MSSV')
    print(f'   2. Thêm 5-10 ảnh khuôn mặt của sinh viên')
    print(f'   3. Ảnh nên:')
    print(f'      - Rõ nét, ánh sáng tốt')
    print(f'      - Nhìn thẳng vào camera')
    print(f'      - Đa dạng góc độ (trái, phải, hơi nghiêng)')
    print(f'      - Kích thước tối thiểu 200x200 pixels')
    print(f'   4. Chạy lại: python train_face_model.py')

if __name__ == '__main__':
    print('=' * 60)
    print('🎓 FACE RECOGNITION MODEL TRAINER')
    print('=' * 60)
    
    # Kiểm tra facenet model
    if not os.path.exists(FACENET_MODEL_PATH):
        print(f'❌ Không tìm thấy FaceNet model: {FACENET_MODEL_PATH}')
        print(f'💡 Vui lòng download model từ:')
        print(f'   https://drive.google.com/file/d/1EXPBSXwTaqrSC0OhUdXNmKSh9qJUQ55-/view')
        exit(1)
    
    # Kiểm tra face data directory
    if not os.path.exists(FACE_DATA_DIR):
        print(f'⚠️ Thư mục {FACE_DATA_DIR} chưa tồn tại!')
        choice = input('Bạn có muốn tạo cấu trúc thư mục mẫu? (y/n): ')
        if choice.lower() == 'y':
            create_sample_structure()
        exit(0)
    
    # Train classifier
    success = train_classifier(FACE_DATA_DIR, FACENET_MODEL_PATH, OUTPUT_CLASSIFIER_PATH)
    
    if success:
        print('\n🎉 SUCCESS! Model đã sẵn sàng sử dụng!')
        print(f'📍 File model: {OUTPUT_CLASSIFIER_PATH}')
        print(f'\n🚀 Bước tiếp theo:')
        print(f'   1. Khởi động server: python manage.py runserver')
        print(f'   2. Vào trang điểm danh bằng khuôn mặt')
        print(f'   3. Test nhận diện với sinh viên đã train')
    else:
        print('\n❌ Training thất bại! Vui lòng kiểm tra lại.')
        print(f'\n💡 Gợi ý:')
        print(f'   - Kiểm tra ảnh có rõ nét không')
        print(f'   - Mỗi sinh viên cần ít nhất 3-5 ảnh')
        print(f'   - Ảnh phải có khuôn mặt rõ ràng')
