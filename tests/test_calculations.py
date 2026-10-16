import pytest
from app.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds

# python file name must start with "test_" in order to pytest auto discovery to find the file
# function naming should also start with "test_" in order for pytest to recognise them as tests

# fixtures are functions that are called at the start of a testing function, used when you want to initialise a class before each test. 
# Saves repeating initlization code inside each test.
@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(100)


@pytest.mark.parametrize("num1, num2, expected", [
    (5, 3, 8), 
    (7, 1, 8), 
    (10, 2, 12), 
    (50, 7, 57)
])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(2, 3) == 6

def test_divide():
    assert divide(20, 5) == 4

# test bank account class
@pytest.mark.parametrize("balance", [10, 20, 50, 100, 1000, 50000])
def test_bank_set_initial_amount(balance):
    bank_account = BankAccount(balance)
    assert bank_account.balance == balance

def test_bank_default_amount():
    acc = BankAccount()
    assert acc.balance == 0


def test_bank_withdraw(bank_account):
    bank_account.withdraw(10)
    assert bank_account.balance == 90

def test_bank_deposit(bank_account):
    bank_account.deposit(50)
    assert bank_account.balance == 150

def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 3) == 110

@pytest.mark.parametrize("deposit, withdraw, balance", [
    (50, 25, 125),
    (100, 50, 150), 
    (80, 30, 150),
    (250, 50, 300),
    (1000, 200, 900)
])
def test_bank_transaction(bank_account, deposit, withdraw, balance):
    bank_account.deposit(deposit)
    bank_account.withdraw(withdraw)
    assert bank_account.balance == balance


# an example of how you test for a test case where you expect a aparticular type of error
def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(250)
