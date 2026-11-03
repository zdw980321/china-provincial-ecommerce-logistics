"""Reproduce the provincial dissimilarity decompositions and manuscript figures."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "provincial_gap_panel.csv"
OUT = ROOT / "output"

EAST = {"北京", "天津", "河北", "辽宁", "上海", "江苏", "浙江", "福建", "山东", "广东", "海南"}
CENTRAL = {"山西", "吉林", "黑龙江", "安徽", "江西", "河南", "湖北", "湖南"}
EAST_FOUR = {"北京", "天津", "河北", "上海", "江苏", "浙江", "福建", "山东", "广东", "海南"}
NORTHEAST_FOUR = {"辽宁", "吉林", "黑龙江"}
CENTRAL_FOUR = {"山西", "安徽", "江西", "河南", "湖北", "湖南"}


def region_three(province_zh: str) -> str:
    if province_zh in EAST:
        return "East"
    if province_zh in CENTRAL:
        return "Central"
    return "West"


def region_four(province_zh: str) -> str:
    if province_zh in EAST_FOUR:
        return "East"
    if province_zh in NORTHEAST_FOUR:
        return "Northeast"
    if province_zh in CENTRAL_FOUR:
        return "Central"
    return "West"


def decompose(panel: pd.DataFrame, grouping: str) -> pd.DataFrame:
    rows = []
    for year, frame in panel.groupby("year", sort=True):
        gap = frame["express_share"] - frame["retail_share_31_provinces"]
        national = gap.abs().sum() / 2
        between = 0.0
        within = 0.0
        for _, group in frame.assign(gap=gap).groupby(grouping):
            group_gap = group["gap"]
            between += abs(group_gap.sum()) / 2
            within += (group_gap.abs().sum() - abs(group_gap.sum())) / 2
        rows.append({
            "year": int(year),
            "national_dissimilarity": national,
            "between_region": between,
            "within_region": within,
            "within_share": within / national,
        })
    return pd.DataFrame(rows)


def configure_plotting() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9.5,
        "axes.labelsize": 10,
        "savefig.dpi": 600,
        "savefig.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#27313a",
        "xtick.color": "#27313a",
        "ytick.color": "#27313a",
        "text.color": "#27313a",
    })


def figures(panel: pd.DataFrame, three: pd.DataFrame) -> None:
    navy, orange, teal, brick, grey = "#1B4965", "#C95F35", "#147D7E", "#A32B2B", "#B9C2C8"
    years = three["year"].tolist()

    fig, ax = plt.subplots(figsize=(7.0, 4.05), layout="constrained")
    within = 100 * three["within_region"]
    between = 100 * three["between_region"]
    positions = range(len(years))
    ax.bar(positions, within, color=navy, width=0.62, label="Within regions")
    ax.bar(positions, between, bottom=within, color=orange, width=0.62, label="Between regions")
    for i, total in enumerate(within + between):
        ax.text(i, total + 0.32, f"{total:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Dissimilarity (percentage points)")
    ax.set_xticks(list(positions), [str(year) for year in years])
    ax.set_ylim(0, float((within + between).max()) + 3.2)
    ax.grid(axis="y", color="#D9E0E5", lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper right", handlelength=1.8)
    fig.savefig(OUT / "figure1_decomposition.png")
    plt.close()

    panel_2024 = panel.loc[panel["year"] == 2024].copy()
    positive = {"Guangdong", "Zhejiang", "Henan", "Hebei"}
    negative = {"Beijing", "Shanghai", "Fujian", "Jiangsu"}
    background = panel_2024.loc[~panel_2024["province"].isin(positive | negative)]
    fig, ax = plt.subplots(figsize=(6.7, 5.7), layout="constrained")
    ax.scatter(100 * background["retail_share_31_provinces"], 100 * background["express_share"], s=24, color=grey, alpha=0.9, zorder=2, label="Other provinces")
    for names, color, label in ((positive, teal, "Higher acceptance share"), (negative, brick, "Higher retail share")):
        frame = panel_2024.loc[panel_2024["province"].isin(names)]
        ax.scatter(100 * frame["retail_share_31_provinces"], 100 * frame["express_share"], s=48, color=color, zorder=4, label=label)
    limit = max(100 * panel_2024["retail_share_31_provinces"].max(), 100 * panel_2024["express_share"].max()) + 1.6
    ax.plot([0, limit], [0, limit], color="#27313a", lw=1.0, ls="--", zorder=1)
    offsets = {"Guangdong": (8, 4), "Zhejiang": (8, -12), "Jiangsu": (-58, 6), "Henan": (-52, 10), "Hebei": (8, 10), "Beijing": (8, -12), "Shanghai": (8, 4), "Shandong": (8, -8), "Fujian": (8, -10)}
    for _, row in panel_2024.iterrows():
        if row["province"] in offsets:
            ax.annotate(row["province"], (100 * row["retail_share_31_provinces"], 100 * row["express_share"]), textcoords="offset points", xytext=offsets[row["province"]], fontsize=8, color="#27313a")
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xlabel("Share of physical online retail (%)")
    ax.set_ylabel("Share of accepted express volume (%)")
    ax.grid(color="#E0E5E8", lw=0.55)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper left", handletextpad=0.5)
    fig.savefig(OUT / "figure2_shares_2024.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(7.0, 3.95), layout="constrained")
    anchors = {"Guangdong": navy, "Zhejiang": teal, "Beijing": brick, "Shanghai": orange}
    for province, color in anchors.items():
        frame = panel.loc[panel["province"] == province].sort_values("year")
        ax.plot(frame["year"], frame["gap_31_percentage_points"], marker="o", ms=5.5, lw=2.1, color=color, label=province)
    ax.axhline(0, color="#27313a", lw=0.8)
    ax.set_xticks(years)
    ax.set_ylabel("Share gap (percentage points)")
    ax.grid(axis="y", color="#E0E5E8", lw=0.55)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=4, fontsize=8.2, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    fig.savefig(OUT / "figure3_gap_paths.png")
    plt.close()

    heat = panel.pivot(index="province", columns="year", values="gap_31_percentage_points")
    heat = heat.loc[heat[2024].sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7.0, 7.5), layout="constrained")
    norm = TwoSlopeNorm(vmin=float(heat.min().min()), vcenter=0, vmax=float(heat.max().max()))
    image = ax.imshow(heat.values, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(heat.columns)), [str(year) for year in heat.columns])
    ax.set_yticks(range(len(heat.index)), heat.index, fontsize=7.7)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=0)
    for x in range(1, len(heat.columns)):
        ax.axvline(x - 0.5, color="white", lw=1.0)
    for y in range(1, len(heat.index)):
        ax.axhline(y - 0.5, color="white", lw=0.28)
    colorbar = fig.colorbar(image, ax=ax, pad=0.015, shrink=0.9)
    colorbar.set_label("Share gap (percentage points)", fontsize=9)
    fig.savefig(OUT / "figure4_gap_matrix.png")
    plt.close()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    configure_plotting()
    panel = pd.read_csv(PANEL)
    panel["region_three"] = panel["province_zh"].map(region_three)
    panel["region_four"] = panel["province_zh"].map(region_four)
    three = decompose(panel, "region_three")
    four = decompose(panel, "region_four")
    three.to_csv(OUT / "decomposition_three_region.csv", index=False)
    four.to_csv(OUT / "decomposition_four_region.csv", index=False)
    figures(panel, three)


if __name__ == "__main__":
    main()
