from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain
from bls import aggregate_signatures, aggregate_verify

alice = Wallet()
bob = Wallet()
blockchain = Blockchain( # 给Alice初始10个代币
    genesis_recipient=alice.get_address(),
    genesis_amount=10                     
)

alice_balance = sum(
    amt for (addr, amt) in blockchain.utxo.values() 
    if addr == alice.get_address()
)
print("Alice 的初始余额:", alice_balance)

tx1 = Transaction(alice.get_address(), bob.get_address(), 10)
tx1.sign(alice)
print("交易1验证结果:", tx1.is_valid())

if blockchain.add_transaction(tx1):
    print("交易1成功上链")

# Bob向Alice转账15个代币（失败，余额不足）
tx2 = Transaction(bob.get_address(), alice.get_address(), 15)
tx2.sign(bob)
print("交易2验证结果:", tx2.is_valid())  # True，但余额不足
print("交易2上链结果:", blockchain.add_transaction(tx2))  # False

# 聚合签名
carol = Wallet()
tx3_data = b"Multisig_Transaction"
signature_alice = alice.sign_transaction(tx3_data)
signature_carol = carol.sign_transaction(tx3_data)
agg_sig = aggregate_signatures([signature_alice, signature_carol])
valid = aggregate_verify([alice.pk, carol.pk], [tx3_data, tx3_data], agg_sig)
print("聚合签名验证结果:", valid)  # True