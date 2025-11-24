# Video File Storage Information

## 📁 Storage Location

**Generated video files are stored at:**
```
/app/backend/generated_videos/
```

**This directory contains:**
- `test_sample.mp4` - Template video (4.2 KB)
- `{project_id}.mp4` - Individual video files for each project

## 🔗 Download URL Format

**Database stores:** `/videos/{project_id}/download`

**Frontend constructs:** `https://catty-news.preview.emergentagent.com/api/videos/{project_id}/download`

**Backend serves from:** `/app/backend/generated_videos/{project_id}.mp4`

## ⚠️ Preview Environment Persistence

### **IMPORTANT: Files are NOT permanently persistent**

The preview environment is **ephemeral**:

1. **During Active Session:** ✅
   - Files remain accessible
   - Downloads work
   - Links are valid

2. **After Container Restart:** ❌
   - `/app/backend/generated_videos/` is cleared
   - All generated videos are lost
   - Database still has records, but files don't exist

3. **After Redeployment:** ❌
   - Complete fresh start
   - All files deleted
   - Database may be reset

## 💾 For Production Deployment

To make files persistent in production, you need:

### **Option 1: External Storage (Recommended)**
- Store videos in AWS S3, Google Cloud Storage, or similar
- Update videoUrl to point to S3 URL
- Files persist forever
- No server storage needed

### **Option 2: Persistent Volume**
- Configure Kubernetes Persistent Volume
- Mount to `/app/backend/generated_videos/`
- Files survive restarts
- Limited by disk space

### **Option 3: Database Storage (Not Recommended)**
- Store video files as binary in MongoDB
- Works for small files
- Not scalable for many/large videos

## 🎯 Current System Behavior

**In Preview Environment:**

```
User Creates Video → File Saved → User Downloads → ✅ Works
                                                 
Container Restarts → Files Deleted → User Tries Download → ❌ 404 Error
```

**Recommended Workflow for Preview:**

1. Generate script
2. Create video project
3. **Download immediately** to your computer
4. Upload to YouTube Studio manually
5. Don't rely on files being available later

## 📊 File Sizes

Current test videos: **4.2 KB each** (3-second purple screen)

Real videos with:
- AI voiceover: ~500 KB - 2 MB
- Images/text overlays: ~2-5 MB
- Stock footage/animations: ~10-50 MB per 60-90 second video

## 🚀 Next Steps for Permanent Storage

If you want persistent storage, add to your implementation:

```python
import boto3

def upload_to_s3(video_path, project_id):
    s3 = boto3.client('s3')
    bucket = 'your-bucket-name'
    key = f'videos/{project_id}.mp4'
    
    s3.upload_file(video_path, bucket, key)
    
    # Return permanent URL
    return f'https://{bucket}.s3.amazonaws.com/{key}'
```

Then update video generation to upload and store S3 URL instead of local path.
