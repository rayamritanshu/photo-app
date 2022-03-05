const story2Html = story => {
    return `
        <div>
            <img src="${ story.user.thumb_url }" class="pic" alt="profile pic" />
            <p>${ story.user.username }</p>
        </div>
    `;
};

// fetch data from your API endpoint:
const displayStories = () => {
    fetch('/api/stories')
        .then(response => response.json())
        .then(stories => {
            const html = stories.map(story2Html).join('\n');
            document.querySelector('.stories').innerHTML = html;
        })
};

const escBtn = ev => {
    const key = ev.which || ev.keyCode;
    const isModalOpen = document.querySelector('#modal') && !document.querySelector('#modal').classList.contains('hidden');
    if (key === 27 && isModalOpen) {
        hideModal();
        ev.stopPropagation();
    }
};

 const user2Html = user => {
    return `
        <img src="${ user.thumb_url }" 
            class="pic" 
            alt="Profile pic for ${ user.username }" />
        <h2> ${ user.username }</h2>
    `;
};
  
const displayProfile = () => {

    fetch('/api/profile')
        .then(response => response.json())
        .then(user => {
            document.querySelector('aside header').innerHTML = user2Html(user);
        });
};

const follow = userId => {
    console.log('follow', userId);
    fetch(`/api/following/`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "user_id": userId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const elem = document.querySelector(`#follow-${data.following.id}`);
        elem.innerHTML = 'unfollow';
        elem.classList.add('active');
        elem.setAttribute('aria-checked', 'true');
        elem.setAttribute('aria-label', "Unfollowed " + elem.dataset.username);
        elem.setAttribute('data-following-id', data.id);
    });
};

const unfollow = (followingId, userId) => {
    console.log('unfollowed', followingId, userId);
    fetch(`/api/following/${followingId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const elem = document.querySelector(`#follow-${userId}`);
        elem.innerHTML = 'follow';
        elem.classList.remove('active');
        elem.removeAttribute('data-following-id');
        elem.setAttribute('aria-checked', 'false');
        elem.setAttribute('aria-label', "Follow " + elem.dataset.username);
    });
};

 const followUnfollowBtn = ev => {
    const elem = ev.currentTarget;
    const userId = elem.dataset.userId;
    if (elem.getAttribute('aria-checked').trim() === 'false') {
        follow(userId);
    } else {
        const fId = elem.dataset.followingId;
        unfollow(fId, userId);
    }
};

 const suggestion2Html = user => {
    return `
        <section>
            <img src="${ user.thumb_url }" class="pic" alt="Profile pic for ${ user.username }" />
            <div>
                <p>${ user.username }</p>
                <p>suggested for you</p>
            </div>
            <div>
                <button 
                    class="link following" 
                    id="follow-${ user.id }" 
                    data-username="${ user.username }" 
                    data-user-id="${ user.id }" 
                    aria-checked="false" 
                    aria-label="Follow ${ user.username }" 
                    onclick="followUnfollowBtn(event)">follow
                </button>
            </div>
        </section>
    `;
};

  
const displaySuggestions = () => {
    fetch('/api/suggestions')
        .then(response => response.json())
        .then(suggestedUsers => {
            document.querySelector('.suggestions > div').innerHTML = 
            suggestedUsers.map(suggestion2Html).join('\n');
        });
};

