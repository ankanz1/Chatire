"""Views for the chat app."""

from django.contrib.auth import get_user_model
from .models import (
    ChatSession, ChatSessionMember, ChatSessionMessage, deserialize_user
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.http import Http404


def raise_404(request):
    """Raise a 404 Error."""
    raise Http404

from notifications.signals import notify


class ChatSessionView(APIView):
    """Manage Chat sessions."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """Return all chat sessions the user belongs to."""
        user = request.user

        # Sessions where user is owner
        owned = ChatSession.objects.filter(owner=user)
        # Sessions where user is a member
        joined_ids = ChatSessionMember.objects.filter(user=user).values_list(
            'chat_session_id', flat=True
        )
        joined = ChatSession.objects.filter(id__in=joined_ids)

        all_sessions = (owned | joined).distinct().order_by('-create_date')

        sessions_data = [
            {
                'uri': s.uri,
                'created_at': s.create_date.isoformat(),
                'is_owner': s.owner == user,
            }
            for s in all_sessions
        ]
        return Response({'sessions': sessions_data})

    def post(self, request, *args, **kwargs):
        """create a new chat session."""
        user = request.user

        chat_session = ChatSession.objects.create(owner=user)

        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri,
            'message': 'New chat session created'
        })

    def patch(self, request, *args, **kwargs):
        """Add a user to a chat session."""
        User = get_user_model()

        uri = kwargs['uri']
        username = request.data['username']
        user = User.objects.get(username=username)

        chat_session = ChatSession.objects.get(uri=uri)
        owner = chat_session.owner

        if owner != user:  # Only allow non owners join the room
            chat_session.members.get_or_create(
                user=user, chat_session=chat_session
            )

        owner = deserialize_user(owner)
        members = [
            deserialize_user(chat_session.user) 
            for chat_session in chat_session.members.all()
        ]
        members.insert(0, owner)  # Make the owner the first member 
        return Response ({
            'status': 'SUCCESS', 'members': members,
            'message': '%s joined the chat' % user.username,
            'user': deserialize_user(user)
        })
    


class ChatSessionMessageView(APIView):
    """Create/Get Chat session messages."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """return all messages in a chat session."""
        uri = kwargs['uri']

        chat_session = ChatSession.objects.get(uri=uri)
        messages = [chat_session_message.to_json() 
            for chat_session_message in chat_session.messages.all()]

        return Response({
            'id': chat_session.id, 'uri': chat_session.uri,
            'messages': messages
        })

    def post(self, request, *args, **kwargs):
        """create a new message in a chat session."""
        uri = kwargs['uri']
        message = request.data['message']

        user = request.user
        chat_session = ChatSession.objects.get(uri=uri)

        chat_session_message = ChatSessionMessage.objects.create(
            user=user, chat_session=chat_session, message=message
        )

        notif_args = {
            'source': user,
            'source_display_name': user.get_full_name(),
            'category': 'chat', 'action': 'Sent',
            'obj': chat_session_message.id,
            'short_description': 'You a new message', 'silent': True,
            'extra_data': {
                'uri': chat_session.uri,
                'message': chat_session_message.to_json()
            }
        }
        notify.send(
            sender=self.__class__, **notif_args, channels=['websocket']
        )

        return Response ({
            'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
            'user': deserialize_user(user)
        })


class TypingView(APIView):
    """Broadcast a typing event to all users in a chat session."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """Publish a typing signal to the room's RabbitMQ exchange."""
        uri = kwargs['uri']
        user = request.user

        typing_payload = {
            '__typing__': True,
            'user': deserialize_user(user),
        }
        notif_args = {
            'source': user,
            'source_display_name': user.get_full_name(),
            'category': 'chat', 'action': 'Typing',
            'obj': 0,
            'short_description': '', 'silent': True,
            'extra_data': {
                'uri': uri,
                'message': typing_payload
            }
        }
        notify.send(
            sender=self.__class__, **notif_args, channels=['websocket']
        )
        return Response({'status': 'OK'})
