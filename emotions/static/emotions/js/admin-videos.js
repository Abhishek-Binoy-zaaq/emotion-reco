async function loadCategories() {
    try {
        const response = await fetch('/api/categories/');
        const data = await response.json();
        const categories = data.results || data;

        const select = document.getElementById('category');
        select.innerHTML = '<option value="">No Category</option>'; // Clear existing options

        const seenIds = new Set();

        categories.forEach(cat => {
            if (!seenIds.has(cat.id)) {
                seenIds.add(cat.id);
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadVideos() {
    try {
        const response = await fetch('/api/videos/');
        const data = await response.json();

        // Handle both paginated and non-paginated responses
        const videos = data.results || data;

        const container = document.getElementById('videosList');

        if (!videos || videos.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No videos uploaded yet. Click "Upload Video" to add one.</p>';
            return;
        }

        container.innerHTML = videos.map(video => `
            <div class="video-card">
                <video class="video-thumbnail" src="${video.video_file}" controls></video>
                <div class="video-info">
                    <div class="video-title">${escapeHtml(video.title)}</div>
                    ${video.category_name ? `<p style="color: #667eea; font-size: 0.85em; margin: 5px 0;">📁 ${escapeHtml(video.category_name)}</p>` : ''}
                    <p style="color: #666; margin: 10px 0; font-size: 0.9em;">${escapeHtml(video.description || 'No description')}</p>
                    <div class="video-stats">
                        📊 ${video.total_sessions || 0} sessions | 
                        🎯 ${video.average_engagement || 0}% engagement
                    </div>
                    <div class="video-actions">
                        <button class="btn btn-primary" onclick='editVideo(${JSON.stringify({ id: video.id, title: video.title, description: video.description, category: video.category })})'>✏️ Edit</button>
                        <button class="btn btn-danger" onclick='deleteVideo(${video.id}, ${JSON.stringify(video.title)})'>🗑️ Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading videos:', error);
        document.getElementById('videosList').innerHTML = '<p style="text-align: center; color: #dc3545; padding: 40px;">Error loading videos. Please refresh the page.</p>';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
    document.getElementById('uploadForm').reset();
    document.getElementById('modalTitle').textContent = 'Upload New Video';
    document.getElementById('videoFileGroup').style.display = 'block';
    document.getElementById('uploadForm').dataset.mode = 'create';
    delete document.getElementById('uploadForm').dataset.videoId;
    loadCategories();
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
}

function editVideo(video) {
    loadCategories().then(() => {
        document.getElementById('uploadModal').style.display = 'block';
        document.getElementById('modalTitle').textContent = 'Edit Video';
        document.getElementById('title').value = video.title;
        document.getElementById('description').value = video.description || '';
        document.getElementById('category').value = video.category || '';
        document.getElementById('videoFileGroup').style.display = 'none';
        document.getElementById('uploadForm').dataset.mode = 'edit';
        document.getElementById('uploadForm').dataset.videoId = video.id;
    });
}

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mode = e.target.dataset.mode;
    const videoId = e.target.dataset.videoId;

    if (mode === 'edit') {
        // Edit existing video
        const categoryValue = document.getElementById('category').value;
        const data = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            category: categoryValue || null
        };

        try {
            const response = await fetch(`/api/videos/${videoId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                closeUploadModal();
                loadVideos();
                alert('Video updated successfully!');
            } else {
                alert('Error updating video');
            }
        } catch (error) {
            alert('Error updating video: ' + error.message);
        }
    } else {
        // Create new video
        const formData = new FormData();
        formData.append('title', document.getElementById('title').value);
        formData.append('description', document.getElementById('description').value);
        const categoryValue = document.getElementById('category').value;
        if (categoryValue) {
            formData.append('category', categoryValue);
        }
        formData.append('is_active', 'true');
        formData.append('video_file', document.getElementById('videoFile').files[0]);

        const videoEl = document.createElement('video');
        videoEl.src = URL.createObjectURL(document.getElementById('videoFile').files[0]);
        videoEl.onloadedmetadata = async () => {
            formData.append('duration', Math.floor(videoEl.duration));

            try {
                const response = await fetch('/api/videos/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                if (response.ok) {
                    closeUploadModal();
                    loadVideos();
                    alert('Video uploaded successfully!');
                } else {
                    alert('Error uploading video');
                }
            } catch (error) {
                alert('Error uploading video: ' + error.message);
            }
        };
    }
});

async function deleteVideo(id, title) {
    if (!confirm(`Are you sure you want to delete "${title}"?\n\nThis will also delete all associated sessions and captures.`)) return;

    try {
        const response = await fetch(`/api/videos/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            alert('Video deleted successfully!');
            loadVideos();
        } else {
            alert('Error deleting video');
        }
    } catch (error) {
        alert('Error deleting video: ' + error.message);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

loadVideos();


// Category Management
function showCategoriesModal() {
    document.getElementById('categoriesModal').style.display = 'block';
    loadCategoriesList();
}

function closeCategoriesModal() {
    document.getElementById('categoriesModal').style.display = 'none';
}

async function loadCategoriesList() {
    try {
        const response = await fetch('/api/categories/');
        const data = await response.json();
        const categories = data.results || data;

        const container = document.getElementById('categoriesList');

        if (!categories || categories.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No categories yet</p>';
            return;
        }

        container.innerHTML = categories.map(cat => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #f8f9fa; margin-bottom: 10px; border-radius: 6px;">
                <div>
                    <strong>${escapeHtml(cat.name)}</strong>
                    <span style="color: #666; margin-left: 10px;">(${cat.video_count} videos)</span>
                </div>
                <button class="btn btn-danger" style="padding: 8px 16px;" onclick="deleteCategory(${cat.id}, '${escapeHtml(cat.name)}')">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

document.getElementById('categoryForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('categoryName').value;

    try {
        const response = await fetch('/api/categories/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            document.getElementById('categoryName').value = '';
            loadCategoriesList();
            alert('Category added successfully!');
        } else {
            const error = await response.json();
            alert('Error: ' + JSON.stringify(error));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function deleteCategory(id, name) {
    if (!confirm(`Delete category "${name}"?\n\nVideos in this category will not be deleted, just uncategorized.`)) return;

    try {
        const response = await fetch(`/api/categories/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            loadCategoriesList();
            alert('Category deleted successfully!');
        } else {
            alert('Error deleting category');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
