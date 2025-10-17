from django.core.mail import EmailMessage
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from utils.email import EmailThread
from utils.jwt_token import token_generator

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    This serializer creates a new user & sends email verification code
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"error": "The passwords do not match"})

        try:
            validate_password(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"error": e.messages})

        return attrs

    def create(self, validated_attrs):
        email = validated_attrs.get("email").lower()
        username = validated_attrs.get("username")

        user = User.objects.filter(email=email).first()

        if user:
            if not user.is_active:
                raise serializers.ValidationError({"error": "Your account is inactive"})
            else:
                raise serializers.ValidationError({"error": "Email already registered"})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"error": "Username already taken"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_attrs["password"],
        )

        # Generate a jwt token for confirm email
        token = token_generator(user)
        FRONTEND_URL = "http://localhost:3000"

        confirm_url = f"{FRONTEND_URL}/auth/verified/{token['access']}"
        msg = f"For confirm email click on: {confirm_url}"
        email_obj = EmailMessage("Confirm email", msg, to=[email])
        EmailThread(email_obj).start()

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "confirm_password")



class ResendEmailVerificationSerializer(serializers.Serializer):
    """This serializer resend email verification code"""

    email = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User does not exist!"})
        if user.is_verified:
            raise serializers.ValidationError({"error": "Email already verified"})
        # Adding the user field to attrs to be captured in the resend email confirmation view to prevent re-query
        attrs["user"] = user
        return super().validate(attrs)




class ResetPasswordSerializer(serializers.Serializer):
    """Reset user password"""

    email = serializers.EmailField(required=True)


class SetPasswordSerializer(serializers.Serializer):
    """Set user password after reset password"""

    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")
        # If new password & confirm new password are not match
        if new_password != confirm_new_password:
            raise serializers.ValidationError({"error": "The passwords do not match"})

        # validate password complexity
        try:
            validate_password(new_password)
        # password is not strong
        except serializers.ValidationError:
            raise serializers.ValidationError()

        return super().validate(attrs)


