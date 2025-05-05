from django.db import models

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
