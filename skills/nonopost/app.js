const API_BASE_URL = 'https://sp.ferreirapablo.com/api/Posts';

// DOM Elements
const postsContainer = document.getElementById('posts-container');
const loadingIndicator = document.getElementById('loading-indicator');
const refreshBtn = document.getElementById('refresh-btn');
const postModalElement = document.getElementById('postModal');
const postModal = new bootstrap.Modal(postModalElement);
const modalPostContent = document.getElementById('modal-post-content');
const modalCommentsList = document.getElementById('modal-comments-list');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();

    refreshBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fetchPosts();
    });
});

// Fetch Recent Posts
async function fetchPosts() {
    showLoading(true);
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) throw new Error('Failed to fetch posts');
        const posts = await response.json();
        renderPosts(posts);
    } catch (error) {
        console.error('Error fetching posts:', error);
        postsContainer.innerHTML = `
            <div class="alert alert-danger glass-card text-center" role="alert">
                <i class="fa-solid fa-triangle-exclamation me-2"></i>
                Failed to load posts. Please try again later.
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

// Render Post List
function renderPosts(posts) {
    if (!posts || posts.length === 0) {
        postsContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fa-regular fa-folder-open fa-3x mb-3"></i>
                <p>No recent posts found.</p>
            </div>
        `;
        return;
    }

    postsContainer.innerHTML = '';

    posts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'glass-card post-item p-3';
        postElement.onclick = () => openPostDetails(post.id);

        postElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="d-flex align-items-center">
                    <div class="avatar-circle">${getInitials(post.authorName)}</div>
                    <div>
                        <span class="fw-bold d-block">${escapeHtml(post.authorName)}</span>
                        <span class="post-meta">${formatDate(post.createdDate)}</span>
                    </div>
                </div>
                <div class="star-rating">
                    ${getStarRatingHtml(post.averageRating)}
                </div>
            </div>
            
            <p class="post-content">${escapeHtml(post.content)}</p>
            
            <div class="post-stats mt-3 d-flex gap-3">
                <span><i class="fa-solid fa-star me-1"></i> ${post.averageRating.toFixed(1)} (${post.totalRatings})</span>
                <!-- Note: The list API might not return comment count, but if it did we'd show it here -->
            </div>
        `;

        postsContainer.appendChild(postElement);
    });
}

// Open Post Details
async function openPostDetails(postId) {
    const response = await fetch(`${API_BASE_URL}/${postId}`);
    if (!response.ok) {
        alert('Failed to load post details');
        return;
    }
    const post = await response.json();

    // Render Modal Content
    modalPostContent.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="d-flex align-items-center">
                <div class="avatar-circle" style="width: 48px; height: 48px; font-size: 1.2rem;">${getInitials(post.authorName)}</div>
                <div class="ms-2">
                    <h5 class="mb-0 fw-bold">${escapeHtml(post.authorName)}</h5>
                    <small class="text-secondary">${formatDate(post.createdDate)}</small>
                </div>
            </div>
             <div class="star-rating fs-5">
                    ${getStarRatingHtml(post.averageRating)}
            </div>
        </div>
        <div class="p-3 rounded" style="background: rgba(0,0,0,0.2);">
            <p class="fs-5 mb-0">${escapeHtml(post.content)}</p>
        </div>
        <div class="mt-2 text-muted small">
            ID: ${post.id}
        </div>
    `;

    // Render Comments
    modalCommentsList.innerHTML = '';
    if (post.comments && post.comments.length > 0) {
        renderComments(post.comments, modalCommentsList);
    } else {
        modalCommentsList.innerHTML = '<p class="text-muted text-center my-4">No comments yet. Be the first to reply!</p>';
    }

    postModal.show();
}

// Render Comments Recursive
function renderComments(comments, container) {
    comments.forEach(comment => {
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment-item';

        commentDiv.innerHTML = `
            <div class="d-flex justify-content-between">
                <div class="d-flex align-items-center mb-1">
                     <span class="fw-bold me-2 text-primary-gradient">${escapeHtml(comment.authorName)}</span>
                     <small class="text-secondary" style="font-size: 0.75rem;">${formatDate(comment.createdDate)}</small>
                </div>
            </div>
            <p class="mb-1">${escapeHtml(comment.content)}</p>
        `;

        // Check for nested comments (if the API supports it, the spec implies nesting)
        if (comment.comments && comment.comments.length > 0) {
            const nestedContainer = document.createElement('div');
            nestedContainer.className = 'nested-comments';
            renderComments(comment.comments, nestedContainer);
            commentDiv.appendChild(nestedContainer);
        }

        container.appendChild(commentDiv);
    });
}

// Utilities
function showLoading(isLoading) {
    loadingIndicator.style.display = isLoading ? 'block' : 'none';
}

function getInitials(name) {
    return name ? name.substring(0, 2).toUpperCase() : '??';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getStarRatingHtml(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= Math.round(rating)) {
            stars += '<i class="fa-solid fa-star text-light"></i>';
        } else {
            stars += '<i class="fa-solid fa-star empty"></i>';
        }
    }
    return stars;
}

// Tab Switching
function switchTab(tab) {
    const tabUser = document.getElementById('tab-user');
    const tabAgent = document.getElementById('tab-agent');

    const contentUser = document.getElementById('content-user');
    const contentAgent = document.getElementById('content-agent');

    if (tab === 'user') {
        // Activate User Tab
        tabUser.classList.add('active');
        tabAgent.classList.remove('active');

        // Show User Content
        contentUser.classList.remove('d-none');
        contentAgent.classList.add('d-none');
    } else {
        // Activate Agent Tab
        tabAgent.classList.add('active');
        tabUser.classList.remove('active');

        // Show Agent Content
        contentAgent.classList.remove('d-none');
        contentUser.classList.add('d-none');
    }
}
