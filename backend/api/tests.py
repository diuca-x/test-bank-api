from django.test import TestCase
import requests
from bank_account.models import Account,Transactions
# Create your tests here.
import random
import json
url = "http://localhost:8000/api/"

class TestBasic(TestCase): 
    url = url + "get-statement"
    def setUp(self):
        Account.objects.create(current_balance=100)
    def test_can_get_statement(self):
        response = self.client.post(self.url)
        assert response.status_code == 204

class TestDeposit(TestCase):
    url = url + "deposit"
    def setUp(self):
        Account.objects.create(current_balance=100)

    def test_deposit_success(self):
        response = self.client.post(self.url,data={"amount":100})
        assert response.status_code == 201

        assert (Transactions.objects.first().balance_at_time and Transactions.objects.first().operation == "deposit" and Account.objects.first().current_balance == 200)
        assert Transactions.objects.first().amount >= 0

    def test_deposit_error_string(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":"asd"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_deposit_error_extra(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":100,"unexpected":"key"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
    
    def test_deposit_error_missing(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
        
    def test_deposit_error_null(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data=json.dumps({"amount":None}),content_type='application/json')
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

class TestWithdraw(TestCase):
    url = url + "withdraw"
    def setUp(self):
        Account.objects.create(current_balance=10000)

    def test_withdraw_success(self):
        response = self.client.post(self.url,data={"amount":100})
        assert response.status_code == 201

        assert Transactions.objects.first().balance_at_time == 10000-100
        assert Transactions.objects.first().operation == "withdraw" 
        assert Account.objects.first().current_balance == 10000-100
        assert Transactions.objects.first().amount <= 0
    
    def test_withdraw_error_insufficient_fund(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":9999999999})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_withdraw_error_negative(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":-50})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_withdraw_error_string(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":"money"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_withdraw_error_extra_key(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":100,"unexpected":"key"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_withdraw_error_missing_key(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
    
    def test_withdraw_error_null_value(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data=json.dumps({"amount":None}),content_type='application/json')
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

class TestTransfer(TestCase):
    url = url + "transfer"
    def setUp(self):
        Account.objects.create(current_balance=10000)

    def test_transfer_success(self):
        response = self.client.post(self.url,data={"amount":100,"account":"GB24BARC20201630093459"})
        assert response.status_code == 201

        assert Transactions.objects.first().balance_at_time == 10000-100
        assert Transactions.objects.first().operation == "transfer" 
        assert Account.objects.first().current_balance == 10000-100
        assert Transactions.objects.first().amount <= 0
    
    def test_transfer_error_insufficient_fund(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":9999999999,"account":"GB24BARC20201630093459"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_transfer_error_string(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":"money","account":"GB24BARC20201630093459"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
    
    def test_transfer_error_extra_key(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"amount":"money","account":"GB24BARC20201630093459","unexpected":"key"})
        
        assert response.status_code == 400
        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
    
    def test_transfer_error_missing_keys(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data={"account":"GB24BARC20201630093459"})
        assert response.status_code == 400

        response = self.client.post(self.url,data={"amount":100})
        assert response.status_code == 400

        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_transfer_error_null(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        response = self.client.post(self.url,data=json.dumps({"amount":None,"account":"GB24BARC20201630093459"}),content_type='application/json')
        assert response.status_code == 400
        
        response = self.client.post(self.url,data=json.dumps({"amount":100,"account":None}),content_type='application/json')
        assert response.status_code == 400

        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_transfer_invalid_iban(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        
        response = self.client.post(self.url,data={"amount":100,"account":"random"})
        assert response.status_code == 400

        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount
    
    def test_transfer_empty_json(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        
        response = self.client.post(self.url,data={})
        assert response.status_code == 400

        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount

    def test_transfer_empty_json(self):
        transaction_number = len(Transactions.objects.all())
        previous_amount = Account.objects.first().current_balance
        
        
        response = self.client.post(self.url,data={"amount":-50,"account":"GB24BARC20201630093459"})
        assert response.status_code == 400

        assert len(Transactions.objects.all()) == transaction_number
        assert Account.objects.first().current_balance == previous_amount


class TestGetStatement(TestCase):
    url = url + "get-statement"

    def setUp(self):
        Account.objects.create(current_balance=99999999999)   
        for i in range (0,5):
            self.client.post(url+"transfer",data={"amount":random.uniform(1,150),"account":"GB24BARC20201630093459"})
            self.client.post(url+"deposit",data={"amount":random.uniform(1,150)})
            self.client.post(url+"withdraw",data={"amount":random.uniform(1,150)})

        assert len(Transactions.objects.all()) == 15

    def test_can_get_statement(self):
        response = self.client.post(self.url)
        assert response.status_code == 200

    def test_can_filter_operation(self):
        response = self.client.post(self.url,data={"operation_type": "deposit"})

        results = response.json().get("data")
        for i in results:
            assert i.get("operation") == "deposit"

        response = self.client.post(self.url,data={"operation_type": "withdraw"})

        results = response.json().get("data")
        for i in results:
            assert i.get("operation") == "withdraw"

        response = self.client.post(self.url,data={"operation_type": "transfer"})

        results = response.json().get("data")
        
        for i in results:
            assert i.get("operation") == "transfer"
    
    def test_can_order(self):
        first_transaction = Transactions.objects.first()
        last_transaction = Transactions.objects.order_by("date").first()

        response = self.client.post(self.url,data={"order": "asc"})

        results = response.json().get("data")
        
        first = results[0]
        last = results[-1]

        assert first_transaction.amount == first.get("amount") 
        assert first_transaction.balance_at_time == first.get("balance_at_time") 
        assert str(first_transaction.date.date()) == first.get("date") 
        assert first_transaction.operation == first.get("operation") 

        """ assert last_transaction.amount == last.get("amount") 
        assert last_transaction.balance_at_time == last.get("balance_at_time") 
        assert str(last_transaction.date.date()) == last.get("date") 
        assert last_transaction.operation == last.get("operation")  """

        

        