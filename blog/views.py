from django.shortcuts import render,get_object_or_404
from django.http import Http404
from . models import Post,Comment
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag

from django.db.models import Count
# Create your views here.

def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag,slug = tag_slug)
        post_list = post_list.filter(tags__in=[tag]) #here tags coming from tags = TaggableManager()

    paginator = Paginator(post_list,3)
    page_number = request.GET.get('page',1) #page is our arguement after ? we can change it like ?kadalas
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/post/list.html',{'posts':posts,'tag':tag})

def post_detail(request,year,month,day,post):
    try:
        # post = get_object_or_404(Post,id=id,status=Post.Status.PUBLISHED)
        post = Post.published.get(
                                  slug=post,
                                  publish__year = year,
                                  publish__month=month,
                                  publish__day=day)
    except Post.DoesNotExist:
        raise Http404("No Post Found")

    #list of active comments
    comments = post.comments.filter(active=True)
    """We use the
    comments manager for the related Comment objects that we previously defined in the Comment
    model, using the related_name attribute of the ForeignKey field to the Post model."""
    #form for users to comment
    form  = CommentForm()

    """list of similar posts"""
    post_tags_ids = post.tags.values_list('id',flat=True)
    """You pass flat=True to it to get single values
    such as [1, 2, 3, ...] instead of one-tuples such as [(1,), (2,), (3,) ...]."""
    similar_posts = Post.published.filter(tags__in= post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    #annotate will ass a new field to each object and we are using that to order_by

    return render(request,'blog/post/detail.html',{'post':post,'comments':comments,'form':form,'similar_posts':similar_posts})

#view to share posts
def post_share(request,post_id):
    try:
        post = Post.published.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404('Post not found')

    sent =False
    if request.method=='POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd  = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read " \
                      f" {post.title}  "
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject,message,'nisamchess@gmail.com',[cd['to']])
            sent=True

    else:
        form = EmailPostForm() #method is not post means it is get so show the form z
    return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent})


"""View for the comment section"""

@require_POST
def post_comment(reqest,post_id):
    try:
        post = Post.published.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404('Post not found')
    comment = None
    form = CommentForm(data=reqest.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        #save into the db
        comment.save()
    return render(reqest,'blog/post/comment.html',{'post':post,'form':form,'comment':comment})

""""
Search view
"""

from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.contrib.postgres.search import TrigramSimilarity

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title',weight='A') + SearchVector('title',weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,'blog/post/search.html',{'form': form,'query': query,'results': results})


