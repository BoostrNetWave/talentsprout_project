from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from studentPost.forms import BlogPostForm , BlogImageForm, CandidatePreferenceForm# Assuming you already have this form
from studentPost.models import BlogPost, CandidatePreference, BlogImage # Your blog model
from django.core.paginator import Paginator
from profiles.models import UserProfile
from django.contrib.auth.models import Group
# # Helper function to check if the user is an admin
# def is_admin_user(user):
#     return user.is_superuser or user.groups.filter(name='admin').exists()

# # View for admin to create blog post
# @login_required
# @user_passes_test(is_admin_user)
# def admin_create_blog_post(request):
#     if request.method == 'POST':
#         form = BlogPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             blog_post = form.save(commit=False)
#             blog_post.user = request.user
#             blog_post.save()
#             messages.success(request, 'Blog post created successfully.')
#             return redirect('admin_blog_list')  # We'll create this next
#     else:
#         form = BlogPostForm()

#     return render(request, 'admin_customization/blog/blog_create.html', {'form': form})

def is_admin_user(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

@login_required
@user_passes_test(is_admin_user)
def admin_create_blog_post(request):
    if request.method == 'POST':
        blog_post_form = BlogPostForm(request.POST)
        candidate_preference_form = CandidatePreferenceForm(request.POST)
        blog_image_form = BlogImageForm(request.POST, request.FILES)

        if blog_post_form.is_valid() and candidate_preference_form.is_valid():
            blog_post = blog_post_form.save(commit=False)
            blog_post.user = request.user
            blog_post.save()

            preference = candidate_preference_form.save(commit=False)
            preference.blog_post = blog_post
            preference.save()

            for image_file in request.FILES.getlist('image'):
                BlogImage.objects.create(blog_post=blog_post, image=image_file)

            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_blog_list')  # Change to your target view
        else:
            messages.error(request, 'There were errors in the form. Please fix them.')
    else:
        blog_post_form = BlogPostForm()
        candidate_preference_form = CandidatePreferenceForm()
        blog_image_form = BlogImageForm()

    return render(request, 'admin_customization/blog/blog_create.html', {
        'blog_post_form': blog_post_form,
        'candidate_preference_form': candidate_preference_form,
        'blog_image_form': blog_image_form
    })


# @login_required
# @user_passes_test(is_admin_user)
# def admin_blog_post_list(request):
#     blogs = BlogPost.objects.all().order_by('-publication_date')
#     return render(request, 'admin_customization/blog/admin_blog_post_list.html', {'blogs': blogs})
# @login_required
# @user_passes_test(is_admin_user)
# def admin_blog_post_list(request):
#     posts_list = BlogPost.objects.all().order_by('-publication_date')  # Fetch all posts
#     paginator = Paginator(posts_list, 12)  # Show 12 posts per page
#     page_number = request.GET.get('page', 1)  # Get the current page number from the URL
#     page_obj = paginator.get_page(page_number)
    
#     profile_image_url = None
    
#     if request.user.is_authenticated:
#         try:
#             # Get the user profile if it exists
#             user_profile = UserProfile.objects.get(user=request.user)
#             profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
#         except UserProfile.DoesNotExist:
#             # Handle the case when the user profile does not exist
#             user_profile = None
#             profile_image_url = None

#     context = {
#         'posts': page_obj,
#         'profile_image_url': profile_image_url,
#     }
#     return render(request, 'admin_customization/blog/admin_blog_post_list.html', context)


# from django.core.paginator import Paginator
# from django.contrib.auth.models import Group
# from studentPost.models import BlogPost, UserProfile

@login_required
@user_passes_test(is_admin_user)
def admin_blog_post_list(request):
    # Filter posts where user is superuser or in 'admin' group
    admin_group, _ = Group.objects.get_or_create(name='admin')

    posts_list = BlogPost.objects.filter(
        user__is_superuser=True
    ) | BlogPost.objects.filter(
        user__groups=admin_group
    )

    posts_list = posts_list.distinct().order_by('-publication_date')
    paginator = Paginator(posts_list, 12)  # 12 per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    context = {
        'posts': page_obj,
        'profile_image_url': profile_image_url,
    }
    return render(request, 'admin_customization/blog/admin_blog_post_list.html', context)



