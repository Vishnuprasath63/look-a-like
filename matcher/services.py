"""
Face Matching Service
Uses DeepFace to compare user-uploaded images against celebrity database.
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def find_celebrity_matches(user_image_path, celebrities, top_n=10):
    """
    Compare a user's face against all celebrities and return top matches.
    
    Args:
        user_image_path: Absolute path to the user's uploaded image
        celebrities: QuerySet of Celebrity objects
        top_n: Number of top matches to return
    
    Returns:
        list of dicts: [{celebrity_id, name, category, similarity, image_url}, ...]
    """
    try:
        from deepface import DeepFace
    except ImportError:
        logger.error("DeepFace is not installed. Run: pip install deepface")
        return []

    results = []

    for celebrity in celebrities:
        celeb_image_path = celebrity.image.path

        if not os.path.exists(celeb_image_path):
            logger.warning(f"Celebrity image not found: {celeb_image_path}")
            continue

        try:
            # Use DeepFace.verify to compare two faces
            result = DeepFace.verify(
                img1_path=str(user_image_path),
                img2_path=str(celeb_image_path),
                model_name="VGG-Face",
                detector_backend="opencv",
                enforce_detection=False,
                silent=True,
            )

            # Convert distance to similarity percentage
            # VGG-Face uses cosine distance by default (0 = identical, 1 = different)
            distance = result.get("distance", 1.0)
            threshold = result.get("threshold", 0.40)

            # Calculate similarity as a percentage (higher = more similar)
            # Using a sigmoid-like mapping for better distribution
            if distance <= 0:
                similarity = 100.0
            elif distance >= 1.0:
                similarity = 0.0
            else:
                # Map distance to percentage: 0 -> 100%, threshold -> ~70%, 1 -> 0%
                similarity = max(0, min(100, (1 - distance) * 100))

            results.append({
                'celebrity_id': celebrity.id,
                'name': celebrity.name,
                'category': celebrity.get_category_display(),
                'similarity': round(similarity, 1),
                'image_url': celebrity.image.url,
                'description': celebrity.description,
            })

        except Exception as e:
            logger.warning(f"Error comparing with {celebrity.name}: {str(e)}")
            continue

    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)

    return results[:top_n]


def validate_face_image(image_path):
    """
    Validate that the uploaded image contains a detectable face.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from deepface import DeepFace

        faces = DeepFace.extract_faces(
            img_path=str(image_path),
            detector_backend="opencv",
            enforce_detection=False,
        )

        if not faces:
            return False, "No face detected in the image. Please upload a clear photo of your face."

        # Check face confidence
        high_confidence_faces = [f for f in faces if f.get('confidence', 0) > 0.5]

        if not high_confidence_faces:
            return False, "Could not clearly detect a face. Please upload a well-lit, front-facing photo."

        if len(high_confidence_faces) > 1:
            return True, "Multiple faces detected. The primary face will be used for matching."

        return True, "Face detected successfully!"

    except Exception as e:
        logger.error(f"Face validation error: {str(e)}")
        return True, "Image accepted. Processing will attempt face detection."
