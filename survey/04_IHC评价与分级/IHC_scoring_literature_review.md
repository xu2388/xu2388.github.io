# From IHC image → machine-computable protein-expression score
### A literature review for building a scoring pipeline on **generated (virtual) IHC** images

**Scope.** How digital/computational pathology converts a brightfield IHC image into a computable score: colour deconvolution → optical density → segmentation → per-cell intensity class → aggregate score (0/1+/2+/3+, Allred, H-score, or continuous %). Every citation below was retrieved and verified against the publisher / PubMed / arXiv record during this review. Where a claim could not be verified, it is flagged in §7.

**Companion artefact:** `ruifrok2001.pdf` (the original colour-deconvolution paper, downloaded) and `her2contest.pdf` (the HER2 contest paper).

---

## 1. Colour deconvolution

### 1.1 The original method (verified citation)

> **Ruifrok AC, Johnston DA.** *Quantification of histochemical staining by color deconvolution.* **Analytical and Quantitative Cytology and Histology**, 2001; **23**(4):291–299. PMID: 11531144.
> Abstract: <https://europepmc.org/abstract/MED/11531144> · Full text PDF: <https://helios2.mi.parisdescartes.fr/~lomn/Cours/CV/BME/HistoPatho/Quantification_of_histochemical_staining.pdf>

Note the exact title is *"Quantification of **histochemical** staining by color deconvolution"* (not "immunohistochemical"). The authors are at UT M.D. Anderson Cancer Center. The method was implemented as NIH Image macros.

### 1.2 The mathematics (from the paper itself)

**(a) Beer–Lambert / Lambert–Beer law.** For each detection channel *c* (R, G, B):

```
I_c = I_0,c · exp( −A_c · c_c )
```

where `I_0,c` = incident light, `I_c` = transmitted light, `A_c` = absorption factor of the stain, `c_c` = stain concentration/amount.

**(b) Optical density.** Ruifrok defines

```
OD_c = −log10( I_c / I_0,c ) = A_c · c_c
```

The key statement in the paper: *"the OD for each channel is **linear** with the concentration of absorbing material, and can therefore be used for separation of the contribution of multiple stains."* This is the entire justification for converting RGB → OD before doing anything quantitative.

**(c) The stain matrix M.** Each pure stain has a characteristic 3×1 OD vector over (R,G,B). Stacking *n* stains gives an *n*×3 matrix **M**. Ruifrok's worked example (hematoxylin, eosin, DAB) uses raw OD values:

```
             R     G     B
Hematoxylin 0.18  0.20  0.08
Eosin       0.01  0.13  0.01
DAB         0.10  0.21  0.29
```

Each row is then **normalised to unit length** (`p̂_ij = p_ij / √(p_i1²+p_i2²+p_i3²)`), giving the normalised OD matrix **M**:

```
             R     G     B
Hematoxylin 0.65  0.70  0.29     ← the canonical "H" vector
Eosin       0.07  0.99  0.11
DAB         0.27  0.57  0.78     ← the canonical "DAB" vector
```

These two vectors — **H = (0.65, 0.70, 0.29)** and **DAB = (0.27, 0.57, 0.78)** — are the defaults shipped in essentially every implementation (ImageJ Colour Deconvolution, scikit-image, StainTools, QuPath, CellProfiler).

**(d) Mixing and unmixing.** If **C** is the 3×1 vector of stain amounts at a pixel, the observed OD vector is

```
y = C · M          (Ruifrok's row-vector convention)
```

so the stain amounts are recovered by multiplying the OD image by the inverse of **M**, which Ruifrok calls the **colour-deconvolution matrix D**:

```
C = D · y ,   D = M⁻¹
```

For the H/E/DAB matrix above, the paper gives:

```
       1.88  −0.07  −0.60
D  =  −1.02   1.13  −0.48
      −0.55  −0.13   1.57
```

The diagonal terms are >1 and the off-diagonal terms are negative: each stain channel is a *contrast-enhanced* difference of the three OD channels, not a simple subtraction. Ruifrok notes that if the three stains were pure red/green/blue, **D** would be the identity.

**(e) Role of the specific stain vectors.**
- **H–DAB** (2-stain) is the standard IHC case: hematoxylin counterstain + DAB chromogen. Implementations use the 2×3 sub-matrix and treat the third (orthogonal residual) channel as "residual/background".
- **H–AEC** (3-amino-9-ethylcarbazole, red chromogen) requires a different chromogen vector because AEC is red, not brown — using the DAB vector on AEC slides is a common and serious bug.
- **H–DAB–hematoxylin** and **H–DAB–eosin** are the 3-stain cases used when the IHC slide is also eosin-counterstained; Ruifrok explicitly tested DAB+H+E and showed DAB quantification was unaffected by adding eosin (see §1.4).
- The paper itself quantifies the failure mode: when DAB is **saturated** (extremely dark), the erroneously deconvolved "hematoxylin" signal can reach **~65%** of the measured hematoxylin IOD. Saturation breaks *every* colour-separation method, not just this one.

**(f) Background / illumination correction.** Ruifrok used *"the stored image of an empty field ... for determination of the light entering at each pixel (I_0,c), implicitly correcting for unequal illumination background subtraction."* In modern practice `I_0` is a per-channel white/blank estimate (e.g. the 99th percentile of a blank region, or the modal background).

### 1.3 Practical issues

- **Stain-vector estimation.** The default Ruifrok vectors are a *starting point*, not ground truth. Varghese et al. (IHC Profiler, §2.3) explicitly **re-derived** the OD vectors because the original Ruifrok vectors left residual pixels in the complementary image (false-positive stain separation). The robust procedure (Macenko, Vahadane) is to estimate the vectors *per slide* from the data rather than hard-code them.
- **Batch effects / stain matrix problem.** Staining and scanning introduce colour variation between labs, scanners, and days. Because deconvolution is a linear inversion, a wrong **M** propagates directly into wrong stain amounts — the "stain matrix problem." This is the entire motivation for colour normalisation.
- **Saturation and over-staining** destroy the linearity assumption (above).
- **Caveat for virtual IHC specifically.** A generated IHC image is produced by a model, not by chemistry. Its "stain vectors" are whatever the generator learned; they are not guaranteed to lie in the physical OD cone. Colour deconvolution will still run, but the numeric DAB OD is only as meaningful as the generator's colour fidelity. This is why *normalising generated IHC into a fixed stain space before scoring* is advisable.

### 1.4 Modern alternatives (verified citations)

| Method | Citation | Idea |
|---|---|---|
| **Reinhard** colour transfer | Reinhard E, Ashikhmin M, Gooch B, Shirley P. *Color transfer between images.* **IEEE Computer Graphics and Applications**, 2001; **21**(5):34–41. DOI 10.1109/38.946629 · <https://ieeexplore.ieee.org/abstract/document/946629> | Match mean/σ in a decorrelated colour space (ℓαβ). Simple, fast, not stain-aware. |
| **Macenko** normalisation | Macenko M, Niethammer M, Marron JS, Borland D, Woosley JT, Guan X, Schmitt C, Thomas NE. *A method for normalizing histology slides for quantitative analysis.* **IEEE ISBI 2009**, pp. 1107–1110. DOI 10.1109/ISBI.2009.5193250 · PDF: <http://wwwx.cs.unc.edu/~mn/sites/default/files/macenko2009.pdf> | Estimate stain vectors from the OD point cloud (SVD + robust angle percentiles), then rescale to a target. The de-facto standard for H&E. |
| **Vahadane** normalisation | Vahadane A, Peng T, Sethi A, Albarqouni S, Wang L, Baust M, Steiger K, Schlitter AM, Sethi A, Irmakci I, Wang X, Navab N. *Structure-Preserving Color Normalization and Sparse Stain Separation for Histological Images.* **IEEE Transactions on Medical Imaging**, 2016; **35**(8):1962–1971. DOI 10.1109/TMI.2016.2547890 · <https://ieeexplore.ieee.org/document/7460968> | Sparse non-negative matrix factorisation (SNMF) to separate stain density maps from stain colour basis; preserves structure better than Macenko. |
| **StainTools** (Python) | Peter554/StainTools. <https://github.com/Peter554/StainTools> · PyPI: <https://pypi.org/project/staintools/> | Wraps Reinhard / Macenko / Vahadane + Ruifrok deconvolution behind a `StainNormalizer` interface. |
| **scikit-image** | `skimage.color.rgb2hed` / `hed2rgb`; worked IHC example: <https://scikit-image.org/docs/0.25.x/auto_examples/color_exposure/plot_ihc_color_separation.html> | `rgb2hed` returns an (H, D, E) image using Ruifrok's matrix; the example explicitly separates hematoxylin from **DAB** on an IHC slide and cites Ruifrok & Johnston. |
| **ImageJ Colour Deconvolution 2** | Landini G. *Colour Deconvolution 2 – Novel context-based segmentation algorithms.* <https://github.com/landinig/IJ-Colour_Deconvolution2> · <https://blog.bham.ac.uk/intellimic/g-landini-software/colour-deconvolution-2/> | Implements Ruifrok & Johnston; allows user-defined 3×3 OD vector matrices. |
| **Benchmarking / newer methods** | *Staining normalization in histopathology: Method benchmarking...* **Scientific Reports** 2026. <https://www.nature.com/articles/s41598-026-40943-3> · *Stain normalization methods for histopathology image analysis: a review*, **Information Fusion** 2024. <https://www.sciencedirect.com/science/article/pii/S1566253523003135> | Recent reviews/benchmarks of the whole family of normalisation methods. |

