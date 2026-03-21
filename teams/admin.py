from urllib.parse import urlencode

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import Team, MembershipApplication, Project, Achievement, Event, EventRegistration


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'created_at')
	search_fields = ('name', 'slug')


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
	list_display = (
		'full_name',
		'email',
		'team_preference',
		'status',
		'created_at',
		'accept_action',
		'reject_action',
	)
	list_filter = ('status', 'team_preference', 'created_at')
	search_fields = ('full_name', 'email', 'department', 'team_preference')
	readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by', 'admin_actions')
	fields = (
		'full_name',
		'email',
		'department',
		'year_of_study',
		'team_preference',
		'motivation',
		'status',
		'reviewed_at',
		'reviewed_by',
		'created_at',
		'admin_actions',
	)

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path(
				'<path:object_id>/accept/',
				self.admin_site.admin_view(self.accept_application),
				name='teams_membershipapplication_accept',
			),
			path(
				'<path:object_id>/reject/',
				self.admin_site.admin_view(self.reject_application),
				name='teams_membershipapplication_reject',
			),
		]
		return custom_urls + urls

	def accept_action(self, obj):
		if obj.status != 'pending':
			return '-'
		url = reverse('admin:teams_membershipapplication_accept', args=[obj.pk])
		return format_html('<a class="button" href="{}">Accept</a>', url)

	accept_action.short_description = 'Accept'

	def reject_action(self, obj):
		if obj.status != 'pending':
			return '-'
		url = reverse('admin:teams_membershipapplication_reject', args=[obj.pk])
		return format_html('<a class="button" href="{}">Reject</a>', url)

	reject_action.short_description = 'Reject'

	def admin_actions(self, obj):
		if not obj or not obj.pk or obj.status != 'pending':
			return '-'

		accept_url = reverse('admin:teams_membershipapplication_accept', args=[obj.pk])
		reject_url = reverse('admin:teams_membershipapplication_reject', args=[obj.pk])
		return format_html(
			'<a class="button" href="{}">Accept</a>&nbsp;'
			'<a class="button" href="{}">Reject</a>',
			accept_url,
			reject_url,
		)

	admin_actions.short_description = 'Actions'

	def accept_application(self, request, object_id):
		application = get_object_or_404(MembershipApplication, pk=object_id)

		if application.status != 'pending':
			self.message_user(request, 'This application has already been reviewed.', level=messages.WARNING)
			return redirect('admin:teams_membershipapplication_changelist')

		user = self._get_or_create_user_from_application(application)
		application.status = 'accepted'
		application.reviewed_at = timezone.now()
		application.reviewed_by = request.user
		application.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])

		self._send_acceptance_email(application, user)
		self.message_user(request, f'Application accepted for {application.email}.', level=messages.SUCCESS)
		return redirect('admin:teams_membershipapplication_changelist')

	def reject_application(self, request, object_id):
		application = get_object_or_404(MembershipApplication, pk=object_id)

		if application.status != 'pending':
			self.message_user(request, 'This application has already been reviewed.', level=messages.WARNING)
			return redirect('admin:teams_membershipapplication_changelist')

		application.status = 'rejected'
		application.reviewed_at = timezone.now()
		application.reviewed_by = request.user
		application.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])

		self._send_rejection_email(application)
		self.message_user(request, f'Application rejected for {application.email}.', level=messages.SUCCESS)
		return redirect('admin:teams_membershipapplication_changelist')

	def _get_or_create_user_from_application(self, application):
		UserModel = get_user_model()

		first_name, last_name = self._split_name(application.full_name)
		defaults = {
			'email': application.email,
			'first_name': first_name,
			'last_name': last_name,
			'is_active': True,
		}

		username_field = getattr(UserModel, 'USERNAME_FIELD', 'username')
		if username_field == 'email':
			lookup = {'email': application.email}
		else:
			defaults.setdefault('username', application.email)
			lookup = {'email': application.email}

		user, created = UserModel.objects.get_or_create(**lookup, defaults=defaults)

		changed_fields = []
		if not created:
			if hasattr(user, 'first_name') and not user.first_name:
				user.first_name = first_name
				changed_fields.append('first_name')
			if hasattr(user, 'last_name') and not user.last_name:
				user.last_name = last_name
				changed_fields.append('last_name')
			if hasattr(user, 'is_active') and not user.is_active:
				user.is_active = True
				changed_fields.append('is_active')

		if hasattr(user, 'department') and not user.department:
			user.department = application.department
			changed_fields.append('department')
		if hasattr(user, 'year_of_study') and not user.year_of_study:
			user.year_of_study = application.year_of_study
			changed_fields.append('year_of_study')
		if hasattr(user, 'approval_status'):
			user.approval_status = 'approved'
			changed_fields.append('approval_status')

		if created:
			user.set_unusable_password()
			user.save()
		elif changed_fields:
			user.save(update_fields=list(set(changed_fields)))

		return user

	def _split_name(self, full_name):
		parts = (full_name or '').strip().split()
		if not parts:
			return 'Member', 'User'
		if len(parts) == 1:
			return parts[0], 'User'
		return parts[0], ' '.join(parts[1:])

	def _send_acceptance_email(self, application, user):
		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)

		frontend_url = getattr(settings, 'FRONTEND_SET_PASSWORD_URL', '').strip()
		if not frontend_url:
			frontend_url = 'http://localhost:3000/set-password'

		query = urlencode({'uid': uid, 'token': token, 'email': application.email})
		set_password_link = f'{frontend_url}?{query}'

		send_mail(
			subject='Your membership application was accepted',
			message=(
				f'Hi {application.full_name},\n\n'
				'Your membership application has been accepted.\n'
				'Use the link below to set your password and activate your account:\n'
				f'{set_password_link}\n\n'
				'If you did not request this, please ignore this email.'
			),
			from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
			recipient_list=[application.email],
			fail_silently=False,
		)

	def _send_rejection_email(self, application):
		send_mail(
			subject='Your membership application update',
			message=(
				f'Hi {application.full_name},\n\n'
				'Thank you for applying. After review, we are unable to approve your '
				'membership application at this time.\n\n'
				'You are welcome to apply again in the future.'
			),
			from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
			recipient_list=[application.email],
			fail_silently=False,
		)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'team', 'created_at')
	search_fields = ('title', 'description')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	list_display = ('title', 'team', 'date')
	search_fields = ('title', 'description')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'date', 'location')
	search_fields = ('title', 'description', 'location')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'email', 'event', 'created_at')
	search_fields = ('full_name', 'email')
