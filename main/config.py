"""
CENTRALIZED CONFIGURATION FOR FACE RECOGNITION SYSTEM
======================================================
Tất cả cấu hình quan trọng được quản lý tại file này để tránh mismatch

⚠️ QUAN TRỌNG: Khi sửa đổi cấu hình, CHỈ SỬA Ở ĐÂY
Các module khác sẽ import từ file này thay vì hardcode
"""

import os

# ============================================================================
# BASE PATHS
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# FACE DATA DIRECTORIES
# ============================================================================
# Thư mục chứa ảnh đã xử lý của sinh viên (sau khi capture & align)
FACE_DATA_DIR = os.path.join(BASE_DIR, 'main', 'Dataset', 'FaceData', 'processed')

# Đường dẫn tương đối từ project root (dùng cho views)
FACE_DATA_DIR_RELATIVE = 'main/Dataset/FaceData/processed'

# Template path cho từng sinh viên
def get_student_face_dir(student_id):
    """Lấy đường dẫn thư mục ảnh của 1 sinh viên"""
    return os.path.join(FACE_DATA_DIR, str(student_id))

# ============================================================================
# MODEL PATHS
# ============================================================================
# FaceNet pretrained model (embedding extraction)
FACENET_MODEL_PATH = os.path.join(BASE_DIR, 'main', 'Models', '20180402-114759.pb')
FACENET_MODEL_PATH_RELATIVE = 'main/Models/20180402-114759.pb'

# Classifier model (SVM đã train)
CLASSIFIER_MODEL_PATH = os.path.join(BASE_DIR, 'main', 'Models', 'facemodel.pkl')
CLASSIFIER_MODEL_PATH_RELATIVE = 'main/Models/facemodel.pkl'

# Anti-spoof models directory
ANTI_SPOOF_MODEL_DIR = os.path.join(BASE_DIR, 'main', 'resources', 'anti_spoof_models')

# MTCNN weights directory
MTCNN_WEIGHTS_DIR = os.path.join(BASE_DIR, 'main', 'align')

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================
# Kích thước ảnh đầu vào (FaceNet yêu cầu 160x160)
INPUT_IMAGE_SIZE = 160

# Số lượng ảnh tối thiểu cho mỗi sinh viên (để train)
MIN_IMAGES_PER_STUDENT = 20

# Batch size khi extract embeddings
BATCH_SIZE = 90

# Số ảnh khuyến nghị khi capture
RECOMMENDED_IMAGES_PER_STUDENT = 300

# Confidence threshold cho SVM prediction
CONFIDENCE_THRESHOLD = 0.80  # 80%

# ============================================================================
# FACE DETECTION CONFIGURATION
# ============================================================================
# MTCNN parameters
MTCNN_MIN_FACE_SIZE = 20
MTCNN_THRESHOLDS = [0.6, 0.7, 0.7]  # P-Net, R-Net, O-Net
MTCNN_SCALE_FACTOR = 0.709
MTCNN_MARGIN = 44  # Pixels to add around detected face

# Anti-spoof best model (fastest & most accurate)
BEST_ANTI_SPOOF_MODEL = "2.7_80x80_MiniFASNetV2.pth"

# ============================================================================
# ATTENDANCE CONFIGURATION
# ============================================================================
# Số phút được phép đến muộn (sau thời gian này = Muộn)
LATE_THRESHOLD_MINUTES = 15

# Tỷ lệ vắng tối đa cho phép (20% tổng buổi)
MAX_ABSENCE_RATIO = 0.20

# Điểm chuyên cần tối đa
MAX_ATTENDANCE_SCORE = 3.0

# ============================================================================
# VIDEO CAPTURE CONFIGURATION
# ============================================================================
# Camera device ID (0 = default webcam, 1 = external camera)
CAMERA_DEVICE_ID = 0

# FPS for video capture
VIDEO_FPS = 30

# Buffer size (smaller = less lag)
VIDEO_BUFFER_SIZE = 1

# Frame skip for optimization (process every N frames)
FRAME_SKIP = 2  # Process every 2nd frame

# Recognition progress threshold (15 frames = ~1.5 seconds)
RECOGNITION_FRAME_THRESHOLD = 15

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_paths_exist():
    """
    Kiểm tra tất cả các đường dẫn quan trọng có tồn tại không
    
    Returns:
        dict: {'status': bool, 'missing': list, 'errors': list}
    """
    errors = []
    missing = []
    
    # Check directories
    if not os.path.exists(FACE_DATA_DIR):
        missing.append(f"Face data directory: {FACE_DATA_DIR}")
    
    if not os.path.exists(os.path.dirname(CLASSIFIER_MODEL_PATH)):
        missing.append(f"Models directory: {os.path.dirname(CLASSIFIER_MODEL_PATH)}")
    
    # Check critical files
    if not os.path.exists(FACENET_MODEL_PATH):
        errors.append(f"FaceNet model not found: {FACENET_MODEL_PATH}")
    
    if not os.path.exists(CLASSIFIER_MODEL_PATH):
        errors.append(f"Classifier model not trained yet: {CLASSIFIER_MODEL_PATH}")
    
    if not os.path.exists(ANTI_SPOOF_MODEL_DIR):
        errors.append(f"Anti-spoof models not found: {ANTI_SPOOF_MODEL_DIR}")
    
    return {
        'status': len(errors) == 0 and len(missing) == 0,
        'missing': missing,
        'errors': errors
    }