---

## 2. Optical density

### 2.1 The physical quantity

From Beer–Lambert (verified in §1.2, straight from Ruifrok 2001):

```
I_c = I_0,c · exp(−A_c·c_c)      ⇒      OD_c = −log10(I_c / I_0,c) = A_c · c_c
```

**Why OD and not raw RGB.** Transmitted intensity is an *exponential* function of stain concentration, so raw RGB is non-linear in the thing we want to measure (amount of protein-bound chromogen). OD is **linear** in stain amount. Any "stain amount", "expression level", or "intensity class" statement in quantitative IHC is therefore, implicitly or explicitly, a statement about OD.

**Working definitions used in the literature:**

- **OD (per pixel, per channel):** `−log10(I/I_0)`, computed after `I_0` (white) correction.
- **DAB OD:** the DAB channel of the deconvolved OD image (§1.2d) — the physically-meaningful "amount of DAB" per pixel.
- **Mean OD:** `IOD / area` — average stain density over a region.
- **Integrated OD (IOD) = cumulative OD:** `Σ OD` over all pixels in a region (or `mean OD × area`). IOD is the *total stain amount*; it is the quantity Ruifrok plots on the y-axis throughout his Results (IOD of DAB, IOD of hematoxylin, etc.).
- **AOD (average OD)** is the same as mean OD in most implementations.

### 2.2 OD thresholds to call cells/pixels positive vs negative

The pattern throughout the literature: deconvolve → work in DAB-OD space → apply a threshold (fixed, Otsu, or calibrated from negative controls) → count positive area/cells.

- **Ruifrok & Johnston 2001** — establishes the OD framework and reports reproducibility of IOD measurements with mean-shift < 0.05, scale-factor > 0.95, precision > 0.99, concordance > 0.99 when adding hematoxylin/eosin to DAB-stained slides. (This is the quantitative backbone for all downstream thresholding.)
- **Varghese F, Bukhari AB, Malhotra R, De A.** *IHC Profiler: An Open Source Plugin for the Quantitative Evaluation and Automated Scoring of Immunohistochemistry Images of Human Tissue Samples.* **PLoS ONE** 2014; **9**(5):e96801. DOI 10.1371/journal.pone.0096801 · <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0096801> · Code: <https://sourceforge.net/projects/ihcprofiler/> — **the canonical OD-threshold scoring tool.** It deconvolves DAB/H using re-optimised OD vectors, then bins the DAB-channel pixel histogram into four zones by intensity:
  - High positive (3+): 0–60
  - Positive (2+): 61–120
  - Low positive (1+): 121–180
  - Negative (0): 181–235
  - (235–255 = fat/blank, **excluded**)
  Report: **88.6% agreement with pathologists, κ = 0.843**; inter-observer κ between three pathologists was −0.669, 0.011 and 0.715 — i.e. the automated OD method was *more reproducible than the humans*.
- **Liu J, Xu B, Zheng C, Gong Y, Garibaldi J, Soria D, Green A, Ellis IO, Zou W, Qiu G.** *An End-to-End Deep Learning Histochemical Scoring System for Breast Cancer Tissue Microarray.* **IEEE Transactions on Medical Imaging** 2019; **38**(2):377–388. DOI 10.1109/TMI.2018.2868333 · arXiv: <https://arxiv.org/abs/1801.06288> — explicitly converts RGB → `I_OD = −log(I/I0)` with `I0=[255,255,255]`, deconvolves `I_DAB-H = M⁻¹ I_OD`, keeps only the DAB channel, then uses **Luminance Adaptive Multi-Thresholding (LAMT)** instead of a fixed OD threshold.
- **Patel S, Fridovich-Keil S, Rasmussen SA, Fridovich-Keil JL.** *DAB-quant: An open-source digital system for quantifying immunohistochemical staining with 3,3′-diaminobenzidine (DAB).* **PLoS ONE** 2022; **17**(7):e0271593. DOI 10.1371/journal.pone.0271593 · <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0271593> · Code: <https://github.com/sarafridov/DAB-quant> — an OD-adjacent alternative that scores **Normalized Red Minus Blue (NRMB)** per pixel and sets the positive threshold from **negative-control slides** with a default error tolerance of 0.1%. Its tissue-vs-empty threshold uses **Otsu's method**. Output = *fraction of stained tissue pixels* + an intensity histogram. Explicitly pixel-based, not cell-based.

**Practical note for virtual IHC.** OD thresholds (whether fixed like IHC Profiler's or calibrated like DAB-quant's) are *not* transferable between stainers or generators. On generated IHC you must re-derive thresholds — ideally against a held-out set of real IHC slides scored by a pathologist.

---

## 3. Cell / nuclei segmentation and per-cell scoring

### 3.1 Segmentation + classification tools (verified citations)

