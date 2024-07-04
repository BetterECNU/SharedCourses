class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender     # 公钥
        self.receiver = receiver # 地址
        self.amount = amount     # 金额
        self.signature = signature
    
    def serialize(self) -> bytes:
        # 序列化交易数据用于签名
        return f"{self.sender}{self.receiver}{self.amount}".encode()
    
    def sign(self, wallet):
        self.signature = wallet.sign_transaction(self.serialize())
    
    def is_valid(self) -> bool:
        from bls import verify
        return verify(self.sender, self.serialize(), self.signature)