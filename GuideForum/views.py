from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from djangoGF import settings
from . import models
from .forms import TopicForm, EntryForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
import operator
from functools import reduce
from operator import itemgetter
import os


def index(request):
    topics = models.Topic.objects.order_by('-date_added')
    return render(request, "topics.html", {'topics': topics})


def topics(request):
    query = request.GET.get('q', '')
    tag_ids = request.GET.getlist('tag')  # Retrieve multiple tag IDs as a list
    selected_tags = [int(tag_id) for tag_id in tag_ids]  # Convert tag IDs to integers

    if query:
        search_terms = query.split()
        conditions = Q()
        for term in search_terms:
            conditions &= (Q(title__icontains=term) | Q(description__icontains=term) | Q(text__icontains=term))
        topics = models.Topic.objects.filter(conditions)
    else:
        topics = models.Topic.objects.all()

    if selected_tags:
        tags = models.Tag.objects.filter(id__in=selected_tags)
        topics = topics.filter(tags__in=tags)

    topics = topics.annotate(tag_count=Count('tags')).order_by('-tag_count', '-rating', 'date_added')
    tags = models.Tag.objects.annotate(topic_count=Count('topic')).order_by('name')

    context = {'topics': topics, 'tags': tags, 'query': query, 'selected_tags': selected_tags}
    return render(request, 'topics.html', context)


def topic(request, topic_id):
    topic = get_object_or_404(models.Topic, id=topic_id)
    entries = topic.entry_set.order_by('-date_added')

    if request.method == 'POST' and request.user.id == topic.owner_id:
        preview = request.FILES.get('preview')
        if preview:
            topic.preview = preview
            topic.save()

    can_edit = False
    if request.user.is_authenticated and request.user.id == topic.owner_id:
        can_edit = True

    context = {'topic': topic, 'entries': entries, 'can_edit': can_edit}
    return render(request, 'topic.html', context)


@login_required
def edit_topic(request, topic_id):
    topic = get_object_or_404(models.Topic, id=topic_id)
    if request.method == 'POST':
        form = TopicForm(request.POST, request.FILES, instance=topic)
        if form.is_valid():
            edited_topic = form.save(commit=False)
            edited_topic.tags.clear()  # Удаляем все текущие теги

            tags_str = form.cleaned_data['tags']
            tags_str = tags_str.strip('[]')
            tags_str = tags_str.replace("'", "")
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

            for tag_name in tags:
                tag, _ = models.Tag.objects.get_or_create(name=tag_name)
                edited_topic.tags.add(tag)

            edited_topic.save()

            return redirect('topic', topic_id=edited_topic.id)
    else:
        form = TopicForm(instance=topic)

    return render(request, 'edit_topic.html', {'form': form, 'topic': topic})


@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(models.Topic, id=topic_id)
    if request.user.id != topic.owner_id:
        raise Http404
    if request.method == 'POST':
        topic.delete()
        return redirect('topics')
    else:
        return HttpResponseNotAllowed(['POST'])


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
            new_topic.owner = models.UserProfile.objects.get(user=request.user)
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
    if topic.owner != models.UserProfile.objects.get(user=request.user):
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
    user_profile = models.UserProfile.objects.get(user=request.user)
    topics = models.Topic.objects.filter(owner=user_profile).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'topics.html', context)


@login_required()
def user_profile(request, user_id):
    user_profile = models.UserProfile.objects.get(user_id=user_id)
    topics = models.Topic.objects.filter(owner=models.UserProfile.objects.get(user=user_profile.user))
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            user_profile.profile_picture = profile_picture
            user_profile.save()
        user_description = request.POST.get('user_description')
        if user_description:
            user_profile.user_description = user_description
            user_profile.save()
    context = {'user_profile': user_profile, 'topics': topics}
    return render(request, 'user_profile.html', context)