def get_system_info():
    """
    Lấy thông tin cấu hình hiện tại của hệ thống
    
    Returns:
        dict: Thông tin cấu hình
    """
    from main.models import StudentInfo
    import pickle
    
    info = {
        'face_data_dir': FACE_DATA_DIR,
        'facenet_model': FACENET_MODEL_PATH,
        'classifier_model': CLASSIFIER_MODEL_PATH,
        'students_in_db': StudentInfo.objects.count(),
        'students_with_images': 0,
        'students_in_model': 0,
        'model_trained': os.path.exists(CLASSIFIER_MODEL_PATH),
    }
    
    # Count students with image folders
    if os.path.exists(FACE_DATA_DIR):
        info['students_with_images'] = len([
            d for d in os.listdir(FACE_DATA_DIR) 
            if os.path.isdir(os.path.join(FACE_DATA_DIR, d))
        ])
    
    # Get students in trained model
    if os.path.exists(CLASSIFIER_MODEL_PATH):
        try:
            with open(CLASSIFIER_MODEL_PATH, 'rb') as f:
                model, class_names = pickle.load(f)
                info['students_in_model'] = len(class_names)
                info['class_names'] = class_names
        except Exception as e:
            info['model_error'] = str(e)
    
    return info


def validate_system_consistency():
    """
    Kiểm tra tính nhất quán giữa DB, file system và model
    
    Returns:
        dict: {'is_consistent': bool, 'warnings': list, 'recommendations': list}
    """
    from main.models import StudentInfo
    import pickle
    
    warnings = []
    recommendations = []
    
    system_info = get_system_info()
    
    # Check 1: Model đã được train chưa
    if not system_info['model_trained']:
        warnings.append("Model chưa được train! Không thể điểm danh bằng khuôn mặt.")
        recommendations.append("Chạy: python train_face_model.py")
        return {'is_consistent': False, 'warnings': warnings, 'recommendations': recommendations}
    
    # Check 2: Số lượng sinh viên
    db_count = system_info['students_in_db']
    model_count = system_info['students_in_model']
    folder_count = system_info['students_with_images']
    
    if db_count != model_count:
        warnings.append(
            f"Mismatch: DB có {db_count} sinh viên, model có {model_count} sinh viên"
        )
        recommendations.append("Train lại model để đồng bộ")
    
    if db_count != folder_count:
        warnings.append(
            f"Mismatch: DB có {db_count} sinh viên, filesystem có {folder_count} thư mục ảnh"
        )
        recommendations.append("Capture ảnh cho sinh viên thiếu")
    
    # Check 3: Sinh viên có trong DB nhưng không có ảnh
    students_without_images = []
    for student in StudentInfo.objects.all():
        student_dir = get_student_face_dir(student.id_student)
        if not os.path.exists(student_dir):
            students_without_images.append(student.id_student)
    
    if students_without_images:
        warnings.append(
            f"{len(students_without_images)} sinh viên chưa có ảnh: {', '.join(students_without_images[:5])}"
        )
        recommendations.append("Capture ảnh cho các sinh viên này")
    
    is_consistent = len(warnings) == 0
    
    return {
        'is_consistent': is_consistent,
        'warnings': warnings,
        'recommendations': recommendations
    }


# ============================================================================
# EXPORT ALL
# ============================================================================
__all__ = [
    # Paths
    'FACE_DATA_DIR',
    'FACE_DATA_DIR_RELATIVE',
    'FACENET_MODEL_PATH',
    'FACENET_MODEL_PATH_RELATIVE',
    'CLASSIFIER_MODEL_PATH',
    'CLASSIFIER_MODEL_PATH_RELATIVE',
    'ANTI_SPOOF_MODEL_DIR',
    'MTCNN_WEIGHTS_DIR',
    
    # Training config
    'INPUT_IMAGE_SIZE',
    'MIN_IMAGES_PER_STUDENT',
    'BATCH_SIZE',
    'RECOMMENDED_IMAGES_PER_STUDENT',
    'CONFIDENCE_THRESHOLD',
    
    # Detection config
    'MTCNN_MIN_FACE_SIZE',
    'MTCNN_THRESHOLDS',
    'MTCNN_SCALE_FACTOR',
    'MTCNN_MARGIN',
    'BEST_ANTI_SPOOF_MODEL',
    
    # Attendance config
    'LATE_THRESHOLD_MINUTES',
    'MAX_ABSENCE_RATIO',
    'MAX_ATTENDANCE_SCORE',
    
    # Video config
    'CAMERA_DEVICE_ID',
    'VIDEO_FPS',
    'VIDEO_BUFFER_SIZE',
    'FRAME_SKIP',
    'RECOGNITION_FRAME_THRESHOLD',
    
    # Helper functions
    'get_student_face_dir',
    'check_paths_exist',
    'get_system_info',
    'validate_system_consistency',
]
