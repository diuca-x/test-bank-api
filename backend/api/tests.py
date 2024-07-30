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
from datetime import datetime,timedelta,timezone,date

class TestGetStatement(TestCase):
    url = url + "get-statement"

    def setUp(self):
        Account.objects.create(current_balance=99999999999)   

        Transactions.objects.create(date = datetime.today() - timedelta(days=1),amount = 100, balance_at_time = 99999999999 + 100,operation="deposit")
        Transactions.objects.create(date = datetime.today() + timedelta(days=1),amount = 100, balance_at_time = 99999999999 + 200,operation="deposit")

        for i in range (0,5):
            self.client.post(url+"transfer",data={"amount":random.uniform(1,150),"account":"GB24BARC20201630093459"})
            self.client.post(url+"deposit",data={"amount":random.uniform(1,150)})
            self.client.post(url+"withdraw",data={"amount":random.uniform(1,150)})


        assert len(Transactions.objects.all()) == 17

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

        response = self.client.post(self.url,data={"order": "asc"})

        results = response.json().get("data")
        
        for index,value in enumerate(results):
            if index+1 < len(results):
                assert results[index].get("date") <= results[index+1].get("date")

        response = self.client.post(self.url,data={"order": "desc"})

        results = response.json().get("data")
        
        for index,value in enumerate(results):
            if index+1 < len(results):
                assert results[index].get("date") >= results[index+1].get("date")

    def test_can_filter_date(self):
        today = datetime.today().strftime('%d-%m-%Y')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')


        response = self.client.post(self.url,data={"dates": [yesterday,today]})
        result = response.json()
        assert result.get("total_elements") == 16
    
    def test_can_filter_full(self):
        today = datetime.today().strftime('%d-%m-%Y')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')


        response = self.client.post(self.url,data={"dates": [yesterday,today],"order":"desc","operation_type": "deposit"})
        result = response.json()

        assert response.status_code == 200
        assert result.get("total_elements") > 1

    def test_error_extra_key(self):

        response = self.client.post(self.url,data={"dates": ["28-7-2024","30-7-2024"],"order":"desc","operation_type": "deposit","unexpected":"key"})
        
        assert response.status_code == 400
    
    def test_error_operation(self):

        response = self.client.post(self.url,data={"operation_type": "random"})
        
        assert response.status_code == 400
    
    def test_error_date_string(self):

        response = self.client.post(self.url,data={"dates": "2"})
        
        assert response.status_code == 400
    
    def test_error_date_one_array(self):

        response = self.client.post(self.url,data={"dates": ["2"]})
        
        assert response.status_code == 400
    
    def test_error_date_reversed(self):
        today = datetime.today().strftime('%d-%m-%Y')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')

        response = self.client.post(self.url,data={"dates": [today,yesterday]})
        result = response.data
        assert response.status_code == 204
        assert result.get("message") == "No transactions found."
    def test_error_order(self):

        response = self.client.post(self.url,data={"order": "asd"})
        
        assert response.status_code == 400