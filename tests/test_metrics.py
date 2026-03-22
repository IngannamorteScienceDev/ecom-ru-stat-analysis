import pandas as pd


def test_basic_growth_formula():
    df = pd.DataFrame({"share_online": [1.0, 2.0, 4.0]})
    df["growth_rate_pct"] = (df["share_online"] / df["share_online"].shift(1)) * 100

    assert pd.isna(df.loc[0, "growth_rate_pct"])
    assert df.loc[1, "growth_rate_pct"] == 200.0
    assert df.loc[2, "growth_rate_pct"] == 200.0