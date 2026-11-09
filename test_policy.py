from main import make_decision


def check(scores, expected):
    actual, _ = make_decision(scores)
    assert actual == expected, f"expected {expected}, got {actual}"


check({"toxic": 0.10}, "allow")
check({"toxic": 0.60}, "review")
check({"toxic": 0.95}, "block")
check({"toxic": 0.10, "threat": 0.80}, "block")
print("Policy checks passed.")
