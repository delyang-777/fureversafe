// Global variables
let searchTimeout;

// Document ready function
$(document).ready(function() {
    initializeTooltips();
    initializeSearch();
    initializeFormValidation();
    loadDashboardStats();
    setupAutoHideAlerts();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = $('#global-search');
    const searchResults = $('#search-results');
    
    if (searchInput.length) {
        searchInput.on('input', function() {
            clearTimeout(searchTimeout);
            const query = $(this).val();
            
            if (query.length < 2) {
                searchResults.removeClass('show').empty();
                return;
            }
            
            searchTimeout = setTimeout(function() {
                performSearch(query);
            }, 300);
        });
        
        // Close search results when clicking outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.search-bar').length) {
                searchResults.removeClass('show').empty();
            }
        });
    }
}

// Perform search via AJAX
function performSearch(query) {
    $.ajax({
        url: '/api/search',
        method: 'GET',
        data: { q: query },
        success: function(data) {
            displaySearchResults(data);
        },
        error: function(xhr, status, error) {
            console.error('Search error:', error);
        }
    });
}

// Display search results
function displaySearchResults(results) {
    const searchResults = $('#search-results');
    searchResults.empty();
    
    let hasResults = false;
    
    // Display dog results
    if (results.dogs && results.dogs.length > 0) {
        hasResults = true;
        searchResults.append('<div class="search-section"><strong>Dogs</strong></div>');
        results.dogs.forEach(function(dog) {
            searchResults.append(`
                <a href="/dog/${dog.id}" class="search-result-item">
                    <i class="fas fa-dog"></i> ${dog.name}
                </a>
            `);
        });
    }
    
    // Display adoption listings
    if (results.listings && results.listings.length > 0) {
        hasResults = true;
        searchResults.append('<div class="search-section"><strong>Adoption Listings</strong></div>');
        results.listings.forEach(function(listing) {
            searchResults.append(`
                <a href="/adoption/${listing.id}" class="search-result-item">
                    <i class="fas fa-heart"></i> ${listing.name}
                </a>
            `);
        });
    }
    
    // Display educational resources
    if (results.resources && results.resources.length > 0) {
        hasResults = true;
        searchResults.append('<div class="search-section"><strong>Educational Resources</strong></div>');
        results.resources.forEach(function(resource) {
            searchResults.append(`
                <a href="/education/${resource.id}" class="search-result-item">
                    <i class="fas fa-graduation-cap"></i> ${resource.title}
                </a>
            `);
        });
    }
    
    if (!hasResults) {
        searchResults.append('<div class="search-result-item text-muted">No results found</div>');
    }
    
    searchResults.addClass('show');
}