const posts2HTML = post => {
    return `
    <section class="card" id="post-${post.id}">
        <div class="header">
            <h4>${ post.user.username }</h4>
            <i class="fa fa-dots"></i>
        </div>
        <img src="${ post.image_url }" alt="Image posted by ${ post.user.username }" width="300" height="300">
        <div class="info">
            <div class="buttons">
                <div>
                    <button 
                        class="like" 
                        data-post-id="${ post.id }" 
                        data-like-id="${ post.current_user_like_id || ''}" 
                        aria-label="Like Button" 
                        aria-checked="${post.current_user_like_id ? 'true' : 'false'}" 
                        onclick="likesToggle(event)">
                        <i class="${post.current_user_like_id ? 'fas' : 'far'} fa-heart"></i>                        
                    </button>
                    <i class="far fa-comment"></i>
                    <i class="far fa-paper-plane"></i>
                </div>
                <div>
                <button 
                    class="bookmark" 
                    data-post-id="${ post.id }" 
                    data-bookmark-id="${ post.current_user_bookmark_id || ''}" 
                    aria-label="Bookmark Button" 
                    aria-checked="${post.current_user_bookmark_id ? 'true' : 'false'}" 
                    onclick="bookmarksToggle(event)">
                    <i class="${post.current_user_bookmark_id ? 'fas' : 'far'} fa-bookmark"></i>
                </button>
                </div>
            </div>
            <p id="likes-${post.id}" class="likes"><strong>${ post.likes.length } ${ post.likes.length === 1 ? 'like' : 'likes' }</strong></p>
            <div class="caption">
                <p>
                    <strong>${ post.user.username }</strong> 
                    ${ post.caption }
                </p>
                <p class="timestamp">${ post.display_time }</p>
            </div>
            <div id="comments-${post.id}" class="comments">
                ${ comments2Html(post.comments) }
            </div>
        </div>
        
        <div class="add-comment">
            <div class="input-holder">
                <input class="comment-textbox" 
                    data-post-id="${post.id}" type="text" 
                    aria-label="Add a comment" 
                    placeholder="Add a comment..." 
                    onkeyup="addComment(event)" />
            </div>
            <button class="link" onclick="addComment(event)">Post</button>
        </div>
    </section>
    `;
};

const comments2Html = comments => {
    let html = '';
    if (comments.length > 1) {
        const postId = comments[0].post_id;
        html += `<p>
                <button id="post-detail-${postId}" class="link" 
                    onclick="showPostDetail(event)"
                    data-post-id="${postId}">
                        View all ${ comments.length } comments
                </button>
            </p>`;
    }
    
    html += comments.slice(comments.length-1, comments.length).map(comment => {
        return `
            <p>
                <strong>${comment.user.username}</strong> 
                ${comment.text}
            </p>
            <p class="timestamp">${comment.display_time}</p>
        `
    }).join('\n');
    return html;
};

const displayPosts = () => {
    fetch('/api/posts')
        .then(response => response.json())
        .then(posts => {
            const html = posts.map(posts2HTML).join('\n');
            document.querySelector('#posts').innerHTML = html;
        })
};

const convertHTML = html => {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.firstElementChild;
};

const showPostDetail = ev => {
    postId = ev.currentTarget.dataset.postId;
    const id = ev.currentTarget.id;
    console.log(postId);

    fetch(`/api/posts/${postId}`)
        .then(response => response.json())
        .then(post => {
            console.log(post);
            const elem = convertHTML(getModal(id, post));
            document.body.appendChild(elem);
            document.body.style.overflowY = 'hidden';
            // EXTRA CREDIT - shifting focus on 'X' to escape
            document.querySelector('#close').focus();
        });
};

const hideModal = ev => {
    if (!ev || ev.target.id === 'modal' || ev.target.id === 'close') { 
        
        document.body.style.overflowY = 'auto';
        const elem = document.querySelector('#close');
        anchor = document.getElementById(elem.dataset.returnId);
        anchor.focus();
        const y = anchor.getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo({top: y, behavior: 'smooth'});


        document.querySelector('#modal').remove();
        if (ev) {
            ev.stopPropagation();
        }
    }
};

const updatePost = (postId, callback) => {
    fetch(`/api/posts/${postId}`)
        .then(response => response.json())
        .then(post => {
            const elem = document.querySelector(`#post-${post.id}`);
            const node = convertHTML(posts2HTML(post));
            elem.replaceWith(node);
            if (callback) {
                callback();
            }
        });
};

const addBookmark = postId => {
    fetch(`/api/bookmarks/`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post_id": postId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updatePost(postId, () => {
            const elem = document.querySelector(`#post-${postId}`);
            elem.querySelector('.bookmark').focus();
        });
        // set focus on like button
        const elem = document.querySelector(`#post-${postId}`);
        elem.querySelector('.bookmark').focus();
    });
};

