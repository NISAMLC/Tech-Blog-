from django import template
from blog.models import Post
from django.db.models import Count

register = template.Library()

"""
Each module that contains template tags needs to define a variable called register to be a valid tag
library. This variable is an instance of template.Library, and it’s used to register the template tags
and filters of the application.
"""

@register.simple_tag
def total_posts():
    return Post.published.count()

# @register.simple_tag
# def is_ai():
#     posts = Post.published.all()
#     ai_posts = [post.title for post in posts if post.title.startswith('AI')]
#     return ai_posts


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]



"""
Creating a template filter to support Markdown syntax
"""

from django.utils.safestring import mark_safe
import markdown

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))