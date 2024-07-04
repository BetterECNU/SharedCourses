
class Blockchain:
    def __init__(self, genesis_recipient=None, genesis_amount=0):
        self.utxo = {}  # 格式: {tx_id: (receiver, amount)}
        
        # 生成创世交易（仅第一次初始化时调用）
        if genesis_recipient is not None and genesis_amount > 0:
            self.add_genesis(genesis_recipient, genesis_amount)
        
    def add_genesis(self, receiver, amount):
        # 添加创世区块
        genesis_tx_id = "genesis_tx_0x1"
        self.utxo[genesis_tx_id] = (receiver, amount)
    
    def validate_transaction(self, tx):
        # 验签
        if not tx.is_valid():
            return False
        # 验证发送方余额
        sender_balance = sum(amt for (addr, amt) in self.utxo.values() if addr == tx.sender)
        return sender_balance >= tx.amount
    
    def add_transaction(self, tx):
        if self.validate_transaction(tx):
            tx_id = hash(tx)  # 简化交易ID生成
            self.utxo[tx_id] = (tx.receiver, tx.amount)
            return True
        return False