const bookmarksToggle = ev => {
    const elem = ev.currentTarget;
    const bookmarkId = elem.dataset.bookmarkId;
    const isBookmarked = bookmarkId != '';
    const postId = elem.dataset.postId;
    if (!isBookmarked) {addBookmark(postId);} 
    else {removeBookmark(bookmarkId, postId);}  
};

const removeBookmark = (bookmarkId, postId) => {
    fetch(`/api/bookmarks/${bookmarkId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updatePost(postId, () => {
            const elem = document.querySelector(`#post-${postId}`);
            elem.querySelector('.bookmark').focus();
        });
    });
};

const likesToggle = ev => {
    const elem = ev.currentTarget
    const postId = elem.dataset.postId;
    const likeId = elem.dataset.likeId;
    const isLiked = likeId != '';
    if (!isLiked) {likePost(postId);} 
    else {unlikePost(likeId, postId);}  
};

const likePost = postId => {
    fetch(`/api/posts/${postId}/likes/`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post_id": postId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updatePost(postId, () => {
            const elem = document.querySelector(`#post-${postId}`);
            elem.querySelector('.like').focus();
        });
    });
};

const unlikePost = (likeId, postId) => {
    fetch(`/api/posts/${postId}/likes/${likeId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updatePost(postId, () => {
            const elem = document.querySelector(`#post-${postId}`);
            elem.querySelector('.like').focus();
        });
    });
};

const addComment = ev => {
    const elem = ev.currentTarget;
    let inputElement = elem;
    ev.preventDefault();

    if (elem.tagName.toUpperCase() === 'INPUT') {
        if (ev.keyCode !== KeyCodes.RETURN) {
            return;
        }
    } else {inputElement = elem.previousElementSibling.querySelector('input');}
    const comment = inputElement.value;
    if (comment.length === 0) {return;}
    const postId = inputElement.dataset.postId;
    const postData = {
        "post_id": postId,
        "text": comment
    };
    console.log(postData);
    fetch("/api/comments", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(comment => {
            updatePost(comment.post_id, () => {
                // refocus on input
                const elem = document.querySelector(`#post-${postId}`);
                elem.querySelector('.comment-textbox').focus();
            });
        });
};

const getPostDetail = post => {
    return `
        <div class="featured-image" style="background-image:url('${post.image_url}')"></div>
        <div class="container">
            <h3>
            <img class="pic" src="${post.user.thumb_url}" /> ${post.user.username}</h3>
            <div class="body">
                ${
                    getCommentDetail(
                        post.user.thumb_url, 
                        post.user.username,
                        post.caption,
                        post.display_time
                    )
                }
                ${
                    post.comments.map(comment => {
                        return getCommentDetail(
                            comment.user.thumb_url, 
                            comment.user.username,
                            comment.text,
                            comment.display_time
                        )
                    }).join('')
                }

            </div>
        </div>
    `;
};

const getModal = (returnId, post) => {
    return `
    <div id="modal" class="modal-bg" 
        onclick="hideModal(event);" data-return-id="${returnId}">
        <button 
            id="close" 
            class="close" 
            aria-label="Close Button"
            onclick="hideModal(event);" 
            data-return-id="${returnId}"><i class="fas fa-times"></i></button>
        <div class="modal" role="dialog" aria-live="assertive">
            ${getPostDetail(post)}
        </div>
    </div>
    `
}

const getCommentDetail = (imageURL, username, text, timestamp) => {
    return `<div class="comment">
        <img class="pic" src="${imageURL}" />
        <div>
            <p>
                <strong>${username}</strong> ${text}
            </p>
            <span>${timestamp}</span>
        </div>
        <button><i class="far fa-heart"></i></button>
    </div>`;
};


const initPage = () => {
    displayStories();
    displaySuggestions();
    displayProfile();
    displayPosts();
    document.addEventListener('keyup', escBtn);
};

initPage();