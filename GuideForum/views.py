from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from . import models
from .forms import TopicForm, EntryForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, "index.html")


def topics(request):
    topics = models.Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'topics.html', context)


def topic(request, topic_id):
    topic = models.Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'topic.html', context)


@login_required
def like_topic(request, topic_id):
    if request.method == 'POST':
        topic = get_object_or_404(models.Topic, id=topic_id)
        if request.user in topic.likes.all():
            topic.likes.remove(request.user)
            topic.rating -= 1
        else:
            topic.likes.add(request.user)
            topic.rating += 1
        topic.save()
        return redirect('topic', topic_id=topic_id)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def new_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()

            tags_str = form.cleaned_data['tags']
            tags_str = tags_str.strip('[]')
            tags_str = tags_str.replace("'", "")
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

            for tag_name in tags:
                tag, _ = models.Tag.objects.get_or_create(name=tag_name)
                new_topic.tags.add(tag)

            return HttpResponseRedirect(reverse('topics'))
    else:
        form = TopicForm()

    context = {'form': form}
    return render(request, 'new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    topic = models.Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('topic', args=[topic_id]))
    context = {'topic': topic, 'form': form}
    return render(request, 'new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = models.Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('topic', args=[topic.id]))
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'edit_entry.html', context)


@login_required
def my_topics(request):
    topics = models.Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'topics.html', context)


@login_required()
def user_profile(request, user_id):
    user_profile = models.UserProfile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            user_profile.profile_picture = profile_picture
            user_profile.save()
    context = {'user_profile': user_profile}
    return render(request, 'user_profile.html', context)