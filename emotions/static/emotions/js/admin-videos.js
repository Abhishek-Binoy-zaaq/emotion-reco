async function loadCategories() {
    try {
        const response = await fetch('/api/categories/');
        const data = await response.json();
        const categories = data.results || data;

        const select = document.getElementById('category');
        select.innerHTML = '<option value="">No Category</option>';

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
        const videos = data.results || data;

        const container = document.getElementById('videosList');

        if (!videos || videos.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12 bg-white rounded-2xl border border-dashed border-gray-300">
                    <div class="text-4xl mb-4">📹</div>
                    <p class="text-slate-500 mb-4">No videos uploaded yet</p>
                    <button onclick="showUploadModal()" class="btn-primary inline-flex">Upload First Video</button>
                </div>
            `;
            return;
        }

        container.innerHTML = videos.map(video => `
            <div class="bg-white rounded-2xl overflow-hidden shadow-sm border border-slate-100 hover:shadow-lg transition-all group flex flex-col">
                <div class="relative bg-black aspect-video">
                    <video class="w-full h-full object-cover" src="${video.video_file}" controls></video>
                </div>
                
                <div class="p-5 flex flex-col flex-1">
                    <div class="flex justify-between items-start mb-2">
                        <div class="font-bold text-slate-800 text-lg line-clamp-1">${escapeHtml(video.title)}</div>
                    </div>
                    
                    ${video.category_name ?
                `<div class="text-sm text-brand-600 font-medium mb-3 flex items-center gap-1">
                            <span>📁</span> ${escapeHtml(video.category_name)}
                        </div>` : ''}
                    
                    <p class="text-slate-500 text-sm mb-4 line-clamp-2 flex-1">${escapeHtml(video.description || 'No description')}</p>
                    
                    <div class="grid grid-cols-2 gap-2 text-xs text-slate-500 bg-slate-50 p-2 rounded-lg mb-4">
                        <div class="text-center">
                            <div class="font-bold text-slate-700">${video.total_sessions || 0}</div>
                            <div>Sessions</div>
                        </div>
                        <div class="text-center border-l border-slate-200">
                            <div class="font-bold text-slate-700">${Math.round(video.average_engagement || 0)}%</div>
                            <div>Engagement</div>
                        </div>
                    </div>

                    <div class="flex gap-2 pt-2 border-t border-gray-100">
                        <button class="flex-1 py-2 px-3 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-brand-600 border border-transparent hover:border-brand-200 transition-all" 
                            onclick='editVideo(${JSON.stringify({ id: video.id, title: video.title, description: video.description, category: video.category })})'>
                            ✏️ Edit
                        </button>
                        <button class="flex-1 py-2 px-3 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 border border-transparent hover:border-red-100 transition-all" 
                            onclick='deleteVideo(${video.id}, ${JSON.stringify(video.title)})'>
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading videos:', error);
        document.getElementById('videosList').innerHTML = '<p class="col-span-full text-center text-red-500 py-8">Error loading videos</p>';
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Modal Helpers
function toggleModal(id, show) {
    const modal = document.getElementById(id);
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
}

function showUploadModal() {
    toggleModal('uploadModal', true);
    document.getElementById('uploadForm').reset();
    document.getElementById('modalTitle').textContent = 'Upload New Video';
    document.getElementById('videoFileGroup').classList.remove('hidden');
    document.getElementById('uploadForm').dataset.mode = 'create';
    delete document.getElementById('uploadForm').dataset.videoId;
    loadCategories();
}

function closeUploadModal() {
    toggleModal('uploadModal', false);
}

function editVideo(video) {
    loadCategories().then(() => {
        toggleModal('uploadModal', true);
        document.getElementById('modalTitle').textContent = 'Edit Video';
        document.getElementById('title').value = video.title;
        document.getElementById('description').value = video.description || '';
        document.getElementById('category').value = video.category || '';
        document.getElementById('videoFileGroup').classList.add('hidden');
        document.getElementById('uploadForm').dataset.mode = 'edit';
        document.getElementById('uploadForm').dataset.videoId = video.id;
    });
}

// Form Handlers
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mode = e.target.dataset.mode;
    const videoId = e.target.dataset.videoId;
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.textContent;

    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;

    try {
        if (mode === 'edit') {
            const data = {
                title: document.getElementById('title').value,
                description: document.getElementById('description').value,
                category: document.getElementById('category').value || null
            };

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
            } else throw new Error('Update failed');

        } else {
            const formData = new FormData();
            formData.append('title', document.getElementById('title').value);
            formData.append('description', document.getElementById('description').value);
            const categoryValue = document.getElementById('category').value;
            if (categoryValue) formData.append('category', categoryValue);
            formData.append('is_active', 'true');

            const fileInput = document.getElementById('videoFile');
            if (fileInput.files[0]) {
                formData.append('video_file', fileInput.files[0]);

                // Get duration
                const videoEl = document.createElement('video');
                videoEl.src = URL.createObjectURL(fileInput.files[0]);

                await new Promise(resolve => {
                    videoEl.onloadedmetadata = () => {
                        formData.append('duration', Math.floor(videoEl.duration));
                        resolve();
                    };
                });
            }

            const response = await fetch('/api/videos/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData
            });

            if (response.ok) {
                closeUploadModal();
                loadVideos();
            } else throw new Error('Upload failed');
        }
    } catch (error) {
        alert('Operation failed: ' + error.message);
    } finally {
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
});

async function deleteVideo(id, title) {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
        const response = await fetch(`/api/videos/${id}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });

        if (response.ok) loadVideos();
        else alert('Error deleting video');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Category Management
function showCategoriesModal() {
    toggleModal('categoriesModal', true);
    loadCategoriesList();
}

function closeCategoriesModal() {
    toggleModal('categoriesModal', false);
}

async function loadCategoriesList() {
    try {
        const response = await fetch('/api/categories/');
        const data = await response.json();
        const categories = data.results || data;
        const container = document.getElementById('categoriesList');

        if (!categories || categories.length === 0) {
            container.innerHTML = '<p class="text-center text-slate-400 py-4 text-sm">No categories yet</p>';
            return;
        }

        container.innerHTML = categories.map(cat => `
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg group hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 transition-all">
                <div class="flex items-center gap-2">
                    <span class="font-medium text-slate-700">${escapeHtml(cat.name)}</span>
                    <span class="text-xs text-slate-400 bg-white px-2 py-0.5 rounded-full border border-gray-100">${cat.video_count} videos</span>
                </div>
                <button class="text-red-400 hover:text-red-600 p-1 rounded-md hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100" 
                    onclick="deleteCategory(${cat.id}, '${escapeHtml(cat.name)}')">
                    &times;
                </button>
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
        } else alert('Failed to create category');
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function deleteCategory(id, name) {
    if (!confirm(`Delete category "${name}"?`)) return;
    try {
        const response = await fetch(`/api/categories/${id}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        if (response.ok) loadCategoriesList();
    } catch (e) { alert(e.message); }
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