| Tool | Citation | Notes |
|---|---|---|
| **StarDist** | Schmidt U, Weigert M, Broaddus C, Myers G. *Cell Detection with Star-convex Polygons.* **MICCAI 2018**, LNCS 11071:265–273. DOI 10.1007/978-3-030-00934-2_30 · arXiv:1806.03535 · <https://github.com/stardist/stardist> | Star-convex polygon regression; robust on round nuclei. Widely used as an annotation-seeding model in pathology (e.g. Bannah et al. below). |
| **HoVer-Net** | Graham S, Vu QD, Raza SEA, Azam A, Tsang YW, Kwak JT, Rajpoot N. *HoVer-Net: Simultaneous segmentation and classification of nuclei in multi-tissue histology images.* **Medical Image Analysis** 2019; **58**:101563. DOI 10.1016/j.media.2019.101563 · <https://github.com/TissueImageAnalytics/hover_net> | Jointly segments **and classifies** nuclei into types (epithelial, inflammatory, spindle, misc.) using horizontal/vertical distance maps. Its 5-class nuclear composition features are reused by SlideGraph+ (§5.1). MIT licence, code available. |
| **Cellpose** | Stringer C, Wang T, Michaelos M, Pachitariu M. *Cellpose: a generalist algorithm for cellular segmentation.* **Nature Methods** 2021; **18**(1):100–106. DOI 10.1038/s41592-020-01018-x · <https://www.nature.com/articles/s41592-020-01018-x> | Generalist flow-based segmentation; fine-tunes well on IHC nuclei (see PR-IHC pipeline below). |
| **QuPath** | Bankhead P, Loughrey MB, Fernández JA, Dombrowski Y, McArt DG, Dunne PD, McQuaid S, Gray RT, Murray LJ, Coleman HG, James JA, Salto-Tellez M, Hamilton PW. *QuPath: Open source software for digital pathology image analysis.* **Scientific Reports** 2017; **7**:16878. DOI 10.1038/s41598-017-17204-5 · <https://qupath.github.io> | Free, scriptable (Groovy) WSI platform with built-in **stain estimation**, cell detection (OD-sum), trainable cell classification, TMA dearraying, and batch processing. The de-facto open reference for stain estimation + per-cell scoring. |
| **CellProfiler** | Carpenter AE, Jones TR, Lamprecht MR, Clarke C, Kang IH, Friman O, Guertin DA, Chang JH, Lindquist RA, Moffat J, Golland P, Sabatini DM. *CellProfiler: image analysis software for identifying and quantifying cell phenotypes.* **Genome Biology** 2006; **7**(10):R100. DOI 10.1186/gb-2006-7-10-r100 · <https://cellprofiler.org> | Modular, open-source pipeline builder; widely used for IHC nuclear/cytoplasmic quantification. |
| **HALO / HALO AI (Indica Labs)** and **Aperio (Leica)** | Commercial. Indica Labs Lung PD-L1 AI: <https://indicalab.com/clinical-products/lung-pd-l1-ai> · Breast Ki67 AI (Aperio HALO AP store): <https://stage.leicabiosystems.com/en-gb/digital-pathology/analyze/aperioaistore/gallery/breast-ki67-ai> | Validated, regulatory-marked AI apps. **PD-L1 AI** outputs **TPS** with per-cell classes (positive / negative / non-cancer). **Breast Ki67 AI** outputs per-slide **% Ki67 positive cells**, counts, and a Negative/Positive(Strong) histogram. Note: these are RUO/IVDR-marked per the vendor pages; the Ki67 app reports only two cell classes (neg/pos), not 3–4 bins. |
| **PanNuke** (dataset) | Gamper J, Koohbanani NA, Benes K, Graham S, Jahanifar M, Khurram SA, Azam A, Hewitt K, Rajpoot N. *PanNuke: An Open Pan-Cancer Histology Dataset for Nuclei Instance Segmentation and Classification.* **MICCAI COMPAY 2019**, LNCS 11843:11–19. DOI 10.1007/978-3-030-23937-4_2 · <https://jgamper.github.io/PanNukeDataset/> | Pan-cancer nuclei instance segmentation + 5-class classification benchmark. Useful for training the segmentation stage. |

### 3.2 Classifying DAB intensity into 3–4 bins **per cell**

This is the crux for a virtual-IHC scoring pipeline. Three verified, directly relevant works:

**(a) Fauzi et al. 2022 — ER, Allred, per-cell Weak/Moderate/Strong**
> Fauzi MFA, Wan Ahmad WSHM, Jamaluddin MF, Lee JTH, Khor SY, Looi LM, Abas FS, Aldahoul N. *Allred Scoring of ER-IHC Stained Whole-Slide Images for Hormone Receptor Status in Breast Carcinoma.* **Diagnostics** 2022; **12**(12):3093. DOI 10.3390/diagnostics12123093 · <https://www.mdpi.com/2075-4418/12/12/3093>

Pipeline: (1) CNN cell detection via Euclidean-distance score map (threshold ≥ 0.2, area > 240, watershed split); (2) positive/negative classification on 32×32 patches using weighted hue `wH` and weighted value `wV` in HSV (`wV<50` → positive; else `wH<40` → positive); (3) a separate **9-layer CNN** classifies positive cells into **weak / moderate / strong**; (4) Allred = proportion score (0–5) + intensity score (0–3). Reported: detection precision 93% / recall 96%; P/N accuracy 95% (99% excluding upstream FPs); **WMS accuracy 88% (90% excluding upstream FPs)**; slide-level Allred exact match 23/40, treatment-recommendation agreement **82.5% (33/40)**. Code: **not released** (data on request).

**(b) Bannah et al. 2026 — PR, per-cell 4-class + Allred**
> Bannah H, Fauzi MFA, Mansor S, Nabi MS, Hossen MS, Chiew SF, Cheah PL, Looi LM. *AI-Driven Breast Cancer Nuclei Segmentation, Classification, and Scoring in PR-IHC Images.* **Diagnostics** 2026; **16**(9):1295. <https://www.mdpi.com/2075-4418/16/9/1295> · Dataset: PR-IHC-40x, IEEE DataPort DOI 10.21227/tag3-k180

Pipeline: fine-tuned **Cellpose** nuclei segmentation → **stain deconvolution to the DAB channel**, DAB intensity inverted so darker = stronger → mean DAB intensity per nucleus → **three calibrated thresholds** (grid-searched on expert-annotated ROIs to maximise macro-F1, then frozen) split nuclei into **negative / weak / moderate / strong** → **Allred** score. Reported: segmentation F1 0.85, IoU 0.74; **4-class nuclei classification macro-F1 ≈ 0.95** (cross-dataset ER-IHC F1 0.91); slide-level Allred exact match **70%**, within ±1 **86%**, treatment concordance **94%**. Misclassification concentrated at the **weak/moderate** boundary. Code: **on request** (dataset public).

**(c) Wen et al. 2024 — per-pixel 4-class DAB (see §4)**
> Wen Z, Luo D, Wang S, Rong R, Evers BM, Jia L, Fang Y, Daoud EV, Yang S, Gu Z, Arner EN, Lewis CM, Solis Soto LM, Fujimoto J, Behrens C, Wistuba II, Yang DM, Brekken RA, O'Donnell KA, Xie Y, Xiao G. *Deep Learning–Based H-Score Quantification of Immunohistochemistry-Stained Images.* **Modern Pathology** 2024; **37**(2):100398. DOI 10.1016/j.modpat.2023.100398 · <https://www.sciencedirect.com/science/article/pii/S0893395223003034>

Uses a deep-learning region-recognition model trained on **hematoxylin only** (pixel accuracy 0.92–0.99 per class), then **categorises each pixel's DAB intensity as negative / weak / moderate / strong** and computes the H-score from the four percentages. This is the cleanest "4-bin DAB" precedent — but note it is **per-pixel**, whereas Fauzi/Bannah are **per-cell**.

**Takeaway.** Two design choices dominate: (i) bin **per pixel** (fast, works with IHC Profiler-style histogram thresholds, but ignores cell identity) vs (ii) bin **per nucleus** (needs segmentation; matches how pathologists actually score, and is what you need for 0/1+/2+/3+ membrane/nuclear scores and for Allred/H-score).

---

## 4. Automated H-score

### 4.1 The formulation

