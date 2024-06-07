import math, time, brownie
from brownie import Contract
import time

def test_zap(zap, pool, strategist, lp_ycrv, amount, user, crv3, cvxcrv, whale_cvxcrv, chain, whale_crv, whale_3crv, gov, st_ycrv, ycrv, yvboost, yveCrv, crv, ybs):
    yveCrv.approve(ycrv, 2**256-1, {'from':user})
    # ycrv = Contract.from_explorer('0xFCc5c47bE19d06BF83eB04298b026F81069ff65b')
    ycrv.burn_to_mint(yveCrv.balanceOf(user)/2, {'from':user})
    crv.approve(zap, 2**256-1, {"from": user})
    crv.approve(pool, 2**256-1, {"from": whale_crv})
    yvboost.approve(zap, 2**256-1, {"from": user})
    yveCrv.approve(zap, 2**256-1, {"from": user})
    lp_ycrv.approve(zap, 2**256-1, {"from": user})
    st_ycrv.approve(zap, 2**256-1, {"from": user})
    cvxcrv.approve(zap, 2**256-1, {"from": user})
    ycrv.approve(zap, 2**256-1, {"from": user})
    ybs.setApprovedCaller(zap, 3, {"from": user})
    chain.snapshot()
    crv_before = crv.balanceOf(user)
    yv_before = lp_ycrv.balanceOf(user)
    print("ZAP CRV --> LP VAULT\n")
    print_user_balances(user, lp_ycrv, crv, yvboost, yveCrv, pool)
    
    legacy_tokens = []
    output_tokens = []
    try:
        for i in range(0,20):
            legacy_tokens.append(zap.LEGACY_TOKENS(i))
    except:
        pass

    try:
        for i in range(0,20):
            output_tokens.append(zap.OUTPUT_TOKENS(i))
    except:
        pass
    
    input_tokens = legacy_tokens + output_tokens
    input_tokens.append(crv.address)
    input_tokens.append(cvxcrv.address)

    # Test some calls
    amount = 10e18
    for i in input_tokens:
        for o in output_tokens:
            if i == o:
                with brownie.reverts():
                    actual = zap.zap(i, o, amount, 0, {'from': user}).return_value
                    r = zap.calc_expected_out(i, o, amount)
                    s = zap.relative_price(i, o, amount)
                continue
            r = zap.calc_expected_out(i, o, amount)
            s = zap.relative_price(i, o, amount)
            min = r * 0.99
            actual = 0
            actual = zap.zap(i, o, amount, min, {'from': user}).return_value
            assert_balances(zap, pool, strategist, lp_ycrv, amount, user, crv3, cvxcrv, whale_cvxcrv, chain, whale_crv, whale_3crv, gov, st_ycrv, ycrv, yvboost, yveCrv, crv)
            print_results(True,i, o, amount, r, s, actual)    

def print_results(is_legacy, i, o, a, r, s, actual):
    abi = Contract("0x9d409a0A012CFbA9B15F6D4B36Ac57A46966Ab9a").abi
    if i == '0xE9A115b77A1057C918F997c32663FdcE24FB873f':
        i = 'YBS'
    else:
        i = Contract.from_abi("",i,abi,persist=False).symbol()
    if o == '0xE9A115b77A1057C918F997c32663FdcE24FB873f':
        o = 'YBS'
    else:
        o = Contract.from_abi("",o,abi,persist=False).symbol()
    print(f'IN  {i}')
    print(f'OUT {o}')
    print(f'AMT IN  {a/1e18}')
    print(f'VIRT AMT OUT {s/1e18}')
    print(f'EXP AMT OUT {r/1e18}')
    if actual is not None:
        print(f'ACTUAL AMT OUT {actual/1e18}')
    print('---')
    
def print_user_balances(user, yvLP, crv, yvboost, yveCrv, pool):
    print("CRV:", crv.balanceOf(user)/1e18)
    print("yveCRV:", yveCrv.balanceOf(user)/1e18)
    print("yvBOOST:", yvboost.balanceOf(user)/1e18)
    print("yvLP:", yvLP.balanceOf(user)/1e18)
    print("----------\n")

def assert_balances(zap, pool, strategist, lp_ycrv, amount, user, crv3, cvxcrv, whale_cvxcrv, chain, whale_crv, whale_3crv, gov, st_ycrv, ycrv, yvboost, yveCrv, crv):
    assert ycrv.balanceOf(zap) < 10
    assert crv.balanceOf(zap) == 0
    assert yvboost.balanceOf(zap) == 0
    assert yveCrv.balanceOf(zap) == 0
    assert lp_ycrv.balanceOf(zap) == 0
    assert st_ycrv.balanceOf(zap) == 0
    assert cvxcrv.balanceOf(zap) == 0
    assert pool.balanceOf(zap) == 0