import math


def gamma_fn(x: int):
    fact = 1
    for i in range(1, x):
        fact = fact * i
    return fact


def gamma_half_fn(x: float):
    n = 2 * x
    assert n == int(n)
    n = int(n)
    fact = 1
    for i in range(1, n - 1):
        fact = fact * i
    out = 1
    for i in range(1, fact + 1):
        out = out * i
    out = math.sqrt(math.pi) * out / (2 ** ((n - 1) / 2))
    return out


def chi_square_pdf(k: int, x: float):
    if x <= 0:
        return 0
    else:
        if k % 2 == 0:
            gamma_out = gamma_fn(int(k / 2))
        else:
            gamma_out = gamma_half_fn(k / 2)
        return x ** (k / 2 - 1) * math.exp(-x / 2) / 2 ** (k / 2) / gamma_out


def get_prize_pool(total_prize_pool: float, buy_in: float, num_players: int):
    allocated_prize_pool = []
    rank = 1
    k = 3

    while rank <= num_players:
        prize_ratio = round(chi_square_pdf(k, rank), 2)
        rank_prize = total_prize_pool * prize_ratio
        if total_prize_pool > sum(allocated_prize_pool) + rank_prize:
            if rank_prize >= buy_in:
                allocated_prize_pool.append(rank_prize)
                rank += 1
            else:
                break
        else:
            break

    left_prize_pool = total_prize_pool - sum(allocated_prize_pool)
    ratios = [prize / total_prize_pool for prize in allocated_prize_pool]
    ratios[0] += 1 - sum(ratios)
    allocated_prize_pool = [
        ratio * left_prize_pool + prize
        for ratio, prize in zip(ratios, allocated_prize_pool)
    ]
    assert sum(allocated_prize_pool) == total_prize_pool
    return allocated_prize_pool
