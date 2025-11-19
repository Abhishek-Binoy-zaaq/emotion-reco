let editingUserId = null;

async function loadUsers() {
    try {
        const response = await fetch('/api/users/');
        const data = await response.json();
        const users = data.results || data;
        
        const tbody = document.getElementById('usersBody');
        
        if (!users || users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">No users found. Click "Create User" to add one.</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email || 'N/A'}</td>
                <td>${user.first_name || ''} ${user.last_name || ''}</td>
                <td>
                    <span style="color: ${user.is_active ? '#28a745' : '#dc3545'}">
                        ${user.is_active ? '✓ Active' : '✗ Inactive'}
                    </span>
                </td>
                <td>-</td>
                <td>
                    <button class="btn" style="padding: 8px 12px; margin: 2px;" onclick="editUser(${user.id}, '${escapeHtml(user.username)}', '${escapeHtml(user.email || '')}', '${escapeHtml(user.first_name || '')}', '${escapeHtml(user.last_name || '')}', ${user.is_active})">✏️ Edit</button>
                    ${user.is_active ? 
                        `<button class="btn" style="padding: 8px 12px; margin: 2px; background: #ffc107;" onclick="toggleUserStatus(${user.id}, false, '${escapeHtml(user.username)}')">🔒 Disable</button>` :
                        `<button class="btn" style="padding: 8px 12px; margin: 2px; background: #28a745;" onclick="toggleUserStatus(${user.id}, true, '${escapeHtml(user.username)}')">🔓 Enable</button>`
                    }
                    <button class="btn btn-danger" style="padding: 8px 12px; margin: 2px;" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">🗑️ Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersBody').innerHTML = '<tr><td colspan="7" style="text-align: center; color: #dc3545; padding: 20px;">Error loading users</td></tr>';
    }
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
            alert(editingUserId ? 'User updated successfully!' : 'User created successfully!');
        } else {
            const error = await response.json();
            alert('Error: ' + JSON.stringify(error));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function toggleUserStatus(userId, newStatus, username) {
    const action = newStatus ? 'enable' : 'disable';
    if (!confirm(`Are you sure you want to ${action} user "${username}"?`)) return;
    
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
            alert(`User ${action}d successfully!`);
            loadUsers();
        } else {
            alert('Error updating user status');
        }
    } catch (error) {
        alert('Error: ' + error.message);
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
            alert('User deleted successfully!');
            loadUsers();
        } else {
            alert('Error deleting user');
        }
    } catch (error) {
        alert('Error: ' + error.message);
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

loadUsers();
