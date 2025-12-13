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
        document.getElementById('usersBody').innerHTML = '<tr><td colspan="7" class="empty-state"><div class="empty-state-icon">⚠️</div><div>Error loading users. Please refresh the page.</div></td></tr>';
    }
}

function updateStats() {
    const total = allUsers.length;
    const active = allUsers.filter(u => u.is_active).length;
    const inactive = total - active;
    
    document.getElementById('totalUsers').textContent = total;
    document.getElementById('activeUsers').textContent = active;
    document.getElementById('inactiveUsers').textContent = inactive;
}

function renderUsers(users) {
    const tbody = document.getElementById('usersBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <div style="font-size: 1.2em; margin-bottom: 10px;">No users found</div>
                    <div>Click "Create User" to add your first user</div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map(user => {
        const fullName = [user.first_name, user.last_name].filter(n => n).join(' ') || '-';
        
        return `
            <tr>
                <td><strong>#${user.id}</strong></td>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5em;">👤</span>
                        <strong>${escapeHtml(user.username)}</strong>
                    </div>
                </td>
                <td>${escapeHtml(user.email) || '<span style="color: var(--text-light);">No email</span>'}</td>
                <td>${escapeHtml(fullName)}</td>
                <td>
                    <span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">
                        ${user.is_active ? '✓ Active' : '✗ Inactive'}
                    </span>
                </td>
                <td><span style="color: var(--text-secondary);">-</span></td>
                <td class="actions-column">
                    <div class="action-buttons">
                        <button class="btn btn-primary btn-action" onclick="editUser(${user.id}, '${escapeHtml(user.username)}', '${escapeHtml(user.email || '')}', '${escapeHtml(user.first_name || '')}', '${escapeHtml(user.last_name || '')}', ${user.is_active})">
                            ✏️ Edit
                        </button>
                        ${user.is_active ? 
                            `<button class="btn btn-disable btn-action" onclick="toggleUserStatus(${user.id}, false, '${escapeHtml(user.username)}')">🔒 Disable</button>` :
                            `<button class="btn btn-enable btn-action" onclick="toggleUserStatus(${user.id}, true, '${escapeHtml(user.username)}')">🔓 Enable</button>`
                        }
                        <button class="btn btn-danger btn-action" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">🗑️ Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, "\\'");
}

function showCreateModal() {
    document.getElementById('userModal').style.display = 'block';
    document.getElementById('modalTitle').textContent = 'Create New User';
    document.getElementById('userForm').reset();
    document.getElementById('passwordGroup').style.display = 'block';
    document.getElementById('password').required = true;
    editingUserId = null;
}

function editUser(id, username, email, firstName, lastName, isActive) {
    document.getElementById('userModal').style.display = 'block';
    document.getElementById('modalTitle').textContent = 'Edit User';
    document.getElementById('username').value = username;
    document.getElementById('email').value = email;
    document.getElementById('firstName').value = firstName;
    document.getElementById('lastName').value = lastName;
    document.getElementById('passwordGroup').style.display = 'none';
    document.getElementById('password').required = false;
    editingUserId = id;
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
    editingUserId = null;
}

document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
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
            const error = await response.json();
            console.error('Error:', error);
        }
    } catch (error) {
        console.error('Error:', error.message);
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
        
        if (response.ok) {
            loadUsers(); // Refresh the user list immediately
        } else {
            console.error('Error updating user status');
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?\n\nThis will also delete all their sessions and data.`)) return;
    
    try {
        const response = await fetch(`/api/users/${userId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            loadUsers(); // Refresh the user list immediately
        } else {
            console.error('Error deleting user');
        }
    } catch (error) {
        console.error('Error:', error.message);
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            
            if (!searchTerm) {
                renderUsers(allUsers);
                return;
            }
            
            const filtered = allUsers.filter(user => {
                const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase();
                return user.username.toLowerCase().includes(searchTerm) ||
                       (user.email && user.email.toLowerCase().includes(searchTerm)) ||
                       fullName.includes(searchTerm);
            });
            
            renderUsers(filtered);
        });
    }
    
    // Load users
    loadUsers();
});
