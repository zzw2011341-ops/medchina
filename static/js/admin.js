// MedChina Admin JavaScript

// API Request Helper
function apiRequest(url, method, data, callback, error_callback) {
    const token = localStorage.getItem('admin_token');
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        data: data ? JSON.stringify(data) : undefined,
        success: function(response) {
            if (callback) callback(response);
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                // Unauthorized, redirect to login
                localStorage.removeItem('admin_token');
                localStorage.removeItem('admin_user');
                window.location.href = '/admin/login';
                return;
            }
            
            const error = xhr.responseJSON ? xhr.responseJSON.detail : '操作失败';
            if (error_callback) {
                error_callback(error);
            } else {
                showAlert(error, 'danger');
            }
        }
    });
}

// Show Alert
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remove existing alerts
    $('.alert').remove();
    
    // Prepend to container
    $('.container-fluid').prepend(alertHtml);
    
    // Auto dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
}

// Format Date
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format Number
function formatNumber(number) {
    if (number === null || number === undefined) return '-';
    return parseFloat(number).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Logout
function logout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        window.location.href = '/admin/login';
    }
}

// Get Current User
function getCurrentUser() {
    const userStr = localStorage.getItem('admin_user');
    return userStr ? JSON.parse(userStr) : null;
}

// Initialize DataTable
function initializeDataTable(tableId, columns, ajaxUrl) {
    const table = $(`#${tableId}`).DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: ajaxUrl,
            type: 'GET',
            beforeSend: function(xhr) {
                const token = localStorage.getItem('admin_token');
                xhr.setRequestHeader('Authorization', 'Bearer ' + token);
            }
        },
        columns: columns,
        language: {
            processing: '处理中...',
            search: '搜索:',
            lengthMenu: '显示 _MENU_ 条记录',
            info: '显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条',
            infoEmpty: '没有记录',
            infoFiltered: '(从 _MAX_ 条记录中过滤)',
            paginate: {
                first: '首页',
                previous: '上一页',
                next: '下一页',
                last: '末页'
            }
        },
        pageLength: 20,
        lengthMenu: [10, 20, 50, 100]
    });
    
    return table;
}

// Document Ready
$(document).ready(function() {
    // Check authentication on all admin pages except login
    if (!window.location.pathname.includes('/admin/login')) {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            window.location.href = '/admin/login';
        }
    }
});
