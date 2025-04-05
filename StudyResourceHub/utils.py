import os
from flask import current_app, url_for

def get_download_url(file_id):
    """Generate a download URL for a file"""
    return url_for('download_file', file_id=file_id, _external=True)

def get_whatsapp_share_url(file_id, filename):
    """Generate a WhatsApp sharing URL for a file"""
    download_url = get_download_url(file_id)
    share_text = f"حمل الملف ده: {filename} - {download_url}"
    return f"https://wa.me/?text={share_text}"

def get_file_icon(file_type):
    """Return an appropriate Font Awesome icon class based on file type"""
    if file_type == 'PDF':
        return 'fa-file-pdf'
    elif file_type == 'Image':
        return 'fa-file-image'
    elif file_type == 'Video':
        return 'fa-file-video'
    else:
        return 'fa-file'

def human_readable_size(size_bytes):
    """Convert bytes to human-readable format"""
    if not size_bytes:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name)-1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"
