function getComments() {
    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;
    let no_posts = document.getElementById("no-posts").value;
    let sort_type = document.querySelector('input[name="sort"]:checked').value;
    console.log([page_type, page_name, no_posts, sort_type])
}