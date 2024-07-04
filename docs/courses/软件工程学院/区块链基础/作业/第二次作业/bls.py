from py_ecc.bls12_381 import G1, G2, add, multiply, is_inf, pairing, curve_order, field_modulus
from py_ecc.fields import bls12_381_FQ as FQ
from functools import reduce
import hashlib

def hash_to_g1(message: bytes):
    G1_cofactor = 0x396c8c005555e1568c00aaab0000aaab

    hashed = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    x_val = hashed % field_modulus
    
    while True:
        y_squared = (pow(x_val, 3, field_modulus) + 4) % field_modulus
        y_val = pow(y_squared, (field_modulus + 1) // 4, field_modulus)
        if pow(y_val, 2, field_modulus) == y_squared:
            x = FQ(x_val)
            y = FQ(y_val)
            point = (x, y)
            point = multiply(point, G1_cofactor)
            if not is_inf(point):
                return point
        x_val = (x_val + 1) % field_modulus

import random

def generate_private_key():
    return random.randint(1, curve_order - 1)

def generate_public_key(sk):
    return multiply(G2, sk)

def sign(sk, message: bytes):
    H_m = hash_to_g1(message)
    return multiply(H_m, sk)

def verify(pk, message: bytes, signature) -> bool:
    H_m = hash_to_g1(message)
    left = pairing(G2, signature)
    right = pairing(pk, H_m)
    return left == right

def aggregate_signatures(signatures: list) -> tuple:
    return reduce(add, signatures)

def aggregate_verify(pubkeys: list, messages: list, aggregate_sig: tuple) -> bool:
    if len(pubkeys) != len(messages):
        return False
    product = 1
    for pk, msg in zip(pubkeys, messages):
        H_m = hash_to_g1(msg)
        product *= pairing(pk, H_m)
    left = pairing(G2, aggregate_sig)
    return left == product

if __name__ == "__main__":
    # 单个签名的情况
    sk = generate_private_key()
    pk = generate_public_key(sk)
    message = b"Hello, BLS!"
    signature = sign(sk, message)
    print("验证结果:", verify(pk, message, signature))
    print("错误消息验证:", verify(pk, b"Wrong message", signature))

    # 多个签名的情况
    num_signers = 3
    sks = [generate_private_key() for _ in range(num_signers)]
    pks = [generate_public_key(sk) for sk in sks]
    messages = [f"Message {i}".encode() for i in range(num_signers)]
    signatures = [sign(sk, msg) for sk, msg in zip(sks, messages)]
    agg_sig = aggregate_signatures(signatures)
    valid = aggregate_verify(pks, messages, agg_sig)
    print("聚合验证结果:", valid)  
    corrupted_messages = [msg + b"no" for msg in messages]
    invalid = aggregate_verify(pks, corrupted_messages, agg_sig)
    print("篡改消息后的验证结果:", invalid)  