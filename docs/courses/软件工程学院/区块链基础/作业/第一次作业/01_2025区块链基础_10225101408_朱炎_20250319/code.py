def calculate_total_bitcoin():
    initial_reward = 50.0
    halving_interval = 210000
    total_btc = 0.0
    current_reward = initial_reward
    halving_count = 0

    while current_reward >= 1e-8:
        period_coins = halving_interval * current_reward
        total_btc += period_coins
        halving_count += 1
        current_reward /= 2

    print(f"\n最终减半次数: {halving_count}次")
    print(f"总发行量: {total_btc:,.8f} BTC ≈ {round(total_btc)} BTC")

def estimate_mining_end_year():
    start_year = 2009           
    blocks_per_halving = 210000 
    block_time_minutes = 10

    minutes_per_year = 365 * 24 * 60
    blocks_per_year = minutes_per_year / block_time_minutes
    years_per_halving = blocks_per_halving / blocks_per_year

    halving_count = 0

    initial_reward = 50.0
    while initial_reward / (2 ** halving_count) >= 1e-8:
        halving_count += 1

    end_year = start_year + years_per_halving * halving_count
    print(f"\n预计全部挖完年份: {end_year:.0f}年")


calculate_total_bitcoin()
estimate_mining_end_year()
