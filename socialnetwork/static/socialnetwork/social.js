function getPostList() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", "/socialnetwork/get-global", true)
    xhr.send()
}

function getPostListFollower() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", "/socialnetwork/get-follower", true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateList(response)
        return
    }
    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }


    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)

}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function updateList(items) {
    // Removes all existing to-do list items
    let list = document.getElementById("all_posts")
    
    let posts = items.posts

    let comments = items.comments
    // console.log(`posts: ${posts.length} comments: ${comments.length}`)
    if ((posts.length == 0) && (comments.length == 1)){
        // console.log('add comment special case')
        let new_comment    = comments[0]
        let post_to_update = document.getElementById(`id_post_div_${new_comment.post_id}`)
        let comment_list = document.getElementById(`id_comment_container_post_${new_comment.post_id}`)
        comment_list.append(makeCommentElement(new_comment))
        return
    }

    // Adds each to do list item received from the server to the displayed list
    posts.forEach(item => {
        if (document.getElementById(`id_post_div_${item.id}`) == null){
            list.prepend(makeListItemElement(item))
        }
        let comment_list = document.getElementById(`id_comment_container_post_${item.id}`)

    
        comments.forEach(comment => {
            if (comment.post_id == item.id){
                if (document.getElementById(`id_comment_text_${comment.id}`) == null){
                    comment_list.append(makeCommentElement(comment))
                }
            }
            
        })

    })

    
}

function addComment(post_id, text){
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("POST", '../add-comment', true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`post_id=${post_id}&comment_text=${text}&csrfmiddlewaretoken=${getCSRFToken()}`)

}

function makeListItemElement(item) {

    
    // let details = `<span class="details">(id=${item.id}, user=${item.user})</span>`

    let post_div      = document.createElement("div")
    post_div.id       = `id_post_div_${item.id}`
    post_div.className    = "container"



    let profile_link    = document.createElement("a")
    profile_link.id     = `id_post_profile_${item.id}`
    let user                = item.user
    let myUserName          = item.signed_in_user;
    if (user == myUserName){
        profile_link.href = "../user_profile"
    } else {
        profile_link.href = `../other_profile/${item.user_id}`
    }
    profile_link.innerHTML = `${item.user_full_name}`


    let post_text       = document.createElement("div")
    post_text.id        = `id_post_text_${item.id}`
    post_text.className = "text-secondary"
    post_text.innerHTML = item.text

    let post_dt         = document.createElement("div")
    post_dt.id          = `id_post_date_time_${item.id}`
    post_dt.className   = "text-success"
    post_dt.innerHTML   = item.creation_time

    let comm_in         = document.createElement('input')
    comm_in.type        = "text"
    comm_in.id          = `id_comment_input_text_${item.id}`
    comm_in.name        = `id_comment_input_text_${item.id}`

    let comm_btn        = document.createElement('button')

    comm_btn.onclick    = function(){
        addComment(item.id, comm_in.value, item.signed_in_user_id)
    }
    comm_btn.innerHTML  = "Add comment"
    comm_btn.id         = `id_comment_button_${item.id}`



    let comm_container  = document.createElement("div")
    comm_container.className = "col-6"
    comm_container.id        = `id_comment_container_post_${item.id}`
    let row = document.createElement("div")
    row.className = 'row'
    let col = document.createElement("div")
    col.classList = 'col-3'

    comm_container.appendChild(comm_in)
    comm_container.appendChild(comm_btn)
 
    row.appendChild(col)
    row.appendChild(comm_container)


    post_div.appendChild(profile_link)
    post_div.appendChild(post_text)
    post_div.appendChild(post_dt)
    post_div.appendChild(row)
    // post_div.appendChild(col)
    // post_div.appendChild(comm_container)
    return post_div
}

function makeCommentElement(comment){
    let comment_div     = document.createElement("div")
    comment_div.id      = `id_comment_div_${comment.id}`
    comment_div.className = "container ml-5"

    let commenter          = document.createElement("a")
    commenter.innerHTML    = comment.creator_fullname
    commenter.id      = `id_comment_profile_${comment.id}`
    let user                = comment.creator_username
    let myUserName          = comment.signed_in_user;
    if (user == myUserName){
        commenter.href = "../user_profile"
    } else {
        commenter.href = `../other_profile/${comment.creator_user_id}`
    }


    let comment_text       = document.createElement("div")
    comment_text.className = "text-secondary"
    comment_text.innerHTML = comment.text
    comment_text.id      = `id_comment_text_${comment.id}`

    let comment_dt         = document.createElement("div")
    comment_dt.id          = `id_comment_date_time_${comment.id}`
    comment_dt.className   = "text-success"
    comment_dt.innerHTML   = comment.creation_time

    comment_div.appendChild(commenter)
    comment_div.appendChild(comment_text)
    comment_div.appendChild(comment_dt)
    return comment_div

}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}
