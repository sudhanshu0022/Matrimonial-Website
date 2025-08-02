# shaadi/context_processors.py
from .models import Message, Conversation, CustomUser

def unread_messages(request):
    if request.user.is_authenticated:
        # Get unread messages where current user is recipient
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_count': unread_count}
    return {}