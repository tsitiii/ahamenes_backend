from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers


class SetPasswordSerializer(serializers.Serializer):
	uid = serializers.CharField()
	token = serializers.CharField()
	email = serializers.EmailField()
	password = serializers.CharField(write_only=True, min_length=8)

	def validate(self, attrs):
		uid = attrs.get('uid')
		token = attrs.get('token')

		try:
			user_id = force_str(urlsafe_base64_decode(uid))
			user = get_user_model().objects.get(pk=user_id)
		except Exception as exc:
			raise serializers.ValidationError({'uid': 'Invalid user identifier.'}) from exc

		if not default_token_generator.check_token(user, token):
			raise serializers.ValidationError({'token': 'Invalid or expired token.'})

		email = (attrs.get('email') or '').strip().lower()
		if user.email.strip().lower() != email:
			raise serializers.ValidationError({'email': 'Email does not match this password setup link.'})

		attrs['user'] = user
		return attrs

	def save(self, **kwargs):
		user = self.validated_data['user']
		password = self.validated_data['password']

		user.set_password(password)

		update_fields = []
		if hasattr(user, 'is_active'):
			user.is_active = True
			update_fields.append('is_active')
		if hasattr(user, 'approval_status'):
			user.approval_status = 'approved'
			update_fields.append('approval_status')

		if update_fields:
			user.save(update_fields=update_fields + ['password'])
		else:
			user.save(update_fields=['password'])

		return user
