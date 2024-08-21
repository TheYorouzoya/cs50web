document.addEventListener('DOMContentLoaded', function () {

    document.body.addEventListener('click', (event) => {

        if (isLikeButton(event.target)) {
            event.preventDefault();
            likeClickedPost(event.target);

        } else if (isEditButton(event.target)) {
            event.preventDefault();
            replacePostContentWithEditForm(event.target);

        } else if (isSaveButton(event.target)) {
            event.preventDefault();
            saveAndUpdatePostContent(event.target);

        } else if (isFollowButton(event.target)) {
            event.preventDefault();
            followUser(event.target);
        }
    });

    document.querySelector('#follow-btn')?.addEventListener('mouseover', function (event) {
        if (this.textContent.includes("Following")) {
            this.innerHTML = `<i class="bi bi-x-lg"></i> Unfollow`;
        }
    });
    document.querySelector('#follow-btn')?.addEventListener('mouseout', function (event) {
        if (this.textContent.includes("Unfollow")) {
            this.innerHTML = `<i class="bi bi-check-lg"></i> Following`;
        }
    });

    // When new post form is submitted
    document.querySelector('#post-form')?.addEventListener('submit', function (event) {
        // Send post data with csrf token header
        event.preventDefault();
        fetch('/add_post', {
            method: 'POST',
            body: JSON.stringify({
                "content": document.querySelector('#post-field').value
            }),
            headers: {
                "X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value
            },
            credentials: 'same-origin'
        })
            .then(response => {
                return response.json();
            })
            .then(data => {
                // If there's an error, print it
                if (data.error) {
                    show_message(data.error, 'error');
                } else {
                    addNewPostToPage(data.post);
                }
            })
    });

});


function likeClickedPost(like_button) {
    const post_id = like_button.parentNode.parentNode.parentNode.dataset.id;

    fetch("/like_post", {
        method: "POST",
        body: JSON.stringify({
            "post_id": post_id
        }),
        headers: {
            "X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value
        },
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                show_message(data.error, 'error');
            } else {
                if (data.liked) {
                    like_button.parentNode.innerHTML = `<span class="like-btn bi-heart-fill"></span> ${data.likes}`;
                } else {
                    like_button.parentNode.innerHTML = `<span class="like-btn bi-heart"></span> ${data.likes}`;
                }
            }
        })
}


function followUser(follow_button) {
    const profile_user = follow_button.dataset.profile;

    fetch("/follow_user", {
        method: "POST",
        body: JSON.stringify({
            "followed": profile_user
        }),
        headers: {
            "X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value
        },
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                show_message(data.error, 'error');
            } else {
                document.querySelector('#followers').innerHTML = `followers: ${data.followers}`;
                if (data.message.includes("Follow")) {
                    document.querySelector('#follow-btn').textContent = 'Following';
                } else {
                    document.querySelector('#follow-btn').textContent = 'Follow';
                }
            }
        })
}


function replacePostContentWithEditForm(edit_button) {
    // Fetch the content div, copy contents, then empty it
    const content_div = edit_button.parentNode.parentNode.querySelector('.content');
    const post_content = content_div.querySelector('.post-text').textContent.replace(/[\n\r]+|[\s]{2,}/g, ' ').trim();
    content_div.innerHTML = '';

    // Initialize textarea, populate it, and append to content div
    const form_field = document.createElement('textarea');
    form_field.classList.add('form-control', 'post-text');
    form_field.setAttribute('rows', '3');
    form_field.setAttribute('cols', '20');
    form_field.textContent = post_content;
    content_div.append(form_field);

    // Initialize save button and append
    const save_button = document.createElement('button');
    save_button.classList.add('btn', 'btn-primary', 'btn-sm', 'btn-info', 'save-btn');
    save_button.innerText = "Save";
    content_div.append(save_button);
}


function saveAndUpdatePostContent(save_button) {
    const content_div = save_button.parentNode;
    const post_id = content_div.parentNode.dataset.id;
    const post_content = content_div.querySelector('textarea').value;

    fetch(`/edit/${post_id}`, {
        method: 'POST',
        body: JSON.stringify({
            "post_content": post_content
        }),
        headers: {
            "X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value
        },
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                show_message(data.error, 'error');
            } else {
                content_div.innerHTML = '';
                content_div.textContent = post_content;
            }
        })
}


// Function that adds a new post to DOM according to the post template in templates/post_layout.html
function addNewPostToPage(post) {
    document.querySelector('#post-field').value = '';
    const parent_container = document.querySelector('#posts_container');
    
    // Initialize post container, add class and dataset
    const post_container = document.createElement('div');
    post_container.classList.add('post');
    post_container.dataset.id = post.id;

    // Post header div
    const post_header = document.createElement('div');
    post_header.classList.add('post-header');
    // Initialize post header elements    
    const author = document.createElement('div');
    author.classList.add('author');
    const author_link = document.createElement('a');
    author_link.setAttribute('href', `/user/${post.author}`);
    author_link.textContent = post.author;
    author.append(author_link);

    const timestamp = document.createElement('div');
    timestamp.classList.add('timestamp');
    timestamp.textContent = post.timestamp;

    // Post Content div
    const content = document.createElement('div');
    content.classList.add('content');
    content.textContent = post.content;

    // Post footer div
    const post_footer = document.createElement('div');
    post_footer.classList.add('post-footer');
    // Initialize post footer elements
    const likes = document.createElement('div');
    likes.classList.add('likes');
    likes.innerHTML = `<span class="bi-heart"></span> <span class="like-counter">${post.likes}</span>`;

    const comments = document.createElement('div');
    comments.classList.add('comments');
    comments.innerHTML = `<a href="/post/${post.id}"><span class="bi-chat-right-text"></span> ${post.comments}</a>`;

    const edit_btn = document.createElement('div');
    edit_btn.classList.add('edit-btn');
    edit_btn.innerHTML = `<span class="bi-pencil"></span> Edit`;
    
    // Append header and footer elements
    post_header.append(author, timestamp);
    post_footer.append(likes, comments, edit_btn);

    // Append elements to post container
    post_container.append(post_header, content, post_footer);
    
    parent_container.prepend(document.createElement('hr'));
    parent_container.prepend(post_container);
    parent_container.focus();
    post_container.classList.add("animate");

}


function show_message(message, message_type) {
    // Select the message container and erase any existing messages
    const message_container = document.querySelector('#message');
    message_container.innerHTML = '';

    // Create message div and append it
    const element = document.createElement('div');
    element.setAttribute('role', 'alert');
    if (message_type === 'error') {
        element.classList.add('alert', 'alert-danger');
    } else {
        element.classList.add('alert', 'alert-success');
    }
    element.textContent = message;
    message_container.append(element);
    message_container.style.display = 'block';
}

function isLikeButton(target) {
    return target.classList.contains('like-btn');
}

function isEditButton(target) {
    return target.classList.contains('edit-btn');
}

function isSaveButton(target) {
    return target.classList.contains('save-btn');
}

function isFollowButton(target) {
    return target.id === 'follow-btn';
}
