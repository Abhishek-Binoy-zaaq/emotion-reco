let editingUserId = null;
let allUsers = [];

async function loadUsers() {
    try {
        const response = await fetch('/api/users/');
        const data = await response.json();
        allUsers = data.results || data;

        updateStats();
        renderUsers(allUsers);
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersBody').innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-red-500">Error loading users. Please refresh.</td></tr>';
    }
}

function updateStats() {
    const total = allUsers.length;
    const active = allUsers.filter(u => u.is_active).length;
    const inactive = total - active;

    const animateValue = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    animateValue('totalUsers', total);
    animateValue('activeUsers', active);
    animateValue('inactiveUsers', inactive);
}

function renderUsers(users) {
    const tbody = document.getElementById('usersBody');

    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-12 text-center text-slate-500">
                    <div class="text-4xl mb-4">👥</div>
                    <div class="text-lg font-medium">No users found</div>
                    <p class="text-sm mt-1">Click "Create User" to add one.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = users.map(user => {
        const fullName = [user.first_name, user.last_name].filter(n => n).join(' ') || '<span class="text-gray-400 italic">Not set</span>';
        const joined = new Date(user.date_joined).toLocaleDateString();

        return `
            <tr class="hover:bg-gray-50 transition-colors group">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="h-10 w-10 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-lg mr-3">
                            ${user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <div class="font-medium text-slate-900">${escapeHtml(user.username)}</div>
                            <div class="text-xs text-slate-500">${escapeHtml(user.email || 'No email')}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-slate-500">
                    ${joined}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-slate-500 font-medium">
                    ${user.session_count || '-'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end gap-2 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                        <button class="text-brand-600 hover:text-brand-900 bg-brand-50 hover:bg-brand-100 p-2 rounded-lg transition-colors" 
                            onclick="editUser(${user.id}, '${escapeHtml(user.username)}', '${escapeHtml(user.email || '')}', '${escapeHtml(user.first_name || '')}', '${escapeHtml(user.last_name || '')}', ${user.is_active})" title="Edit">
                            ✏️
                        </button>
                        
                        ${user.is_active ?
                `<button class="text-amber-600 hover:text-amber-900 bg-amber-50 hover:bg-amber-100 p-2 rounded-lg transition-colors" 
                                onclick="toggleUserStatus(${user.id}, false, '${escapeHtml(user.username)}')" title="Disable Account">
                                🔒
                            </button>` :
                `<button class="text-green-600 hover:text-green-900 bg-green-50 hover:bg-green-100 p-2 rounded-lg transition-colors" 
                                onclick="toggleUserStatus(${user.id}, true, '${escapeHtml(user.username)}')" title="Enable Account">
                                🔓
                            </button>`
            }
                        
                        <button class="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 p-2 rounded-lg transition-colors" 
                            onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')" title="Delete">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, "\\'");
}

// Modal Logic
function toggleModal(show) {
    const modal = document.getElementById('userModal');
    if (show) {
        modal.classList.remove('hidden');
    } else {
        modal.classList.add('hidden');
        editingUserId = null;
    }
}

function showCreateModal() {
    toggleModal(true);
    document.getElementById('modalTitle').textContent = 'Create New User';
    document.getElementById('userForm').reset();
    document.getElementById('passwordGroup').classList.remove('hidden');
    document.getElementById('password').required = true;
    editingUserId = null;
}

function editUser(id, username, email, firstName, lastName, isActive) {
    toggleModal(true);
    document.getElementById('modalTitle').textContent = 'Edit User';
    document.getElementById('username').value = username;
    document.getElementById('email').value = email;
    document.getElementById('firstName').value = firstName;
    document.getElementById('lastName').value = lastName;
    document.getElementById('passwordGroup').classList.add('hidden');
    document.getElementById('password').required = false;
    editingUserId = id;
}

function closeUserModal() {
    toggleModal(false);
}

document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;

    const userData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value
    };

    if (!editingUserId) {
        userData.password = document.getElementById('password').value;
    }

    try {
        const url = editingUserId ? `/api/users/${editingUserId}/` : '/api/users/';
        const method = editingUserId ? 'PATCH' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            closeUserModal();
            loadUsers();
        } else {
            alert('Failed to save user');
        }
    } catch (error) {
        console.error('Error:', error.message);
        alert('Error: ' + error.message);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

async function toggleUserStatus(userId, newStatus, username) {
    try {
        const response = await fetch(`/api/users/${userId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ is_active: newStatus })
        });

        if (response.ok) loadUsers();
    } catch (error) { console.error(error); }
}

async function deleteUser(userId, username) {
    if (!confirm(`Delete user "${username}"?\nThis cannot be undone.`)) return;

    try {
        const response = await fetch(`/api/users/${userId}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });

        if (response.ok) loadUsers();
    } catch (error) { console.error(error); }
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            if (!term) { renderUsers(allUsers); return; }

            const filtered = allUsers.filter(u =>
                u.username.toLowerCase().includes(term) ||
                (u.email && u.email.toLowerCase().includes(term)) ||
                `${u.first_name} ${u.last_name}`.toLowerCase().includes(term)
            );
            renderUsers(filtered);
        });
    }
    loadUsers();
});
