from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Post
from .forms import PostForm, ReplyForm
from courses.models import Course
from enrollment.models import Enroll

# Create your views here.

def can_user_access_discussion(user, course):
    if user.is_authenticated:
        is_instructor = course.instructor == user
        is_enrolled = Enroll.objects.filter(student= user, course= course).exists()
        return is_instructor or is_enrolled
    return False


@login_required
def post_list(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug)

    if not can_user_access_discussion(request.user, course):
        messages.error(request, "You must enroll to view the discussion.")
        return redirect('courses:course_details', course_slug= course.slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit= False)
            new_post.course = course
            new_post.author = request.user
            new_post.save()
            messages.success(request, "New topic posted successfully.")
            return redirect('discussion:post_list', course_slug= course.slug)
        
    else:
        form = PostForm()

    # Fetch top level posts only.
    posts = Post.objects.filter(course= course, parent__isnull= True).select_related('author')

    context= {'course': course, 'posts': posts, 'form': form, 'page_title': f"Discussion for {course.title}"}
    return render(request, 'discussion/post_list.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id= post_id, parent__isnull= True)
    course = post.course

    if not can_user_access_discussion(request.user, course):
        messages.error(request, "You must enroll to view this post.")
        return redirect('courses:course_details', course_slug= course.slug)
    
    if request.method == "POST":
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            new_reply = reply_form.save(commit= False)
            new_reply.parent = post
            new_reply.course = course
            new_reply.author = request.user
            new_reply.title = f"Re: {post.title}"
            new_reply.save()
            messages.success(request, "Your reply was posted.")
            return redirect('discussion:post_detail', post_id= post.id)
        
    else:
        reply_form = ReplyForm()

    replies = post.replies.all().select_related('author')

    context= {'post':post, 'course': course, 'reply_form': reply_form, 'replies': replies, 'page_title': post.title}
    return render(request, 'discussion/post_detail.html', context)