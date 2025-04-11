class UserAlreadyExistsError(Exception):
    """Exceção para quando usuário já existe"""
    def __init__(self, message="Usuário já existe"):
        self.message = message
        super().__init__(self.message)

class InvalidCredentialsError(Exception):
    """Exceção para credenciais inválidas"""
    def __init__(self, message="Credenciais inválidas"):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exceção para erros de banco de dados"""
    def __init__(self, message="Erro no banco de dados"):
        self.message = message
        super().__init__(self.message)

class AccountValidationError(Exception):
    """Erros de validação de dados da conta"""
    def __init__(self, message="Erro de validação da conta"):
        self.message = message
        super().__init__(self.message)

class AccountNotFoundError(Exception):
    """Conta não encontrada"""
    def __init__(self, message="Conta não encontrada"):
        self.message = message
        super().__init__(self.message)

class AccountOwnershipError(Exception):
    """Conta não pertence ao usuário"""
    def __init__(self, message="Conta não pertence ao usuário"):
        self.message = message
        super().__init__(self.message)

class DuplicateAccountError(Exception):
    """Conta duplicada (nome já existe)"""
    def __init__(self, message="Nome da conta já existe"):
        self.message = message
        super().__init__(self.message)

class CreditAccountError(Exception):
    """Erros específicos de contas de crédito"""
    def __init__(self, message="Erro em conta de crédito"):
        self.message = message
        super().__init__(self.message)

class DebitAccountError(Exception):
    """Erros específicos de contas de débito"""
    def __init__(self, message="Erro em conta de débito"):
        self.message = message
        super().__init__(self.message)

class DatabaseIntegrityError(Exception):
    """Erros de integridade do banco de dados"""
    def __init__(self, message="Violação de integridade do banco"):
        self.message = message
        super().__init__(self.message)

class AccountOperationError(Exception):
    """Erros genéricos de operações com contas"""
    def __init__(self, message="Erro na operação com conta"):
        self.message = message
        super().__init__(self.message)

# Adicionando exceções para transações
class TransactionError(Exception):
    """Erros genéricos de transações"""
    def __init__(self, message="Erro na transação"):
        self.message = message
        super().__init__(self.message)

class TransactionNotFoundError(Exception):
    """Erros genéricos de transações"""
    def __init__(self, message="Transação não encontrada"):
        self.message = message
        super().__init__(self.message)

class InsufficientBalanceError(TransactionError):
    """Saldo insuficiente"""
    def __init__(self, message="Saldo insuficiente"):
        self.message = message
        super().__init__(self.message)

class InvalidCategoryError(TransactionError):
    """Transação inválida"""
    def __init__(self, message="Transação inválida"):
        self.message = message
        super().__init__(self.message)

    