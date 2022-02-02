function getComments() {
    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;
    let no_posts = document.getElementById("no-posts").value;
    let sort_type = document.querySelector('input[name="sort"]:checked').value;
    let user_input = {
        'page_type': page_type,
        'page_name': page_name,
        'no_posts': no_posts,
        'sort_type': sort_type
    }

    fetch("/getuserinput", {
      method: "POST",
      body: JSON.stringify(user_input)
    }).then(res => {
      console.log("Request complete! response:", res);
    });
}