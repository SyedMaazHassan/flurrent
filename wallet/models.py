from django.db import models
import uuid
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver


class Account(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, null=True, blank = True)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, null=True, blank = True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.title} - {self.account_id}' 

    def is_enough_balance(self, required_amount):
        current_balance = self.balance_num()
        return current_balance >= required_amount

    def balance_num(self):
        all_transaction_of_account = Transaction.objects.filter(account = self)
        agg_sum = all_transaction_of_account.aggregate(Sum("signed_amount"))
        agg_sum = agg_sum['signed_amount__sum'] if agg_sum['signed_amount__sum'] else 0
        return agg_sum

    def balance(self):
        acc_balance = self.balance_num()
        return int(acc_balance)

    def add_transaction(self, order, amount, source, note, is_credit = False, is_debit = False):
        if is_debit == is_credit:
            raise Exception("Transaction can't be added")
        signed_amount = amount if is_credit else amount*-1
        new_transaction = Transaction.objects.create(
            amount = amount,
            signed_amount = signed_amount,
            is_credit = is_credit,
            is_debit = is_debit,
            source = source,
            note = note,
            account = self,
            order = order
        )
        return new_transaction

    def credit(self, order, amount, source, note):
        print("Amount to be credited into account")
        return self.add_transaction(order=order, amount=amount, source=source, note=note, is_credit=True)

    def debit(self, order, amount, source, note):
        if self.is_enough_balance(amount):
            print("Amount to be debited from account")
            return self.add_transaction(order=order, amount=amount, source=source, note=note, is_debit=True)
        
        raise Exception("Wallet Topup required to do this transaction. Add balance by the option below.")

    def save(self, *args, **kwargs):
        if not (self.pk or self.user):
            raise Exception("Account can't be created")
        super(Account, self).save(*args, **kwargs)


@receiver(post_save, sender="authentication.User")
def create_account(sender, instance, created, **kwargs):
    if created:
        print(instance)
        try:
            name = instance.getFullName()
            with transaction.atomic():
                account = Account.objects.create(
                    title = name, 
                    user = instance
                )
                account.credit(None, 500, "System", "Free credit provided by the system")
                print(f"{name}'s account has been created")
        except:
            print("something went wrong")
            # instance.delete()
            raise Exception("Error while creating the account. Try registering the user again.")

    else:
        print("nothing works")



class Transaction(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.FloatField()
    signed_amount = models.FloatField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    is_credit = models.BooleanField(default=False)
    is_debit = models.BooleanField(default=False)
    source = models.CharField(max_length=255)
    order = models.ForeignKey('endorsers.Order', on_delete=models.CASCADE, null=True, blank=True)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def getAmount(self):
        return int(self.amount)

    # def getTransactionCardTitle(self):
    #     if self.is_buy:
    #         return self.account.title

    #     if not self.subscription:
    #         return "Metavid"
    #     name = None
    #     if self.is_credit:
    #         name = self.subscription.consumer.getAccount().title
    #     else:
    #         name = self.subscription.creator.user.getAccount().title
    #     return name

    # def getProfileIcon(self):
    #     if self.is_buy:
    #         return "https://thumbs.dreamstime.com/b/credit-card-illustration-front-back-view-vector-eps-190373102.jpg"
    #     if not self.subscription:
    #         return "https://i.pinimg.com/474x/5e/2f/81/5e2f81487ffda9e12292f7ebe2a0adf0.jpg"
    #     icon = None
    #     if self.is_credit:
    #         icon = self.subscription.consumer.profile_picture.url
    #     else:
    #         icon = self.subscription.creator.user.profile_picture.url
    #     return icon

    class Meta:
        ordering = ("-created_at",)
