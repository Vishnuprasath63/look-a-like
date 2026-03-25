import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Celebrity, MatchResult
from .services import find_celebrity_matches, validate_face_image


def home_view(request):
    """Landing page — public."""
    recent_count = MatchResult.objects.count()
    celebrity_count = Celebrity.objects.count()
    return render(request, 'matcher/home.html', {
        'recent_count': recent_count,
        'celebrity_count': celebrity_count,
    })


@login_required
def upload_view(request):
    """Image upload page."""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('face_image')

        if not uploaded_file:
            messages.error(request, 'Please select an image to upload.')
            return render(request, 'matcher/upload.html')

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        if uploaded_file.content_type not in allowed_types:
            messages.error(request, 'Please upload a JPG, PNG, or WebP image.')
            return render(request, 'matcher/upload.html')

        # Validate file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'Image size must be under 10MB.')
            return render(request, 'matcher/upload.html')

        # Create MatchResult to save the uploaded image
        match_result = MatchResult(user=request.user)
        match_result.uploaded_image = uploaded_file
        match_result.save()

        # Validate face in image
        is_valid, face_message = validate_face_image(match_result.uploaded_image.path)

        if not is_valid:
            match_result.delete()
            messages.error(request, face_message)
            return render(request, 'matcher/upload.html')

        # Find celebrity matches
        celebrities = Celebrity.objects.all()

        if not celebrities.exists():
            match_result.delete()
            messages.warning(request, 'No celebrities in database yet. Please run the seed command first.')
            return render(request, 'matcher/upload.html')

        match_results = find_celebrity_matches(
            user_image_path=match_result.uploaded_image.path,
            celebrities=celebrities,
            top_n=10,
        )

        if match_results:
            match_result.set_results(match_results)
            match_result.top_match_name = match_results[0]['name']
            match_result.top_match_score = match_results[0]['similarity']
            match_result.save()
            return redirect('results', match_id=match_result.id)
        else:
            match_result.delete()
            messages.error(request, 'Could not process the image. Please try a different photo.')
            return render(request, 'matcher/upload.html')

    return render(request, 'matcher/upload.html')


@login_required
def results_view(request, match_id):
    """Display match results."""
    match_result = get_object_or_404(MatchResult, id=match_id, user=request.user)
    results = match_result.get_results()
    top_result = results[0] if results else None
    other_results = results[1:] if len(results) > 1 else []

    return render(request, 'matcher/results.html', {
        'match_result': match_result,
        'top_result': top_result,
        'other_results': other_results,
    })


@login_required
def history_view(request):
    """User's match history."""
    matches = MatchResult.objects.filter(user=request.user)[:20]
    return render(request, 'matcher/history.html', {
        'matches': matches,
    })
