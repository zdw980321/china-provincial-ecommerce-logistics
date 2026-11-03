# A provincial dissimilarity index for diagnosing e-commerce logistics flows in China

This repository reproduces the provincial distribution analysis in *A provincial dissimilarity index for diagnosing e-commerce logistics flows in China*.

The analysis compares accepted express parcel volume with physical-goods online retail across China's 31 provinces for 2021-2024. It generates the three-region and four-region dissimilarity decompositions and the four figures supplied with the manuscript.

## Inputs

`data/provincial_gap_panel.csv` is a derived provincial panel assembled from the public annual operating bulletins republished by the Ministry of Transport and Table 15-13 of the China Statistical Yearbook 2022-2025. The manuscript provides the column definitions and source citations.

## Reproduce

Create a Python environment with the packages in `requirements.txt`, then run:

```bash
python src/reproduce.py
```

The command writes CSV results and 600 dpi PNG figures to `output/`.

## Outputs

- `decomposition_three_region.csv`
- `decomposition_four_region.csv`
- `figure1_decomposition.png`
- `figure2_shares_2024.png`
- `figure3_gap_paths.png`
- `figure4_gap_matrix.png`

## License

The analysis code is released under the MIT License. The panel is a derived dataset; reuse should cite the official public statistical sources named above and the accompanying article.
