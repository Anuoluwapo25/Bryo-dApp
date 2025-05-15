from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PaymentSettings(models.Model):    
    """Singleton model to store payment link settings"""
    success_message = models.TextField(default="Thank you for your payment!")    
    inactive_message = models.TextField(default="This payment link is no longer active.", blank=True)    
    redirect_url = models.URLField(default="", blank=True)    
    branding_image = models.ImageField(upload_to='payment_branding/', blank=True, null=True)    
    payment_limit = models.PositiveIntegerField(default=0, blank=True, help_text="0 means unlimited")
    
    def save(self, *args, **kwargs):
        self.pk = 1  
        super().save(*args, **kwargs)        

    @classmethod  
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta: 
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"



class PrivyUser(models.Model):
    privy_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.wallet_address or self.privy_id
    
class WaitList(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Event(models.Model):
    EVENT_VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    name = models.CharField()
    day = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    virtual_link = models.URLField(blank=True, null=True)
    ticket_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    capacity = models.IntegerField(blank=False, null=True)
    transferable = models.BooleanField(default=False)
    event_image = models.ImageField(
        upload_to='event_images/', 
        null=True, 
        blank=True
    )
    visibility = models.CharField(max_length=10, choices=EVENT_VISIBILITY_CHOICES, default='public')
    timezone = models.CharField(
        max_length=50, 
        default='GMT+0:00 Lagos'
    )
    created_at = models.DateTimeField(auto_now_add=True)



class EventTicket(models.Model):
    """
    Represents a ticket for a specific event
    """
    TICKET_STATUS_CHOICES = [
        ('active', 'Active'),
        ('transferred', 'Transferred'),
        ('used', 'Used'),
        ('cancelled', 'Cancelled')
    ]
    
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tickets')
    original_owner = models.ForeignKey(PrivyUser, on_delete=models.CASCADE, related_name='original_tickets')
    current_owner = models.ForeignKey(PrivyUser, on_delete=models.CASCADE, related_name='current_tickets')
        
    status = models.CharField(
        max_length=20, 
        choices=TICKET_STATUS_CHOICES, 
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_transferred_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'current_owner') 
    
    def __str__(self):
        return f"Ticket for {self.event.name} - {self.ticket_code}"
    

class TicketTransfer(models.Model):
    """
    Tracks ticket transfer transactions
    """
    TRANSFER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    ticket = models.ForeignKey(EventTicket, on_delete=models.CASCADE, related_name='transfers')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers')
    
    transfer_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=TRANSFER_STATUS_CHOICES, 
        default='pending'
    )
    
    blockchain_transaction_hash = models.CharField(
        max_length=100, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"Transfer of {self.ticket} from {self.sender} to {self.recipient}"
    
