from bls import generate_private_key, generate_public_key

class Wallet:
    def __init__(self):
        self.sk = generate_private_key()
        self.pk = generate_public_key(self.sk)
    
    def get_address(self):
        return self.pk  # 公钥作为地址
    
    def sign_transaction(self, tx_data: bytes):
        from bls import sign
        return sign(self.sk, tx_data)