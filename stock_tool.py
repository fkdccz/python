"""
个人股票基金数据获取工具
基于 AKShare（免费开源金融数据接口）
功能：股票行情、基金数据、财务指标、板块资金流向等
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# 一、股票行情
# ============================================================

def get_stock_realtime(symbol: str):
    """
    获取单只股票实时行情
    :param symbol: 股票代码，如 "000001"（平安银行）
    """
    df = ak.stock_zh_a_spot_em()
    stock = df[df["代码"] == symbol]
    if stock.empty:
        print(f"未找到股票代码: {symbol}")
        return None
    print(f"\n{'='*50}")
    print(f"  {stock.iloc[0]['名称']}（{symbol}）实时行情")
    print(f"{'='*50}")
    info = stock.iloc[0]
    print(f"  最新价:   {info['最新价']}")
    print(f"  涨跌幅:   {info['涨跌幅']}%")
    print(f"  涨跌额:   {info['涨跌额']}")
    print(f"  成交量:   {info['成交量']}")
    print(f"  成交额:   {info['成交额']}")
    print(f"  今开:     {info['今开']}")
    print(f"  最高:     {info['最高']}")
    print(f"  最低:     {info['最低']}")
    print(f"  换手率:   {info['换手率']}%")
    print(f"  量比:     {info['量比']}")
    print(f"{'='*50}\n")
    return stock


def get_stock_history(symbol: str, period: str = "daily", days: int = 30):
    """
    获取股票历史行情
    :param symbol: 股票代码，如 "000001"
    :param period: 周期 daily/weekly/monthly
    :param days: 获取最近多少天
    """
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"  # 前复权
    )
    print(f"\n{symbol} 最近{days}天历史行情（{period}）:")
    print(df.tail(10).to_string(index=False))
    return df


def get_market_overview():
    """获取A股市场概览（涨跌家数等）"""
    df = ak.stock_zh_a_spot_em()
    total = len(df)
    up = len(df[df["涨跌幅"] > 0])
    down = len(df[df["涨跌幅"] < 0])
    flat = total - up - down
    limit_up = len(df[df["涨跌幅"] >= 9.9])
    limit_down = len(df[df["涨跌幅"] <= -9.9])

    print(f"\n{'='*50}")
    print(f"  A股市场概览")
    print(f"{'='*50}")
    print(f"  总数:     {total} 只")
    print(f"  上涨:     {up} 只")
    print(f"  下跌:     {down} 只")
    print(f"  平盘:     {flat} 只")
    print(f"  涨停:     {limit_up} 只")
    print(f"  跌停:     {limit_down} 只")
    print(f"{'='*50}\n")
    return df


# ============================================================
# 二、基金数据
# ============================================================

def get_fund_info(fund_code: str):
    """
    获取基金基本信息和净值
    :param fund_code: 基金代码，如 "110011"（易方达中小盘）
    """
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        print(f"\n基金 {fund_code} 最近净值走势:")
        print(df.tail(10).to_string(index=False))
        return df
    except Exception as e:
        print(f"获取基金数据失败: {e}")
        return None


def get_fund_ranking(fund_type: str = "全部", top_n: int = 20):
    """
    获取基金排行榜
    :param fund_type: 基金类型
    :param top_n: 前N名
    """
    try:
        df = ak.fund_open_fund_rank_em(symbol="全部")
        df_sorted = df.sort_values(by="近1年", ascending=False).head(top_n)
        print(f"\n基金排行榜 TOP {top_n}（按近1年收益）:")
        cols = ["基金代码", "基金简称", "日期", "单位净值", "近1周", "近1月", "近3月", "近1年"]
        available_cols = [c for c in cols if c in df_sorted.columns]
        print(df_sorted[available_cols].to_string(index=False))
        return df_sorted
    except Exception as e:
        print(f"获取基金排行失败: {e}")
        return None


# ============================================================
# 三、财务指标
# ============================================================

def get_stock_financial(symbol: str):
    """
    获取股票关键财务指标
    :param symbol: 股票代码
    """
    try:
        df = ak.stock_financial_abstract_ths(symbol=symbol)
        print(f"\n{symbol} 财务摘要:")
        print(df.head(10).to_string(index=False))
        return df
    except Exception as e:
        print(f"获取财务数据失败: {e}")
        return None


def get_stock_pe(symbol: str):
    """
    获取个股市盈率等估值指标
    :param symbol: 股票代码
    """
    df = ak.stock_zh_a_spot_em()
    stock = df[df["代码"] == symbol]
    if stock.empty:
        print(f"未找到: {symbol}")
        return None
    info = stock.iloc[0]
    print(f"\n{'='*50}")
    print(f"  {info['名称']}（{symbol}）估值指标")
    print(f"{'='*50}")
    print(f"  市盈率(动):  {info.get('市盈率-动态', 'N/A')}")
    print(f"  市净率:      {info.get('市净率', 'N/A')}")
    print(f"  总市值:      {info.get('总市值', 'N/A')}")
    print(f"  流通市值:    {info.get('流通市值', 'N/A')}")
    print(f"{'='*50}\n")
    return stock


# ============================================================
# 四、板块与资金
# ============================================================

def get_sector_fund_flow():
    """获取行业板块资金流向"""
    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日")
        print("\n行业板块资金流向（今日）:")
        print(df.head(20).to_string(index=False))
        return df
    except Exception as e:
        print(f"获取板块资金流向失败: {e}")
        return None


def get_hot_stocks():
    """获取今日热门股票（人气榜）"""
    try:
        df = ak.stock_hot_rank_em()
        print("\n今日热门股票 TOP 20:")
        print(df.head(20).to_string(index=False))
        return df
    except Exception as e:
        print(f"获取热门股票失败: {e}")
        return None


# ============================================================
# 五、指数数据
# ============================================================

def get_index_realtime():
    """获取主要指数实时行情"""
    try:
        df = ak.stock_zh_index_spot_em()
        # 筛选主要指数
        major_indices = ["上证指数", "深证成指", "创业板指", "沪深300", "中证500", "科创50"]
        result = df[df["名称"].isin(major_indices)]
        print(f"\n{'='*50}")
        print(f"  主要指数实时行情")
        print(f"{'='*50}")
        for _, row in result.iterrows():
            print(f"  {row['名称']:8s}  {row['最新价']:>10.2f}  涨跌幅: {row['涨跌幅']:>6.2f}%")
        print(f"{'='*50}\n")
        return result
    except Exception as e:
        print(f"获取指数数据失败: {e}")
        return None


# ============================================================
# 主程序入口
# ============================================================

def main():
    """主菜单"""
    menu = """
