# from django.urls import reverse
# from django.contrib import messages
from django.shortcuts import redirect, render
# from profiles.models import Profile
from wallet.models import Account, Transaction
# from django.views.generic.list import ListView 
from django.db import transaction
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from authentication.models import User

@login_required
def earnings_view(request):
    account = Account.objects.filter(user = request.user).first()
    all_transactions = Transaction.objects.filter(account = account)
    context = {}
    summary = {
        "balance": 0,
        "withdrawn": 0,
        "used_for_subs": 0,
        "income": 0
    }

    if len(all_transactions) > 0:
        balance = account.balance()
        # withdrawn_query = all_transactions.filter(is_debit = True)
        # withdrawn_sum = withdrawn_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

        # used_form_subs_query = all_transactions.filter(is_debit = True, subscription__isnull = False) 
        # used_form_subs_sum = used_form_subs_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

        expenses_query = all_transactions.filter(is_debit = True)
        expenses_sum = expenses_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

        netincome_query = all_transactions.filter(is_credit = True)
        netincome_sum = netincome_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

        summary['balance'] = balance
        # summary['withdrawn'] = int(withdrawn_sum) if withdrawn_sum else 0
        # summary['used_for_subs'] = int(used_form_subs_sum) if used_form_subs_sum else 0
        summary['income'] = int(netincome_sum) if netincome_sum else 0
        summary['expenses'] = int(expenses_sum) if expenses_sum else 0
        context['wallet_summary'] = summary
        context['all_transactions'] = all_transactions

    return render(request, "transactions.html", context)


# # Create your views here.
# @login_required
# def wallet_topup(request):
#     context = {}
#     if request.method == "POST":
#         qty = request.POST.get("coins_qty")
#         qty = int(qty) if qty else qty
#         if not qty:
#             messages.error(request, "Given coins quantity is invalid")
#         elif qty > 2000:
#             context["coins_qty"] = qty
#             messages.error(request, "You can buy at most 2000 coins at a time")
#         else:
#             try:
#                 with transaction.atomic():
#                     profile = Profile.objects.get(user = request.user)
#                     account = profile.getAccount()
#                     account.credit(
#                         amount = qty,
#                         source = "Card",
#                         note = "Coins bought by paying through card",
#                         is_buy = True
#                     )
#                     messages.success(request, "Coins have been added in your metavid account")
#             except Exception as e:
#                 messages.error(request, str(e))            

#     return redirect(reverse("wallet:index", kwargs=context))


# class WalletList(ListView): 
#     template_name = "coin_history.html"
#     model = Transaction
#     extra_context={'page': "wallet"}

#     def get_context_data(self, **kwargs):
#         context = super(WalletList, self).get_context_data(**kwargs)
#         all_transactions = context["object_list"]
#         print(all_transactions)
#         summary = {
#             "balance": 0,
#             "withdrawn": 0,
#             "used_for_subs": 0,
#             "income": 0
#         }
#         if len(all_transactions) > 0:
#             balance = all_transactions[0].account.balance()
#             withdrawn_query = all_transactions.filter(is_debit = True, is_withdrawn = True, subscription__isnull = True)
#             withdrawn_sum = withdrawn_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

#             used_form_subs_query = all_transactions.filter(is_debit = True, subscription__isnull = False) 
#             used_form_subs_sum = used_form_subs_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

#             netincome_query = all_transactions.filter(is_credit = True) 
#             netincome_sum = netincome_query.aggregate(Sum("signed_amount"))['signed_amount__sum']

#             summary['balance'] = balance
#             summary['withdrawn'] = int(withdrawn_sum) if withdrawn_sum else 0
#             summary['used_for_subs'] = int(used_form_subs_sum) if used_form_subs_sum else 0
#             summary['income'] = int(netincome_sum) if netincome_sum else 0
#             context['wallet_summary'] = summary

#         return context

#     def get_queryset(self):
#         profile = Profile.objects.get(user = self.request.user) 
#         queryset = Transaction.objects.filter(account = profile.getAccount())
        # if self.request.GET.get("browse"):
        #     selection = self.request.GET.get("browse")
        #     if selection == "Cats":
        #         queryset = Cats.objects.all()
        #     elif selection == "Dogs":
        #         queryset = Dogs.objects.all()
        #     elif selection == "Worms":
        #         queryset = Worms.objects.all()
        #     else:
        #         queryset = Cats.objects.all()
        # return queryset