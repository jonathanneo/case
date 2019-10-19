from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from ..models import Tag, TagRelationship, CaseStudy, MedicalHistory, Medication, Attempt, Comment, Other, Question, Playlist
from ..forms import PlaylistTagForm



@login_required
def playlist_landing(request):
    playlists = Playlist.objects.filter(owner=request.user)
    form = PlaylistTagForm()
    c = {
        "playlists": playlists,
        "form": form
    }
    return render(request, "playlist_landing.html", c)