╔══════════════════════════════════════════════════╗
║         个人股票基金数据工具 v1.0               ║
║         基于 AKShare 免费数据                   ║
╠══════════════════════════════════════════════════╣
║  1. 查看主要指数行情                            ║
║  2. 查询个股实时行情                            ║
║  3. 查询个股历史K线                             ║
║  4. A股市场概览（涨跌家数）                     ║
║  5. 个股估值指标（PE/PB）                       ║
║  6. 个股财务摘要                                ║
║  7. 基金净值查询                                ║
║  8. 基金排行榜                                  ║
║  9. 行业板块资金流向                            ║
║  10. 今日热门股票                               ║
║  0. 退出                                        ║
╚══════════════════════════════════════════════════╝
"""
    while True:
        print(menu)
        choice = input("请选择功能 (0-10): ").strip()

        if choice == "0":
            print("再见！祝投资顺利！")
            break
        elif choice == "1":
            get_index_realtime()
        elif choice == "2":
            code = input("请输入股票代码（如 000001）: ").strip()
            get_stock_realtime(code)
        elif choice == "3":
            code = input("请输入股票代码: ").strip()
            days = input("查询最近几天（默认30）: ").strip()
            days = int(days) if days else 30
            get_stock_history(code, days=days)
        elif choice == "4":
            get_market_overview()
        elif choice == "5":
            code = input("请输入股票代码: ").strip()
            get_stock_pe(code)
        elif choice == "6":
            code = input("请输入股票代码: ").strip()
            get_stock_financial(code)
        elif choice == "7":
            code = input("请输入基金代码（如 110011）: ").strip()
            get_fund_info(code)
        elif choice == "8":
            get_fund_ranking()
        elif choice == "9":
            get_sector_fund_flow()
        elif choice == "10":
            get_hot_stocks()
        else:
            print("无效选择，请重试")

        input("\n按回车继续...")


if __name__ == "__main__":
    main()