// Initialize form validation
function initializeFormValidation() {
    // Add custom validation for date inputs
    $('form').on('submit', function(e) {
        let isValid = true;
        
        // Validate future dates for appointments
        $('input[type="datetime-local"]').each(function() {
            const selectedDate = new Date($(this).val());
            const now = new Date();
            
            if ($(this).closest('form').find('input[name="appointment_type"]').length && selectedDate < now) {
                alert('Appointment date must be in the future');
                isValid = false;
                return false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
}

// Load dashboard statistics
function loadDashboardStats() {
    if ($('#dashboard-stats').length) {
        $.ajax({
            url: '/api/dashboard/stats',
            method: 'GET',
            success: function(data) {
                updateDashboardUI(data);
            },
            error: function(xhr, status, error) {
                console.error('Stats error:', error);
            }
        });
    }
}

// Update dashboard UI with stats
function updateDashboardUI(data) {
    if (data.total_dogs !== undefined) {
        $('#total-dogs').text(data.total_dogs);
    }
    if (data.upcoming_appointments !== undefined) {
        $('#upcoming-appointments').text(data.upcoming_appointments);
    }
    if (data.vaccinations_due !== undefined) {
        $('#vaccinations-due').text(data.vaccinations_due);
    }
}

// Setup auto-hide for alerts
function setupAutoHideAlerts() {
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

// Image preview for uploads
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $(previewId).attr('src', e.target.result).show();
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Confirm deletion
function confirmDelete(message, callback) {
    if (confirm(message || 'Are you sure you want to delete this item?')) {
        callback();
    }
}

// Load more content for infinite scroll
let loading = false;
$(window).on('scroll', function() {
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
        if (!loading && $('#load-more-trigger').length) {
            loading = true;
            $('#load-more-trigger').trigger('click');
        }
    }
});

// Handle adoption application status updates
function updateApplicationStatus(applicationId, status) {
    $.ajax({
        url: `/adoption/application/${applicationId}/${status}`,
        method: 'POST',
        success: function(response) {
            location.reload();
        },
        error: function(xhr, status, error) {
            alert('Error updating application status');
        }
    });
}

// Mark lost/found report as resolved
function resolveReport(reportId) {
    if (confirm('Mark this report as resolved?')) {
        $.ajax({
            url: `/lost-found/${reportId}/resolve`,
            method: 'POST',
            success: function(response) {
                location.reload();
            },
            error: function(xhr, status, error) {
                alert('Error resolving report');
            }
        });
    }
}

// Filter adoption listings
function filterAdoptions() {
    const breed = $('#filter-breed').val();
    const size = $('#filter-size').val();
    const age = $('#filter-age').val();
    
    window.location.href = `/adoptions?breed=${breed}&size=${size}&age=${age}`;
}

// Export data functionality
function exportData(type) {
    window.location.href = `/export/${type}`;
}

// Print dog profile
function printDogProfile(dogId) {
    const printWindow = window.open(`/dog/${dogId}/print`, '_blank');
    printWindow.print();
}

// Share on social media
function shareOnSocial(platform, url, title) {
    let shareUrl = '';
    switch(platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
            break;
    }
    window.open(shareUrl, '_blank', 'width=600,height=400');
}

// Initialize charts if on dashboard
if ($('#adoption-chart').length) {
    loadAdoptionChart();
}

function loadAdoptionChart() {
    $.ajax({
        url: '/api/adoption-stats',
        method: 'GET',
        success: function(data) {
            // Initialize chart with data
            const ctx = document.getElementById('adoption-chart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Adoptions',
                        data: data.values,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        tension: 0.4
                    }]
                }
            });
        }
    });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = $(`
        <div class="toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(notification);
    const toast = new bootstrap.Toast(notification);
    toast.show();
    
    notification.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Add CSRF token to AJAX requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
    }
});


// Notification functions
function loadNotifications(showAll = false) {
    $.ajax({
        url: '/api/notifications',
        method: 'GET',
        data: { page: 1, per_page: 10 },
        success: function(data) {
            displayNotifications(data.notifications);
            updateNotificationBadge(data.total);
        }
    });
}

function displayNotifications(notifications) {
    const container = $('#notificationList');
    container.empty();
    
    if (notifications.length === 0) {
        container.html('<div class="dropdown-item text-center text-muted">No new notifications</div>');
        return;
    }
    
    notifications.forEach(notification => {
        let icon = getNotificationIcon(notification.type);
        let bgColor = getNotificationColor(notification.type);
        
        container.append(`
            <div class="dropdown-item notification-item" data-id="${notification.id}">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <i class="${icon} fs-5" style="color: ${bgColor}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <strong>${escapeHtml(notification.title)}</strong>
                        <div class="small text-muted">${escapeHtml(notification.message)}</div>
                        <small class="text-muted">${timeAgo(notification.created_at)}</small>
                    </div>
                    <button class="btn btn-sm btn-link text-muted" onclick="markRead(${notification.id})">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            </div>
        `);
    });
}

function getNotificationIcon(type) {
    const icons = {
        'approval': 'fas fa-user-check',
        'adoption': 'fas fa-heart',
        'lost_found': 'fas fa-search',
        'appointment': 'fas fa-calendar-check',
        'system': 'fas fa-bell'
    };
    return icons[type] || 'fas fa-bell';
}

function getNotificationColor(type) {
    const colors = {
        'approval': '#28a745',
        'adoption': '#e83e8c',
        'lost_found': '#fd7e14',
        'appointment': '#17a2b8',
        'system': '#6c757d'
    };
    return colors[type] || '#007bff';
}

function updateNotificationBadge(count) {
    const badge = $('#notificationBadge');
    if (count > 0) {
        badge.text(count > 99 ? '99+' : count);
        badge.show();
    } else {
        badge.hide();
    }
}

function markRead(notificationId) {
    $.ajax({
        url: '/api/notifications/mark-read',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ notification_ids: [notificationId] }),
        success: function() {
            $(`.notification-item[data-id="${notificationId}"]`).fadeOut();
            updateUnreadCount();
        }
    });
}

function markAllRead() {
    $.ajax({
        url: '/api/notifications/mark-read',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ notification_ids: [] }),
        success: function() {
            $('#notificationList').html('<div class="dropdown-item text-center text-muted">No new notifications</div>');
            updateNotificationBadge(0);
        }
    });
}

function updateUnreadCount() {
    $.ajax({
        url: '/api/notifications/count',
        method: 'GET',
        success: function(data) {
            updateNotificationBadge(data.count);
        }
    });
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load notifications every 30 seconds
setInterval(() => {
    if (window.location.pathname !== '/login') {
        updateUnreadCount();
        if ($('.dropdown-menu.show').length) {
            loadNotifications();
        }
    }
}, 30000);

// Load notifications on page load
$(document).ready(function() {
    if (window.location.pathname !== '/login') {
        updateUnreadCount();
    }
});

// Load notifications when dropdown opens
$('.dropdown-toggle[data-bs-toggle="dropdown"]').on('shown.bs.dropdown', function() {
    if ($(this).find('.fa-bell').length) {
        loadNotifications();
    }
});