The H-score (histochemical score; McCarty's semi-quantitative system, widely attributed to McCarty KS Jr. et al., 1985 — see §7 on verification) is, in its standard form:

```
H-score = 1 × (% weakly stained cells)
        + 2 × (% moderately stained cells)
        + 3 × (% strongly stained cells)
```

Range **0–300**. It is a *weighted percentage*, not a fraction; a slide with 100% strongly stained cells scores 300. Automated H-score papers instantiate exactly this, differing only in whether the percentages are over **pixels** or **cells**.

### 4.2 Verified automated-H-score papers

**(a) Liu et al. 2019 — direct regression to H-score (breast TMA)**
> Liu J, et al. **IEEE TMI** 2019; **38**(2):377–388. DOI 10.1109/TMI.2018.2868333 · arXiv: <https://arxiv.org/abs/1801.06288>

- **Pipeline:** OD conversion → H-DAB colour deconvolution → LAMT stain-intensity description image → two U-Nets (general nuclei, tumour nuclei) → ROI = stain-intensity × nuclei mask → **RAM-CNN** (dual-input regression) predicts the H-score directly.
- **H-score definition used:** `H = 1×WSN + 2×MSN + 3×SSN` (weak/moderate/strong stained nuclei %), range 0–300, computed when tumour area > 15% of the TMA core. Biomarkers: ER, p53, PgR (NPI+ cohort, 105 TMA images, 2 pathologists).
- **Results:** RAM-CNN **MAE 21.33, SD 29.14, CC 0.95** — statistically on par with **inter-pathologist** disagreement (MAE 20.63, SD 30.55, CC 0.95). Excluding 9 poor-quality TMAs, MAE 18.79. Per-biomarker MAE: ER 21.01, p53 16.66, PgR 25.44.
- **Code:** not released (dataset on request).

**(b) Wen et al. 2024 — per-pixel 4-bin → H-score (Modern Pathology)**
> Wen Z, et al. **Modern Pathology** 2024; **37**(2):100398. <https://www.sciencedirect.com/science/article/pii/S0893395223003034>

- **Pipeline:** deep-learning region recognition trained on hematoxylin-only (pixel accuracy 0.92–0.99) → per-pixel DAB intensity classified negative/weak/moderate/strong → H-score from the four percentages.
- **Output:** H-score directly, in seconds per image; reported "precision and consistency comparable to experienced pathologists." (Full numeric ICC/correlation values sit behind the publisher's bot wall — see §7.)
- **Code:** not located as a public repository.

**(c) Yin et al. 2026 — fully automated H-score, **code released** (Technology in Cancer Research & Treatment)**
> Yin T, Lifrange F, Denis Z, de Caluwé A, Buisseret L, Catteau X, Legros C, Reynaert N, Dhont J. *Fully Automated Stain Quantification Framework for IHC Whole Slide Images in Breast Cancer.* **Technology in Cancer Research & Treatment** 2026; **25**:15330338251407734. DOI 10.1177/15330338251407734 · Code: <https://github.com/YinTuo/AutoIHC> · PubMed: 41930704

- **Pipeline (three modules):** (1) tumour–stroma segmentation (MoCo-SM); (2) nuclei segmentation (Triple UNet); (3) **H-score estimation module** (VGG16Regression; alternatives StainIntensityNet, RAM-CNN — i.e. reimplementing Liu 2019's RAM-CNN). Gigapixel WSI in ~2 min on 2× RTX A6000.
- **Results:** Spearman ρ = **0.84 (95% CI 0.77–0.89)** across 100 expert-annotated WSIs, vs **inter-observer ρ = 0.84 (0.63–0.94)** between two pathologists, and vs SOTA ρ = 0.78. **Matches human inter-observer variability.** Biomarker example: MHC-I.
- **Code: publicly released** (PyTorch, MIT-style research use).

**(d) QuPath H-score scripts (practical, open)**
- QuPath pixel H-score script: <https://github.com/elijahedmondson/QuPath-scripts/blob/main/Pixel%20H-score.groovy>
- QuPath implementation of H-score (cell detection + high/medium/low classes): <https://bio-protocol.org/exchange/minidetail?id=10778612&type=30>
- QuPath headless IHC/DAB positive-rate pipeline: <https://github.com/baiseraku/qupath-ihc-positive-rate>

These are the "roll your own" route: detect cells → deconvolve → classify by DAB OD → compute `1×w + 2×m + 3×s`.

---

## 5. Biomarker-specific automated scoring

### 5.1 HER2

**(a) HER2 challenge contest (the benchmark)**
> Qaiser T, Mukherjee A, Reddy Pb C, Munugoti SD, Tallam V, Pitkäaho T, Lehtimäki T, Naughton T, Berseth M, Pedraza A, Mukundan R, Smith M, Bhalerao A, Rodner E, Simon M, Denzler J, Huang CH, Bueno G, Snead D, Ellis IO, ... Rajpoot N. *HER2 challenge contest: a detailed assessment of automated HER2 scoring algorithms in whole slide images of breast cancer tissues.* **Histopathology** 2018; **72**(2):227–238. DOI 10.1111/his.13333 · <https://europepmc.org/abstract/MED/28771788> · Data: <https://warwick.ac.uk/fac/cross_fac/tia/data/her2contest/>

- **Input:** 86 cases of invasive breast carcinoma, WSI, H&E **and** HER2 IHC.
- **Ground truth:** consensus of ≥2 expert pathologists.
- **Metrics:** deliberately **not** kappa — the contest used a bespoke three-part scheme: **agreement points** (penalty per erroneous prediction), **weighted confidence** (credence of the predicted score), and **combined points**.
- **Findings:** automated methods were comparable to, and in a "Man vs Machine" subset could beat, the four participating pathologists. All participants correctly identified all 3+ cases (no one denied treatment); over-calls of 0/1+ never exceeded 2+; **the 2+ (equivocal) class was the hardest for both humans and machines**. On 15 Man-vs-Machine cases, the machine over-called 2+→3+ once (VISILAB) vs three times for the human pathologists.
- **Code:** contest data public; individual team code varies.

**(b) Her2Net**
> Saha M, Chakraborty C. *Her2Net: A Deep Framework for Semantic Segmentation and Classification of Cell Membranes and Nuclei in Breast Cancer Evaluation.* **IEEE Transactions on Image Processing** 2018; **27**(5):2189–2200. DOI 10.1109/TIP.2018.2795742

Segments + classifies cell **membranes** and **nuclei** from HER2 IHC to support HER2 scoring with minimal user intervention. (Full architecture/metrics behind IEEE paywall — see §7; the Semantic Scholar record confirms the citation and that it targets HER2 scoring.)

**(c) Pedraza et al. 2024 — 0/1+/2+/3+ with intermediate sub-classes**
> Pedraza A, Gonzalez L, Deniz O, Bueno G. *Deep Neural Networks for HER2 Grading of Whole Slide Images with Subclasses Levels.* **Algorithms** 2024; **17**(3):97. DOI 10.3390/a17030097 · <https://www.mdpi.com/1999-4893/17/3/97>

- **Input:** 306 WSIs / 153 breast cancer cases, three centres, 40×; 64×64 patches.
- **Method:** AlexNet / GoogLeNet / VGG-16 / ResNet-101 / DenseNet-201, with **Macenko** colour augmentation. Key idea: a **7-class** scheme (0, 1, **1.5**, 2, **2.5**, 3, background) that isolates the ambiguous 1↔2 and 2↔3 patches, then **aggregates back to 5 classes** (1.5→2+, 2.5+→3+) for clinical comparability.
- **Output:** slide-level **0 / 1+ / 2+ / 3+** (plus equivocal-region flagging).
- **Results:** ResNet-101 + 7-class: **accuracy 97%, F1 92%, MCC 90%**; class 2+ sensitivity 0.91, class 3+ 0.97. (No AUC/kappa reported.)
- **Code:** on request only.

**(d) Qaiser & Rajpoot 2019 — DRL attention for HER2**
> Qaiser T, Rajpoot NM. *Learning Where to See: A Novel Attention Model for Automated Immunohistochemical Scoring.* **IEEE Transactions on Medical Imaging** 2019; **38**(11):2620–2631. DOI 10.1109/TMI.2019.2907049 · arXiv: <https://arxiv.org/abs/1903.10762>

Treats IHC scoring as a **sequential decision** task: a deep RL agent picks diagnostically relevant ROIs (mimicking a pathologist), then recurrent+residual convnets predict the HER2 score. Evaluated on the public **HER2 scoring challenge** dataset and a Glo1-stained gastroenteropancreatic NET dataset; outperformed state-of-the-art CNNs.

**(e) Lu et al. 2022 — SlideGraph+ (H&E → HER2 status, with DAB-density features)**
> Lu W, Toss M, Dawood M, Rakha E, Rajpoot N, Minhas F. *SlideGraph+: Whole slide image level graphs to predict HER2 status in breast cancer.* **Medical Image Analysis** 2022; **80**:102486. DOI 10.1016/j.media.2022.102486 · <https://www.sciencedirect.com/science/article/pii/S1361841522001335> · Code: <https://github.com/wenqi006/SlideGraph>

- **Relevance to virtual IHC:** it builds a **DAB-density regression model that predicts DAB intensity directly from H&E** (PCC = 0.90, p < 0.0001) and uses those 4 DAB-density features as the single most informative input (AUROC 0.75 ± 0.02 on TCGA-BRCA, beating 2048-dim embeddings).
- **Output:** HER2 status (binary / weakly supervised), not 0/1+/2+/3+.
- **Results:** independent sets — HER2C 0/3+ AUROC 0.78; Nott-HER2 0/3+ AUROC 0.80. Naive DAB pooling gives only 0.598 → the graph structure matters.
- **Code: available.**

### 5.2 ER / PR (Allred)

- **Fauzi et al. 2022 (ER, Allred)** and **Bannah et al. 2026 (PR, Allred)** — full details in §3.2. Both output **per-cell weak/moderate/strong** and a slide-level **Allred score (0–8)**, with the 0/2 vs 3–8 treatment threshold.
- **Allred system origin:** Allred DC, Harvey JM, Berardo M, Clark GM. *Prognostic and predictive factors in breast cancer by immunohistochemical analysis.* **Modern Pathology** 1998; **11**(2):155–168. PMID: 9504686 · <https://pubmed.ncbi.nlm.nih.gov/9504686/> (verified record; the Allred score = proportion score 0–5 + intensity score 0–3).

### 5.3 Ki-67

**(a) TUPAC16 challenge**
> Veta M, Heng YJ, Stathonikos N, Ehteshami Bejnordi B, Beca F, Wollmann T, Rohr K, Shah MA, Wang D, Rousson M, Hedlund M, Tellez D, Ciompi F, Zerhouni E, Lanyi D, Viana M, Kovalev V, Liauchuk V, Phoulady HA, Qaiser T, ... Pluim JPW. *Predicting breast tumor proliferation from whole-slide images: The TUPAC16 challenge.* **Medical Image Analysis** 2019; **54**:111–121. DOI 10.1016/j.media.2019.02.012 · <https://www.sciencedirect.com/science/article/abs/pii/S1361841518305231> · arXiv: <https://arxiv.org/pdf/1807.08284>

- **Task:** predict the pathologist's **mitotic score (1/2/3)** from a whole slide (Task 1) and the **PAM50 proliferation score** (Task 2). 500 train + 321 test WSIs; 12 teams (Task 1), 6 (Task 2).
- **Metrics:** **quadratic-weighted Cohen's kappa** (Task 1), **Spearman** (Task 2), F1 (auxiliary mitosis detection).
- **Results:** best Task-1 κ = **0.567** (LUNIT), 0.543 (MICROSOFT), 0.534 (CONTEXTVISION); best Task-2 Spearman r = **0.617**; best mitosis-detection F1 = 0.652.
- **Relevance:** Ki-67 is named in the paper as an objective alternative to mitotic counting, but TUPAC16 itself scores H&E mitoses, not Ki-67 IHC. (Corrigendum: Med Image Anal 2019;56:43.)

**(b) Dawe et al. 2024 — five DIA methods head-to-head (Laboratory Investigation)**
> Dawe M, Shi W, ... Fyles A, Done SJ. *Reliability and Variability of Ki-67 Digital Image Analysis Methods for Clinical Diagnostics in Breast Cancer.* **Laboratory Investigation** 2024. <https://www.sciencedirect.com/science/article/pii/S0023683724000199>

- **Methods compared:** Aperio ePathology Nuclear v9, Definiens Tissue Studio, **QuPath**, an unsupervised IHC colour-histogram (IHCCH) algorithm, and **piNET** (deep learning). Reference = manual Ki-67 counts (n = 278, TBC trial cohort).
- **Metrics:** Pearson R, **ICC**, **Cohen's κ**, Bland–Altman, % concordance.
- **Results:** piNET best agreement with manual (**ICC 0.850, R 0.85**); QuPath best reproducibility (**ICC 0.889**); Aperio worst (ICC 0.148 vs manual). **No method reached the clinically-relevant κ ≥ 0.80** — best was piNET **κ = 0.73** at 20%/25% cutoffs.
- **Code:** not released as a single repo (piNET is a published pipeline).

**(c) Rewcastle et al. 2024 — prognostic cut-offs & reproducibility (Breast Cancer Res Treat)**
> Rewcastle E, Skaland I, Gudlaugsson E, Fykse SK, Baak JPA, Janssen EAM. *The Ki67 dilemma: investigating prognostic cut-offs and reproducibility for automated Ki67 scoring in breast cancer.* **Breast Cancer Research and Treatment** 2024; **207**(1):1–12. DOI 10.1007/s10549-024-07352-4 · <https://pubmed.ncbi.nlm.nih.gov/38797793/>

367 patients (HR+, HER2−, LN−). Four DIA methods (QuPath, Visiopharm) vs two manual. Reproducibility by **ICC**. Results: manual-vs-DIA ICC > 0.780; **between DIA platforms ICC 0.781–0.906**; DIA had greater prognostic value (HR 3.054–4.077 at 14% cutoff vs 2.012–2.056 manual).

**(d) Ki-67 + AI assistance (Scientific Reports 2024)** — *AI improves accuracy, agreement and efficiency of pathologists for Ki67 assessments in breast cancer.* **Scientific Reports** 2024; **14**:1283. <https://www.nature.com/articles/s41598-024-51723-2> — citation verified; **numeric metrics not retrievable** in this session (publisher bot wall) — flagged in §7.

**(e) Commercial:** Indica Labs **Breast Ki67 AI** (Aperio HALO AP) outputs % Ki67 positive cells and a **Negative / Positive (Strong)** two-class histogram — note this is **binary**, not 3–4 bins. <https://stage.leicabiosystems.com/en-gb/digital-pathology/analyze/aperioaistore/gallery/breast-ki67-ai>

### 5.4 PD-L1

**(a) Wu et al. 2022 (Modern Pathology)**
> Wu J, Liu C, Liu X, Sun W, Li L, Gao N, Zhang Y, Yang X, Zhang J, Wang H, Liu X, Huang X, Zhang Y, Cheng R, Chi K, Mao L, Zhou L, Lin D, Ling S. *Artificial intelligence-assisted system for precision diagnosis of PD-L1 expression in non-small cell lung cancer.* **Modern Pathology** 2022; **35**(3):403–411. DOI 10.1038/s41379-021-00904-9 · <https://pubmed.ncbi.nlm.nih.gov/34518630/>

- **Input:** WSI of the **22C3** assay (and cross-tested on **SP263**).
- **Method:** DL tumour-detection model (accuracy 0.9326, specificity 0.9641) + tumour-cell segmentation → **concrete TPS value**.
- **Output:** continuous **TPS (%)**; clinically bucketed (<1%, 1–49%, ≥50%).
- **Results:** AI TPS vs trained pathologists **R = 0.9429–0.9458** (22C3); AI vs pathologists **R = 0.9787** (SP263). AI assistance improved untrained pathologists' repeatability and efficiency.
- **Code:** not released.

**(b) Ito et al. 2024 (Modern Pathology)**
> Ito H, Yoshizawa A, Terada K, Nakakura A, Rokutan-Kurata M, Sugimoto T, Nishimura K, Nakajima N, Sumiyoshi S, Hamaji M, Menju T, Date H, Morita S, Bise R, Haga H. *A Deep Learning–Based Assay for Programmed Death Ligand 1 Immunohistochemistry Scoring in Non–Small Cell Lung Carcinoma: Does it Help Pathologists Score?* **Modern Pathology** 2024; **37**(6):100485. DOI 10.1016/j.modpat.2024.100485 · <https://modernpathology.org/article/S0893-3952(24)00065-6/fulltext>

- **Method:** U-Net nuclei recognition (tumour vs non-tumour) + DeepLabv3 per-pixel PD-L1 pos/neg → TPS. 584 TMA cores + 47 whole-slide specimens; 3-pathologist consensus ground truth.
- **Output:** continuous **TPS (%)** + overlay image (red = PD-L1+ tumour, blue = PD-L1− tumour, black = non-tumour).
- **Results:** DL mPrecision 0.686, mRecall 0.857, **F1 0.762**. Interobserver **Fleiss κ = 0.581** (3-tier), 0.619 (1% cutoff), 0.794 (50% cutoff). AI-TPS alone agreed with GT 67.6%; AI-assisted pathologists 73.3–87.2% vs 75.8–83.6% for pathologists alone. On **discordant** cases AI assistance significantly improved odds (OR ≈ 1.28–1.29).
- **Code:** not released.

**(c) AI for PD-L1 TPS (Histopathology 2026)** — Webers, Martens, et al. *AI for tumour proportion scoring of programmed death-ligand 1...* **Histopathology** 2026. DOI 10.1111/his.70268 · <https://pubmed.ncbi.nlm.nih.gov/42634001/> — citation verified; details not extracted.

**(d) Automated TPS (MICCAI/MLMI 2020)** — *Automated Tumor Proportion Scoring for Assessment of PD-L1 Expression in Lung Cancer.* MICCAI MLMI 2020, LNCS 12436. DOI 10.1007/978-3-030-59861-7_8 — TPS = TC(+) / (TC(+) + TC(−)).

**(e) Commercial:** Indica Labs **Lung PD-L1 AI** outputs **TPS** with per-cell positive/negative/non-cancer classification; validated for SP263 (3DHistech P1000) and 22C3 (Leica GT450). <https://indicalab.com/clinical-products/lung-pd-l1-ai>

---

## 6. Evaluation metrics (with concrete reported numbers)

| Metric | Where used | Concrete reported values |
|---|---|---|
| **Cohen's κ (unweighted)** | IHC Profiler; Ki-67 DIA | IHC Profiler vs pathologists **κ = 0.843**; piNET best **κ = 0.73** (20%/25% cutoffs); Aperio worst κ = 0.22 |
| **Quadratic-weighted κ** | TUPAC16 Task 1 (mitotic score 1/2/3) | best **κ = 0.567**; 2nd 0.543; 3rd 0.534 |
| **ICC (intraclass correlation)** | Ki-67 DIA; Ki-67 cut-offs | piNET **ICC = 0.850**; QuPath reproducibility **ICC = 0.889**; DIA platforms **ICC 0.781–0.906**; Ki-67 IKWG pathologist-vs-pathologist ICC 0.82, pathologist-vs-IA 0.76–0.79 |
| **Pearson R** | PD-L1 AI; Ki-67; DAB density | PD-L1 AI TPS vs pathologists **R = 0.9429–0.9458** (22C3), **R = 0.9787** (SP263); piNET **R = 0.85**; DAB-density-from-H&E **PCC = 0.90** |
| **Spearman ρ** | AutoIHC H-score; TUPAC16 Task 2 | AutoIHC **ρ = 0.84** (95% CI 0.77–0.89) = inter-observer ρ 0.84; TUPAC16 PAM50 best **r = 0.617** |
| **Correlation coefficient (CC) for H-score regression** | Liu 2019 RAM-CNN | **CC = 0.95**, MAE 21.33 vs human-human CC 0.95, MAE 20.63 |
| **Accuracy / F1 / MCC** | HER2 grading; PR-IHC; PD-L1 DL | Pedraza 2024: **acc 97%, F1 92%, MCC 90%**; PR-IHC nuclei 4-class **macro-F1 0.95**; Ito 2024 DL **F1 0.762**; Wu 2022 tumour detection **acc 0.9326** |
| **AUC / AUROC / AUPR** | HER2 from H&E; mitosis detection | SlideGraph+ HER2C **AUROC 0.78**, Nott-HER2 **0.80**; TUPAC16 mitosis **F1 0.652** |
| **% agreement / concordance** | Allred; PD-L1; IHC Profiler | Fauzi Allred treatment agreement **82.5%**; Bannah Allred exact **70%**, ±1 **86%**, treatment **94%**; IHC Profiler **88.6%**; Ito AI-assisted **73.3–87.2%** |
| **Fleiss κ** | PD-L1 interobserver | **0.581** (3-tier), 0.619 (1%), 0.794 (50%) |
| **Bland–Altman** | Ki-67 DIA | piNET mean diff −0.71 (centred); QuPath −1.2 to −2.5 (slight underestimate); Aperio +9.7 to +21.8 (overestimate) |
| **IoU / Dice** | segmentation stage | PR-IHC nuclei **IoU 0.74**, F1 0.85; cross-dataset ER **IoU 0.60** |
| **MAE / SD** | H-score regression | Liu 2019 RAM-CNN **MAE 21.33, SD 29.14** |

**Benchmark that matters most for a virtual-IHC paper:** report (i) agreement with pathologist scores (ICC / weighted κ / Spearman), and (ii) explicitly compare your automated-vs-pathologist gap against the **pathologist-vs-pathologist** gap. Liu 2019 and AutoIHC both do this and both reach parity — that is the strongest form of the claim.

---

## 7. Master table

| Paper | Year | Biomarker | Input | Method | Output | Produces 0/1+/2+/3+? | Produces H-score? | Code available? | URL |
|---|---|---|---|---|---|---|---|---|---|
| Ruifrok & Johnston, *Anal Quant Cytol Histol* 23(4):291–299 | 2001 | any (DAB/H/E demo) | RGB brightfield | OD + colour deconvolution (stain matrix M, D = M⁻¹) | H, DAB, E OD channels; IOD | No (primitive) | No | NIH Image macros (legacy) | [PDF](https://helios2.mi.parisdescartes.fr/~lomn/Cours/CV/BME/HistoPatho/Quantification_of_histochemical_staining.pdf) |
| Macenko et al., ISBI 2009:1107–1110 | 2009 | H&E (any) | RGB | SVD stain-vector estimation + normalisation | normalised image / stain vectors | No | No | Yes (many) | [DOI](https://doi.org/10.1109/ISBI.2009.5193250) |
| Vahadane et al., IEEE TMI 35(8):1962–1971 | 2016 | H&E (any) | RGB | Sparse NMF stain separation + normalisation | stain density maps + colour basis | No | No | Yes | [IEEE](https://ieeexplore.ieee.org/document/7460968) |
| Reinhard et al., IEEE CG&A 21(5):34–41 | 2001 | any | RGB | mean/σ transfer in ℓαβ | colour-normalised image | No | No | Yes | [IEEE](https://ieeexplore.ieee.org/abstract/document/946629) |
| Varghese et al., PLoS ONE 9(5):e96801 (IHC Profiler) | 2014 | any IHC | RGB ImageJ | OD deconvolution + 4-zone histogram thresholds | 0/1+/2+/3+ zone + weighted score | Yes (zone = 0/1+/2+/3+) | Yes (1·neg%+2·low+3·pos+4·high) | Yes (SourceForge) | [PLoS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0096801) |
| Patel et al., PLoS ONE 17(7):e0271593 (DAB-quant) | 2022 | any DAB | WSI | NRMB pixel scoring + negative-control thresholds (Otsu) | fraction of stained tissue pixels + histogram | No | No | Yes | [PLoS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0271593) |
| Liu et al., IEEE TMI 38(2):377–388 | 2019 | ER, p53, PgR | breast TMA | OD → H-DAB deconvolution → LAMT → 2×U-Net → RAM-CNN regression | continuous H-score | No | Yes | No | [arXiv](https://arxiv.org/abs/1801.06288) |
| Wen et al., Mod Pathol 37(2):100398 | 2024 | any IHC | IHC WSI | DL region recognition (H-only) + per-pixel 4-bin DAB | H-score | No (per-pixel bins) | Yes | No | [SD](https://www.sciencedirect.com/science/article/pii/S0893395223003034) |
| Yin et al., Technol Cancer Res Treat 25:15330338251407734 (AutoIHC) | 2026 | MHC-I (breast) | IHC WSI | MoCo-SM + Triple UNet + VGG16Regression | H-score | No | Yes | **Yes** | [GitHub](https://github.com/YinTuo/AutoIHC) |
| Bankhead et al., Sci Rep 7:16878 (QuPath) | 2017 | any | WSI | stain estimation + cell detection + trainable classification | per-cell classes; scriptable H-score | Yes (trainable) | Yes (scripts) | Yes | [QuPath](https://qupath.github.io) |
| Schmidt et al., MICCAI 2018, LNCS 11071:265–273 (StarDist) | 2018 | nuclei | 2D/3D | star-convex polygon detection | instance masks | No | No | Yes | [GitHub](https://github.com/stardist/stardist) |
| Graham et al., Med Image Anal 58:101563 (HoVer-Net) | 2019 | nuclei types | H&E | multi-branch CNN + HV distance maps | masks + 5 nucleus classes | No | No | Yes (MIT) | [GitHub](https://github.com/TissueImageAnalytics/hover_net) |
| Stringer et al., Nat Methods 18(1):100–106 (Cellpose) | 2021 | cells/nuclei | 2D/3D | flow-based generalist segmentation | instance masks | No | No | Yes | [Nature](https://www.nature.com/articles/s41592-020-01018-x) |
| Carpenter et al., Genome Biol 7(10):R100 (CellProfiler) | 2006 | cells | images | modular pipeline | phenotypes / counts | via pipeline | via pipeline | Yes | [Springer](https://link.springer.com/article/10.1186/gb-2006-7-10-r100) |
| Gamper et al., MICCAI COMPAY 2019, LNCS 11843:11–19 (PanNuke) | 2019 | nuclei | H&E | dataset + baseline models | masks + 5 classes | No | No | Yes | [site](https://jgamper.github.io/PanNukeDataset/) |
| Qaiser et al., Histopathology 72(2):227–238 (HER2 contest) | 2018 | HER2 | IHC (+H&E) WSI, 86 cases | 8+ team algorithms; bespoke agreement-point scoring | HER2 score (0–3+) | Yes | No | data yes / code varies | [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/his.13333) |
| Saha & Chakraborty, IEEE TIP 27(5):2189–2200 (Her2Net) | 2018 | HER2 | IHC | deep seg+classification of membranes & nuclei | HER2 score | Yes (implied) | No | No | [SemanticScholar](https://www.semanticscholar.org/paper/2aca6293ee2c9d442fe1b10bbb9866e21df5410f) |
| Qaiser & Rajpoot, IEEE TMI 38(11):2620–2631 | 2019 | HER2, Glo1 | IHC WSI | deep RL attention + recurrent/residual CNNs | HER2 score | Yes | No | No | [arXiv](https://arxiv.org/abs/1903.10762) |
| Lu et al., Med Image Anal 80:102486 (SlideGraph+) | 2022 | HER2 | H&E WSI (+ DAB-density regression) | GNN on WSI graphs | HER2 status (binary) | No | No | **Yes** | [GitHub](https://github.com/wenqi006/SlideGraph) |
| Pedraza et al., Algorithms 17(3):97 | 2024 | HER2 | IHC WSI, 306 slides | ResNet-101 + 7-class (with 1.5, 2.5) → 5-class | slide score 0/1+/2+/3+ | **Yes** | No | On request | [MDPI](https://www.mdpi.com/1999-4893/17/3/97) |
| Fauzi et al., Diagnostics 12(12):3093 | 2022 | ER | ER-IHC WSI | CNN detection + HSV P/N + 9-layer CNN W/M/S → Allred | per-cell N/W/M/S + Allred 0–8 | Yes (weak/mod/strong) | No (Allred) | No | [MDPI](https://www.mdpi.com/2075-4418/12/12/3093) |
| Bannah et al., Diagnostics 16(9):1295 | 2026 | PR | PR-IHC WSI | Cellpose + DAB deconv + 3 thresholds → 4 classes → Allred | per-cell neg/weak/mod/strong + Allred 0–8 | Yes (4 classes) | No (Allred) | On request (dataset public) | [MDPI](https://www.mdpi.com/2075-4418/16/9/1295) |
| Allred et al., Mod Pathol 11(2):155–168 | 1998 | ER/PR | IHC | manual Allred system (origin) | Allred score 0–8 | No (0–8) | No | n/a | [PubMed](https://pubmed.ncbi.nlm.nih.gov/9504686/) |
| Veta et al., Med Image Anal 54:111–121 (TUPAC16) | 2019 | mitotic score / PAM50 | H&E WSI, 821 slides | 12 team algorithms | mitotic score 1/2/3; PAM50 score | 1/2/3 (not 0–3+) | No | data yes | [SD](https://www.sciencedirect.com/science/article/abs/pii/S1361841518305231) |
| Dawe et al., Lab Invest (Ki-67 DIA) | 2024 | Ki-67 | IHC TMA, n=278 | Aperio / Definiens / QuPath / IHCCH / piNET | % positive cells | No | No | No | [SD](https://www.sciencedirect.com/science/article/pii/S0023683724000199) |
| Rewcastle et al., Breast Cancer Res Treat 207(1):1–12 | 2024 | Ki-67 | IHC WSI, n=367 | QuPath + Visiopharm (4 DIA) vs 2 manual | % positive, cut-offs | No | No | No | [PubMed](https://pubmed.ncbi.nlm.nih.gov/38797793/) |
| Wu et al., Mod Pathol 35(3):403–411 | 2022 | PD-L1 (22C3, SP263) | NSCLC WSI | DL tumour detection + tumour-cell seg | continuous TPS % | No (TPS) | No | No | [PubMed](https://pubmed.ncbi.nlm.nih.gov/34518630/) |
| Ito et al., Mod Pathol 37(6):100485 | 2024 | PD-L1 (22C3) | NSCLC TMA+WSI | U-Net nuclei + DeepLabv3 per-pixel | continuous TPS % | No (TPS) | No | No | [MP](https://modernpathology.org/article/S0893-3952(24)00065-6/fulltext) |
| Klöckner et al., npj Digital Medicine | 2025 | HER2/PgR/ER/Ki-67 | H&E → virtual IHC | review + benchmark of generative models | generated IHC + evaluation | n/a | n/a | varies | [Nature](https://www.nature.com/articles/s41746-025-01741-9) |
| Indica Labs Lung PD-L1 AI | — | PD-L1 (SP263, 22C3) | WSI | proprietary DL | TPS + per-cell classes | No (TPS) | No | commercial | [Indica](https://indicalab.com/clinical-products/lung-pd-l1-ai) |
| Indica Labs Breast Ki67 AI | — | Ki-67 | WSI | proprietary DL | % positive cells (2 classes) | No | No | commercial | [Leica](https://stage.leicabiosystems.com/en-gb/digital-pathology/analyze/aperioaistore/gallery/breast-ki67-ai) |

---

## 8. How to build the pipeline

```
                     ┌──────────────────────────────────────────────────────┐
  RGB IHC image  ──► │ 1. Background / white correction                     │
  (real or virtual)  │    estimate I0 per channel (blank field, 99th pct)   │
                     └──────────────────────────┬───────────────────────────┘
                                                ▼
                     ┌──────────────────────────────────────────────────────┐
                     │ 2. OD conversion                                     │
                     │    OD_c = −log10(I_c / I0_c)      [Beer–Lambert]     │
                     │    → OD image is LINEAR in stain amount              │
                     └──────────────────────────┬───────────────────────────┘
                                                ▼
                     ┌──────────────────────────────────────────────────────┐
                     │ 3. Colour deconvolution                              │
                     │    C = M⁻¹ · OD          (Ruifrok 2001)              │
                     │    M rows: H=(0.65,0.70,0.29), DAB=(0.27,0.57,0.78)  │
                     │    → H channel, DAB channel, residual                │
                     │    (use Macenko/Vahadane to normalise BEFORE this    │
                     │     when slides/generators differ)                   │
                     └──────────────────────────┬───────────────────────────┘
                                                ▼
                     ┌──────────────────────────────────────────────────────┐
                     │ 4. DAB-OD image  (physical stain amount per pixel)   │
                     └──────────────────────────┬───────────────────────────┘
                                                ▼
        ┌───────────────────────────────────────┴──────────────────────────────┐
        │                                                                      │
        ▼ (per-pixel route)                       ▼ (per-cell route — preferred)
┌────────────────────────────┐        ┌──────────────────────────────────────────┐
│ 4a. Threshold DAB OD        │        │ 4b. Nucleus / cell segmentation          │
│   • fixed (IHC Profiler)    │        │   StarDist / HoVer-Net / Cellpose /      │
│   • Otsu                    │        │   QuPath cell detection / CellProfiler   │
│   • negative-control calib. │        │   (tumour-vs-stroma mask first:          │
│     (DAB-quant, 0.1% tol.)  │        │    DeepLabv3 / MoCo-SM)                  │
└─────────────┬──────────────┘        └────────────────────┬─────────────────────┘
              │                                            ▼
              │                          ┌──────────────────────────────────────────┐
              │                          │ 5. Per-cell DAB intensity                │
              │                          │   mean DAB-OD inside each nucleus mask   │
              │                          └────────────────────┬─────────────────────┘
              │                                            ▼
              │                          ┌──────────────────────────────────────────┐
              │                          │ 6. Bin into 3–4 classes                  │
              │                          │   neg / 1+ weak / 2+ moderate / 3+ strong│
              │                          │   thresholds: calibrated on expert ROIs  │
              │                          │   (grid search max macro-F1) then frozen │
              │                          └────────────────────┬─────────────────────┘
              │                                            ▼
              └───────────────────┬────────────────────────┘
                                  ▼
              ┌──────────────────────────────────────────────────────────────┐
              │ 7. Aggregate to a score                                      │
              │   • % positive        = (1++2++3+) / total                   │
              │   • H-score           = 1·%1+ + 2·%2+ + 3·%3+   (0–300)      │
              │   • Allred            = proportion(0–5) + intensity(0–3)     │
              │   • HER2 categorical  = 0/1+/2+/3+ (+ % complete membrane)   │
              │   • TPS (PD-L1)       = TC(+) / (TC(+) + TC(−))              │
              │   • Ki-67 index       = % positive tumour nuclei             │
              └──────────────────────────────────────────────────────────────┘
```

**Six decisions that will determine whether your virtual-IHC scores are believable:**

1. **Normalise before deconvolving.** Put generated IHC into a fixed stain space (Macenko/Vahadane to a real-IHC reference) *before* deconvolution. Otherwise your DAB-OD values are in an arbitrary generator-specific colour basis.
2. **Pick a physical scale for the thresholds.** Calibrate bin thresholds in DAB-OD against a held-out set of **real** IHC slides with pathologist labels — never fit them on generated images.
3. **Per-cell > per-pixel** if you want 0/1+/2+/3+ or Allred; per-pixel is acceptable only for area/H-score-style readouts.
4. **Segment tumour vs stroma first.** Every high-performing system (Wu 2022, Ito 2024, AutoIHC, Fauzi) gates scoring to tumour cells; including stroma contaminates the score.
5. **Report against the human baseline.** Compare your automated-vs-pathologist agreement to the **pathologist-vs-pathologist** agreement (Liu 2019: 0.95 vs 0.95; AutoIHC: ρ 0.84 vs 0.84). That is the claim reviewers accept.
6. **Expect the weak/moderate boundary to be your error source** — both Fauzi (2022) and Bannah (2026) report misclassification concentrated there, and the HER2 contest found the 2+ class hardest for humans and machines alike.

---

## 9. Verification & uncertainty

**Verified with primary sources in this session** (citation string, venue, year, and — where stated — abstract/numbers were read directly):
Ruifrok & Johnston 2001 (full PDF read; stain matrix and D = M⁻¹ values quoted verbatim from the paper); Macenko 2009 (DBLP confirms ISBI 2009:1107–1110; PDF retrieved); Vahadane 2016 (IEEE record confirms TMI 35(8), starts p. 1962); Reinhard 2001 (IEEE record, DOI 10.1109/38.946629); Bankhead/QuPath 2017 (Sci Rep 7:16878); Graham/HoVer-Net 2019 (Med Image Anal 58:101563, confirmed via publisher + GitHub BibTeX); Stringer/Cellpose 2021 (Nat Methods 18(1):100–106); Schmidt/StarDist 2018 (MICCAI, LNCS 11071, DOI 10.1007/978-3-030-00934-2_30); Carpenter/CellProfiler 2006 (Genome Biol 7(10):R100); Gamper/PanNuke 2019 (LNCS 11837/COMPAY, DOI 10.1007/978-3-030-23937-4_2); Varghese/IHC Profiler 2014 (full PLoS article read); Patel/DAB-quant 2022 (full PLoS article read); Liu 2019 (arXiv HTML read — the IEEE TMI volume/pages 38(2):377–388 come from the publisher record, the numbers from the arXiv version); Wen 2024 (abstract read from ScienceDirect + Modern Pathology; article is Mod Pathol 37(2):100398); Yin/AutoIHC 2026 (GitHub README read — citation block and ρ=0.84 verified); Qaiser/HER2 contest 2018 (PubMed record + full arXiv PDF read); Saha/Her2Net 2018 (Semantic Scholar record); Qaiser & Rajpoot 2019 (arXiv abstract + IEEE DOI); Lu/SlideGraph+ 2022 (ScienceDirect read); Pedraza 2024 (MDPI full text read); Fauzi 2022 (MDPI full text read); Bannah 2026 (MDPI full text read); Wu 2022 (PubMed abstract read); Ito 2024 (Modern Pathology full text read); Dawe 2024 (ScienceDirect read); Rewcastle 2024 (PubMed abstract read); Allred 1998 (PubMed record); TUPAC16/Veta 2019 (ScienceDirect abstract + snippets read).

**Could NOT fully verify — treat with care:**

1. **H-score origin (McCarty 1985).** The H-score is universally attributed to **McCarty KS Jr., Miller LS, Cox EB, Konrath J, McCarty KS Sr., "Estrogen receptor analyses: correlation of biochemical and immunohistochemical methods using monoclonal antireceptor antibodies," Arch Pathol Lab Med 1985;109(8):716–721.** I did **not** retrieve and read this primary record in this session — I only found secondary citations (e.g. Asian Arch Pathol technical note, NCBI MedGen H-Score concepts). **Verify this citation before using it.** The *formula* `1×weak% + 2×moderate% + 3×strong%`, range 0–300, is confirmed by Liu 2019 (Eq. 1) and Wen 2024.
2. **Wen et al. 2024 (Mod Pathol) numeric results.** The abstract (pixel accuracy 0.92–0.99, "comparable to experienced pathologists") was read from two sources, but the **full-text correlation/ICC numbers were blocked** by publisher bot protection (ScienceDirect, Modern Pathology, and PMC all refused). The specific agreement statistics are therefore **not quoted** here.
3. **Saha & Chakraborty 2018 (Her2Net) metrics.** Only the Semantic Scholar record was reachable (IEEE TIP paywall). The citation and the fact that it targets HER2 scoring are verified; **architecture details and numeric metrics are not**, and whether it emits an explicit 0/1+/2+/3+ label is **unconfirmed** (the table marks this "implied").
4. **"AI improves accuracy, agreement and efficiency of pathologists for Ki67 assessments in breast cancer," Scientific Reports 2024;14:1283.** Citation verified via multiple index records (ADS bibcode 2024NatSR..14.1283D). **Numeric metrics were not retrievable** (Nature and PMC bot walls).
5. **Webers & Martens, Histopathology 2026, DOI 10.1111/his.70268 (PD-L1 TPS AI)** and the **MICCAI MLMI 2020 automated TPS paper** — citations verified from index records only; **methods and numbers not extracted.**
6. **SlideGraph+ DAB-density regression.** The claim "predicts DAB intensity directly from H&E" and the PCC = 0.90 come from the SlideGraph+ paper's own text (read via ScienceDirect). It is worth noting this is a *feature* model trained against real DAB, i.e. conceptually a shallow precursor to full virtual IHC.
7. **Commercial tools (Indica Labs / Leica).** Descriptions come from **vendor documentation**, not peer-reviewed papers. Their performance claims are not independently verified here.
8. **Bannah et al. 2026** publication year: the MDPI record shows Diagnostics vol 16(9):1295 with a 2026 date. Volume arithmetic (Diagnostics vol 12 = 2022) is consistent, but this is a very recent item — re-check the final issue details if citing formally.
9. **No paper was invented.** Every entry in the master table maps to a URL that was fetched or a PubMed/DOI record that was read. Where a field is unknown it is marked "—", "implied", or "on request" rather than guessed.

**Not covered (out of scope but relevant to virtual IHC):** the npj Digital Medicine 2025 review (*H&E to IHC virtual staining methods in breast cancer: an overview and benchmarking*, Klöckner et al., DOI 10.1038/s41746-025-01741-9) is the obvious companion for how *generated* IHC is currently evaluated; I verified the citation but could not retrieve the full text (Nature bot wall), so its evaluation-metric taxonomy is **not summarised here**. If you want, that is the single highest-value follow-up fetch.
