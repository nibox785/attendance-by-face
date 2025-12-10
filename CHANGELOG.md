# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-12-11

### 🚀 Major Changes

#### Face Recognition Improvements (v2.0)
- **Reduced confidence threshold** from 0.90 → 0.50 for better recognition rate
- **Added margin check** (0.15) to prevent false positives
- **Image enhancement** with CLAHE and noise reduction
- **Faster recognition** - Reduced from 30 → 10 frames (~1.5s per student)
- **Better debug info** - Shows top 3 predictions with confidence scores
- **Single-class support** - Can train model with just 1 student

#### Session-based Attendance System
- Complete refactoring to session-based approach
- Each session has unique ID and status (OPEN/CLOSED)
- No duplicate attendance records
- Session reopen capability for editing
- Audit trail tracking (who modified, when, method)

#### Student ID Matching
- Added `normalize_student_id()` for consistent formatting
- Fuzzy matching with SequenceMatcher (80-85% similarity)
- Better handling of MSSV mismatches

### ✨ New Features
- Admin panel with full CRUD operations
- Face image capture via admin interface
- Anti-spoofing detection (MiniFASNetV2)
- Progress bar during face recognition
- Color-coded feedback (green=recognized, red=unknown, yellow=processing)

### 🐛 Bug Fixes
- Fixed missing `@admin_required` decorator causing 500 errors
- Fixed model existence validation
- Added extensive logging for debugging

### 📁 Project Restructuring
- Created `docs/` folder for all documentation
- Created `scripts/` folder for utility scripts
- Updated README.md with clear project structure
- Improved .gitignore

### 📚 Documentation
- Created 8 comprehensive documentation files
- Added step-by-step training guide
- Added system analysis and comparison docs
- Added important warnings about MSSV matching

## [1.0.0] - 2024-09-02

### Initial Release
- Basic face recognition with FaceNet + SVM
- Manual attendance marking
- Student and lecturer portals
- Admin dashboard
- MySQL database integration
