"""
Django admin page for verified track configuration
"""

from django.contrib import admin

from verified_track_content.forms import VerifiedTrackCourseForm
from verified_track_content.models import VerifiedTrackCohortedCourse


@admin.register(VerifiedTrackCohortedCourse)
class VerifiedTrackCohortedCourseAdmin(admin.ModelAdmin):
    """Admin for enabling verified track cohorting. """
    form = VerifiedTrackCourseForm
