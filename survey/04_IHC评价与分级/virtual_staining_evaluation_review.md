# Do Virtual-Staining / Virtual-IHC Papers Evaluate TARGET PROTEIN EXPRESSION (not just pixel similarity)?

**Literature review prepared for:** a CV researcher building an H&E → virtual-IHC generative model.
**Core question:** *Do existing virtual-staining / virtual-IHC papers evaluate whether the generated image correctly reproduces the target protein expression, or only pixel/image similarity?*

**Bottom line up front:** Yes — a *minority* of papers do go beyond pixels. Roughly three evaluation "levels" exist beyond PSNR/SSIM/LPIPS:

1. **Stain-channel level** — colour deconvolution into H&E/DAB, then compare DAB optical-density (OD) maps/histograms between generated and real IHC (IOD, mIOD, Pearson-R on DAB, Jensen–Shannon divergence on DAB histograms).
2. **Biomarker-score level** — compute a clinical score (HER2 0/1+/2+/3+, Ki-67 index %, ER/PR positive-nucleus %, positive-cell ratio, or a task-driven "semantic fidelity" score) on the generated IHC and compare with ground-truth IHC.
3. **Pathologist level** — blinded reader studies, visual Turing tests, staining-quality grading, or downstream classifier trained on generated IHC.

The overwhelming majority of pure-ML papers still report only pixel/perceptual metrics. The strongest protein-expression evaluations cluster in a small set: **Ozcan/Bai HER2 (2022), Martino Ki-67 OSCC (2024), Peng/TDKstain HER2 (2024), Chen/PSPStain (2024), Chen/PGVMS (2026), Ma/DSFF-GAN (2024), Pati/VirtualMultiplexer (2024), PixCell (2025), Liu/Star-Diff (2025), Zhang/MVFStain (2022), Zeng PR (2022), VihcGAN (2026), Ji Ki-67 (2024), and the ROSIE mIF (2025).**

---

## 1. Ranked list of the most relevant papers (full citations + URLs)

### Tier A — Evaluate protein-expression / biomarker score AND/OR pathologist scoring on generated IHC

1. **Bai B, Wang H, Li Y, de Haan K, Colonnese F, Wan Y, Zuo J, Doan NB, Zhang X, Zhang Y, Li J, Yang X, Dong W, Darrow MA, Kamangar E, Lee HS, Rivenson Y, Ozcan A.** *Label-Free Virtual HER2 Immunohistochemical Staining of Breast Tissue using Deep Learning.* **BME Frontiers** 2022;2022:9786242. DOI 10.34133/2022/9786242. arXiv:2112.05240. https://spj.science.org/doi/10.34133/2022/9786242
2. **Martino F, Ilardi G, Varricchio S, Russo D, Di Crescenzo RM, Staibano S, Merolla F.** *A deep learning model to predict Ki-67 positivity in oral squamous cell carcinoma.* **Journal of Pathology Informatics** 2024;15:100354. https://www.sciencedirect.com/science/article/pii/S2153353923001682 (PMC10750186)
3. **Peng Q, Lin W, Hu Y, Bao A, Lian C, Wei W, Yue M, Liu J, Yu L, Wang L.** *Advancing H&E-to-IHC Virtual Staining with Task-Specific Domain Knowledge for HER2 Scoring.* **MICCAI 2024**, LNCS 15004:3–13. DOI 10.1007/978-3-031-72083-3_1. https://papers.miccai.org/miccai-2024/051-Paper3227.html (code: https://github.com/balball/TDKstain)
4. **Chen F, Zhang R, Zheng B, Sun Y, He J, Qin W.** *Pathological Semantics-Preserving Learning for H&E-to-IHC Virtual Staining (PSPStain).* **MICCAI 2024**, 384–394. arXiv:2407.03655. https://arxiv.org/abs/2407.03655 (code: https://github.com/ccitachi/PSPStain)
5. **Chen F, Zhang R, Hu W, Abera DE, Peng Y, Zheng B, Sun Y, Cai J, Qin W.** *PGVMS: A Prompt-Guided Unified Framework for Virtual Multiplex IHC Staining with Pathological Semantic Learning.* **IEEE Trans. Medical Imaging** 2026 (in press). arXiv:2602.23292. https://arxiv.org/abs/2602.23292 (code: https://github.com/ccitachi/PGVMS)
6. **Ma Y, Zhang Y, Wang Z, Li J, Miao Y, Yang F, Pan W.** *DSFF-GAN: A novel stain transfer network for generating immunohistochemical image of endometrial cancer.* **Computers in Biology and Medicine** 2024;170:108046. https://www.sciencedirect.com/science/article/pii/S0010482524001306
7. **Pati P, Jaume G, Foncubierta-Rodríguez A, et al.** *Accelerating histopathology workflows with generative AI-based virtually multiplexed tumour profiling (VirtualMultiplexer).* **Nature Machine Intelligence** 2024;6:1077–1093. DOI 10.1038/s42256-024-00889-5. https://www.nature.com/articles/s42256-024-00889-5
8. **Yellapragada S, Graikos A, Li Z, Triaridis K, Belagali V, Nandi TN, Bai K, Knudsen BS, Kurc T, Gupta RR, Prasanna P, Madduri RK, Saltz J, Samaras D.** *PixCell: A generative foundation model for digital histopathology images.* arXiv:2506.05127 (2025). https://arxiv.org/abs/2506.05127
9. **Liu J, Deng X, Li H, Kazemi A, Grashei C, Wilkens G, You X, Groll T, Navab N, Mogler C, Schüffler PJ.** *From pixels to pathology: Restoration diffusion for diagnostic-consistent virtual IHC (Star-Diff).* **Computers in Biology and Medicine** 2025. https://www.sciencedirect.com/science/article/pii/S001048252501618X
10. **Zeng B, Wang H, Zhou J, et al.** *Semi-supervised PR Virtual Staining for Breast Histopathological Images.* **MICCAI 2022**, 232–241. DOI 10.1007/978-3-031-16434-7_23. https://link.springer.com/chapter/10.1007/978-3-031-16434-7_23
11. **Zhang R, et al.** *MVFStain: multiple virtual functional stain histopathology images generation based on specific domain mapping.* **Medical Image Analysis** 2022;80:102520. DOI 10.1016/j.media.2022.102520.
12. **Liu S, Zhu C, Xu F, Jia X, Shi Z, Jin M.** *BCI: Breast Cancer Immunohistochemical Image Generation Through Pyramid Pix2pix.* **CVPR Workshops 2022**, 1815–1824. https://openaccess.thecvf.com/content/CVPR2022W/CVMI/html/Liu_BCI_Breast_Cancer_Immunohistochemical_Image_Generation_Through_Pyramid_Pix2pix_CVPRW_2022_paper.html (dataset: https://bupt-ai-cz.github.io/BCI/)
13. **Liu S, Zhu C, et al.** *Unpaired stain transfer using pathology-consistent constrained generative adversarial networks (PC-StainGAN).* **IEEE Trans. Medical Imaging** 2021;40:1977–1989.
14. **Wang X, et al. (VihcGAN)** *Virtual immunohistochemistry by conditional generative adversarial networks.* **Scientific Reports** 2026;15:32233. DOI 10.1038/s41598-025-32233-1. https://www.nature.com/articles/s41598-025-32233-1 (PMC13451361)
15. **Ji C, Oshima K, Urata T, Kimura F, Ishii K, Uehara T, Suzuki K, Takeyama S, Yamaguchi M.** *Transformation from hematoxylin-and-eosin staining to Ki-67 immunohistochemistry digital staining images using deep learning: experimental validation on the labeling index.* **Journal of Medical Imaging** 2024;11(4):047501. DOI 10.1117/1.JMI.11.4.047501.
16. **Dubey S, Chong Y, Knudsen B, Elhabian SY.** *VIMs: Virtual Immunohistochemistry Multiplex Staining via Text-to-Stain Diffusion Trained on Uniplex Stains.* arXiv:2407.19113 (2024), MICCAI-DGM workshop. https://arxiv.org/abs/2407.19113
17. **Liu P, Meng J, Jiang Y, Li Y, Tian J, Sun B, Ni C, Ye Q.** *AI-enabled virtual immunohistochemistry for real-time molecular inference during intraoperative diagnosis.* **Expert Systems with Applications** 2026;329:133031. https://www.sciencedirect.com/science/article/pii/S0957417426019421
18. **Wang Q, Akram AR, Dorward DA, Talas S, Monks B, Thum C, Hopgood JR, Javidi M, Vallejo M.** *Deep learning-based virtual H&E staining from label-free autofluorescence lifetime images.* **npj Imaging** 2024;2:21. DOI 10.1038/s44303-024-00021-7. (PMC11213708)
19. **DGR authors (HKUST/CUHK)** *Generative AI for misalignment-resistant virtual staining to accelerate histopathology.* **Nature Communications** 2026;17. DOI 10.1038/s41467-026-71038-2. https://www.nature.com/articles/s41467-026-71038-2
20. **ROSIE authors** *ROSIE: AI generation of multiplex immunofluorescence staining from histopathology images.* **Nature Communications** 2025;16. DOI 10.1038/s41467-025-62346-0. https://www.nature.com/articles/s41467-025-62346-0 (bioRxiv: 10.1101/2024.11.10.622859)

### Tier B — Reviews / benchmark / evaluation-methodology papers (the "negative evidence" backbone)

21. **Klöckner P, Teixeira J, Montezuma D, Fraga J, Horlings HM, Cardoso JS, Oliveira SP.** *H&E to IHC virtual staining methods in breast cancer: an overview and benchmarking.* **npj Digital Medicine** 2025;8:384. DOI 10.1038/s41746-025-01741-9. https://www.nature.com/articles/s41746-025-01741-9 ← *the single most useful review for your question; includes a re-benchmark of pyramid Pix2Pix / ASP / PSPStain with JSD on the DAB channel.*
22. **Bai B, Yang X, Li Y, Zhang Y, Pillar N, Ozcan A.** *Deep learning-enabled virtual histological staining of biological samples.* **Light: Science & Applications** 2023;12:57. DOI 10.1038/s41377-023-01104-7.
23. **Latonen L, Koivukoski S, Khan U, Ruusuvuori P.** *Virtual staining for histology by deep learning.* **Trends in Biotechnology** 2024;42(10):1177–1191.
24. **Lin W, Hu Y, Zhu R, Wang B, Wang L.** *Virtual staining for pathology: Challenges, limitations and perspectives.* **Intelligent Oncology** 2025;1(2):105–119. DOI 10.1016/j.intonc.2025.03.005.
25. *Virtual histological staining: toward standardization and clinical translation.* **Biomedical Engineering Letters** 2026. DOI 10.1007/s13534-026-00597-6.
26. **Wang Q, Tweel JED, Haji Reza P, Layton A.** *Pathology-Guided Virtual Staining Metric for Evaluation and Training (PaPIS).* arXiv:2507.12624 (2025). https://arxiv.org/abs/2507.12624
27. **"On the Utility of Virtual Staining for Downstream Tasks"** arXiv:2508.00164 (2025). https://arxiv.org/abs/2508.00164

### Tier C — Foundational / related (autofluorescence→H&E, mIF, datasets)

28. **Rivenson Y, Wang H, Wei Z, de Haan K, Zhang Y, Wu Y, Günaydın H, Zuckerman JE, Chong T, Sisk AE, Westbrook LM, de Haan G, Ozcan A.** *Virtual histological staining of unlabelled tissue-autofluorescence images via deep learning.* **Nature Biomedical Engineering** 2019;3:466–477. DOI 10.1038/s41551-019-0362-y.
29. **Li B, et al.** *Virtual histological staining of unlabeled autopsy tissue.* **Nature Communications** 2024;15:1684. DOI 10.1038/s41467-024-46077-2. arXiv:2308.00920.
30. **Li F, Hu Z, Chen W, Kak A.** *Adaptive Supervised PatchNCE Loss for Learning H&E-to-IHC Stain Translation with Inconsistent Groundtruth Image Pairs (ASP) + MIST dataset.* **MICCAI 2023**, 632–641. arXiv:2303.06193.
31. **Gamble P, et al.** *Determining breast cancer biomarker status and associated morphological features using deep learning.* **Communications Medicine** 2021;1:14. (Not virtual staining, but the reference for the clinical positivity thresholds.)

---

## 2. Master table

| Paper | Year | Venue | Generated stain | Tissue/Cancer | Evaluation metrics used | Protein-expression-level eval? | Pathologist eval? | Statistics used | URL |
|---|---|---|---|---|---|---|---|---|---|
| Bai et al. (Ozcan group) | 2022 | BME Frontiers | Autofluorescence → **HER2 IHC** | Breast | PSNR, SSIM, SSIM_DAB; nucleus/membrane feature metrics (nuclei count, membrane AUC, connectedness) | **Yes** — membrane/nucleus stain features; HER2 score ordering | **Yes** — 3 board-certified breast pathologists, blinded WSI grading (HercepTest 0/1+/2+/3+) | Confusion matrix (22 correct virtual vs 19 IHC; 14 vs 18 errors); two-sided χ²; paired one-sided t-tests (staining quality, 1–4 scale) | https://spj.science.org/doi/10.34133/2022/9786242 |
| Martino et al. | 2024 | J. Pathol. Inform. | H&E → **Ki-67 IHC** | Oral squamous cell carcinoma (TMA) | Pathologist likelihood test; **QuPath IHC positivity quantification**; categorical Ki-67 cut-offs | **Yes** — QuPath positivity %, 3 cut-offs (5/10/15%), PPV | Yes — pathologists recognised synthetic only ~50% of cases | "Remarkable agreement"; high PPV (numbers in full text) | https://www.sciencedirect.com/science/article/pii/S2153353923001682 |
| Peng et al. (TDKstain) | 2024 | MICCAI | H&E → **HER2 IHC** | Breast | PSNR/SSIM/FID/DISTS; nuclei-density error; **membrane-staining-intensity error by HER2 score**; **downstream 4-class membrane-intensity classification** | **Yes** — membrane intensity (4 classes = HER2 scoring) | No reader study (but task-specific domain-knowledge analysis) | ResNet50 classifier ACC 0.7263/F1 0.6795 (generated) vs 0.7228/0.7298 (real) vs 0.4246 (H&E); threshold-sweep membrane-intensity error curves | https://papers.miccai.org/miccai-2024/051-Paper3227.html |
| Chen et al. (PSPStain) | 2024 | MICCAI | H&E → **HER2 IHC** | Breast | PSNR, SSIM + **IOD, mIOD, Pearson-R on DAB (FOD)** | **Yes** — "coherence of protein expression level"; IOD/mIOD/Pearson-R | No | BCI-HER2 Pearson-R 0.7553; MIST-HER2 0.8303; ablation 0.3611→0.6197→0.7553 | https://arxiv.org/abs/2407.03655 |
| Chen et al. (PGVMS) | 2026 | IEEE TMI | H&E → **multiplex IHC** (HER2/ER/PR/Ki67 + HepPar1/EBER/CK/PD-L1) | Breast, colon, liver, NPC, HNSCC | PSNR/SSIM (called non-conclusive), **IOD, Pearson-R, cumulative-OD curves**, FID, DISTS, CONCH-FID; **downstream ViT-B/32 classification with OD cut-offs**; pathologist 1–5 scoring | **Yes** — IOD/Pearson-R per marker; OD-cutoff classification | **Yes** — pathologist 1–5 scale (cellular localization, heterogeneity, intensity) | HER2 4-class acc 0.617; ER 0.772; PR 0.818; Ki67 0.740; blur experiment shows PSNR↑ while biological fidelity↓ | https://arxiv.org/abs/2602.23292 |
| Ma et al. (DSFF-GAN) | 2024 | Comput. Biol. Med. | H&E → **Ki-67 IHC** | Endometrial cancer (+ breast MIST) | SSIM, PSNR, CSS; **"protein expression level" difference between generated and reference Ki-67**; positive-cell-region labels | **Yes** — protein-expression comparison (region-wise positive/negative) | Yes — two pathologists quantified positive-cell ratio per patch vs real patches | "Smallest deviation and lowest variation"; exact stats in full text | https://www.sciencedirect.com/science/article/pii/S0010482524001306 |
| Pati et al. (VirtualMultiplexer) | 2024 | Nature Mach. Intell. | H&E → **multiplex IHC** (AR, NKX3.1, ERG, p53, CD44, CD146) | Prostate (EMPaCT TMA → WSI) | FID, CSS; **visual Turing test**; staining-quality grading; **cell-level positive/negative intensity concordance**; downstream biochemical-recurrence prediction | **Partial** — cell-class intensity distributions & separability; not a clinical score | **Yes** — 4 experts (3 prostate histopath + 1 pathologist) visual Turing test | Sensitivity 52.1%, specificity 54.1% (chance ≈ 50%); 70.7% virtual acceptable vs 78.3% real staining quality | https://www.nature.com/articles/s42256-024-00889-5 |
| Yellapragada, Graikos et al. (PixCell) | 2025 | arXiv | H&E → **IHC** (HER2, ER, PR, Ki67) | Breast (MIST, HER2Match) | FID, FHD, FVD, CLIP-FID, embedding cosine sim; **wF1, mF1, Cohen κ, weighted κ, MCC** on expression labels; pathologist 1–3 quality scoring | **Yes (ER/PR/Ki-67)** — DeepLIIF positive-nucleus % with clinical thresholds (ER ≥10%, PR >1%, Ki67 >30%); **no H-score; no numeric HER2 score** | **Yes** — 2 board-certified pathologists (blinded), 5-criteria 1–3 scale; subtype classification 94.4% match | Cohen's κ, weighted κ, MCC; 95% Wilson CIs; 95% CIs over 5 seeds | https://arxiv.org/abs/2506.05127 |
| Liu et al. (Star-Diff) | 2025 | Comput. Biol. Med. | H&E → **HER2 IHC** | Breast (BCI) | SSIM/PSNR (criticised); **Semantic Fidelity Score (SFS)** = classification-guided class-wise recall degradation; AUROC | **Yes** — diagnostic consistency of HER2 status (2+/3+ vs 0/1+) | No reader study (uses pathologist-annotated classifier labels) | SFS formula; 5px translation → 47.9% SSIM drop; AUROC/SFS robust (≤2.1% drop under deformation) | https://www.sciencedirect.com/science/article/pii/S001048252501618X |
| Zeng et al. | 2022 | MICCAI | H&E → **PgR/PR IHC** | Breast | Image metrics; **positive/negative label consistency via DAB thresholding** | **Yes** — PgR positivity status | **Yes** — pathologist determined concordance of positivity status real vs generated | "High agreement with biomarker status" | https://link.springer.com/chapter/10.1007/978-3-031-16434-7_23 |
| Zhang et al. (MVFStain) | 2022 | Medical Image Analysis | H&E → **HER2, ER, PgR, Ki67 IHC** | Breast (+ lung, heart, vascular) | PSNR, **HTI**, **mIOD (mean integrated optical density)** | **Yes** — mIOD (protein/stain amount) | **Yes** — 2 pathologists, blinded, graded stain quality 1–3 | "Virtual images nearly equal to real" | DOI 10.1016/j.media.2022.102520 |
| Liu et al. (BCI) | 2022 | CVPRW | H&E → **HER2 IHC** | Breast | PSNR, SSIM | **Yes (weak)** — pathologists assessed HER2 expression | **Yes** — 2 pathologists | **<40%** of generated images got the same HER2 expression as real | https://openaccess.thecvf.com/content/CVPR2022W/CVMI/html/Liu_BCI_Breast_Cancer_Immunohistochemical_Image_Generation_Through_Pyramid_Pix2pix_CVPRW_2022_paper.html |
| VihcGAN | 2026 | Scientific Reports | H&E → **CD3 / PAX5 IHC** | Canine lymph node (lymphoma) | PSNR, SSIM, FSIM, FSIMc, VSI; **novel "Stain IoU"** on positive-stained masks; **positive-stained-ratio correlation** | **Yes** — positive-stained area ratio vs real; R² 0.85 (CD3), 0.70 (PAX5) | **Yes** — 2 veterinary pathologists, expert grading | R² vs Pix2pix (0.66/0.61) and CycleGAN (0.32/0.12) | https://www.nature.com/articles/s41598-025-32233-1 |
| Ji et al. | 2024 | J. Med. Imaging | H&E → **Ki-67 IHC** | (Ki-67 labeling index) | **Labeling-index validation** on generated vs real IHC | **Yes** — Ki-67 labeling index | — | Exact stats in full text | DOI 10.1117/1.JMI.11.4.047501 |
| Dubey et al. (VIMs) | 2024 | arXiv (MICCAI-DGM) | H&E → **CDX2 / CK8-18 IHC** (multiplex from uniplex) | Colon (ulcerative colitis) | MSE, SSIM, FID; **DICE/IoU/Hausdorff on DAB-channel masks**; pathologist FP/FN | **Partial** — correct subcellular localisation (nuclear vs cytoplasmic) via DAB masks, not abundance | **Yes** — 2 board-certified pathologists (FP/FN, ranking) | DICE/IoU/Hausdorff | https://arxiv.org/abs/2407.19113 |
| Liu et al. (VSM-MTL) | 2026 | Expert Syst. Appl. | H&E → **IHC-p40** | Lung (BA/CMPT vs adenocarcinoma) | Structural/pixel metrics; **blinded pathologist diagnostic-equivalence** | No quantitative expression metric in abstract | **Yes** — blinded, pathologists rated virtual as "diagnostically equivalent" | No statistics reported in accessible abstract | https://www.sciencedirect.com/science/article/pii/S0957417426019421 |
| Wang et al. (FLIM→H&E) | 2024 | npj Imaging | FLIM → **H&E** (reverse direction) | Lung, colorectal, endometrial | NRMSE, NMI, PSNR, MSSIM; 7 cell-type lifetime signatures | **Yes (biological)** — cell-type-specific lifetime signatures | **Yes** — 3 pathologists, blinded, 12 pairs, 4 criteria, 1–4 scale | Mean scores per pathologist; inter-observer comparison | DOI 10.1038/s44303-024-00021-7 |
| DGR | 2026 | Nature Communications | H&E → **HER2 IHC** (+ PAS-AB) | (breast) | Image-quality metrics; **blinded pathologist discrimination** | No | **Yes** — pathologists 52% accuracy distinguishing virtual from real (= chance) | 52% accuracy | https://www.nature.com/articles/s41467-026-71038-2 |
| ROSIE | 2025 | Nature Communications | H&E → **multiplex immunofluorescence** | 20 tissues/diseases, 16M cells | Cell-phenotype identification from predicted markers; marker localisation | **Yes** — imputes expression & localisation of dozens of proteins | — | Held-out validation of cell phenotypes | https://www.nature.com/articles/s41467-025-62346-0 |
| Rivenson et al. (Ozcan group) | 2019 | Nature Biomed. Eng. | Autofluorescence → **H&E** | (multi-tissue) | PSNR, SSIM, etc. | No | **Yes** — blind comparison by board-certified pathologists | Blind comparison | DOI 10.1038/s41551-019-0362-y |
| Li et al. (autopsy) | 2024 | Nature Communications | Autofluorescence → **H&E** | Autopsy tissue | Image metrics | No | Yes | — | DOI 10.1038/s41467-024-46077-2 |

### Review / methodology rows

| Paper | Year | Venue | What it contributes to the evaluation question | Key statement |
|---|---|---|---|---|
| Klöckner et al. | 2025 | npj Digital Medicine | Review + re-benchmark of H&E→IHC breast models with **JSD on DAB-channel intensity histograms** | "…metrics such as FID or KID … fail at assessing the most important characteristic … whether the pathological information from the source is accurately preserved"; "no method has emerged that can claim to be the golden standard"; "most methods do not provide such [downstream] evaluations" |
| Bai et al. | 2023 | Light Sci. Appl. | 4-level evaluation taxonomy (pixel metrics / feature analysis / pathologist / downstream DNN) | "algorithmic scores cannot always accurately reflect the diagnostic value" |
| Latonen et al. | 2024 | Trends Biotechnol. | Argues computational + histological assessment both required | "optimizing pixelwise metrics does not guarantee satisfactory histology in the output" |
| Lin et al. | 2025 | Intelligent Oncology | Review of models/datasets/**evaluation methods** | Focus on evaluation methods; H&E→IHC HER2 example |
| arXiv 2508.00164 | 2025 | arXiv | Systematic study of whether virtual staining helps downstream tasks | "In most reported studies, virtually stained images have been assessed only using traditional image quality measures"; "traditional IQ measures … may not indicate the utility of an image" |
| Wang et al. (PaPIS) | 2025 | arXiv | Proposes a pathology-aware perceptual metric | "conventional FR-IQA metrics often fail to accurately assess the diagnostic quality of virtual staining images"; notes **absence of expert validation** as its own limitation |

---

## 3. Detailed per-paper notes (top ~13)

### 3.1 Bai et al. 2022 — Label-Free Virtual HER2 IHC (Ozcan group) — *the canonical pathologist-graded virtual-IHC paper*
- **Paper:** Bai B. et al., BME Frontiers 2022;2022:9786242 (arXiv 2112.05240).
- **Year:** 2022.
- **Biomarker:** HER2.
- **Disease-Tissue:** Breast cancer, FFPE sections.
- **Scoring System:** Dako HercepTest 0 / 1+ / 2+ / 3+.
- **Input:** 4-channel autofluorescence (DAPI, FITC, TxRed, Cy5) of **unlabelled** tissue.
- **Method:** cGAN; attention-gated U-Net generator + CNN discriminator.
- **Output:** Bright-field RGB virtual HER2 IHC (~12 s/mm²).
- **Automation level:** Fully automated end-to-end; no pathologist in the loop.
- **Uses 0-1+-2+-3+?** **Yes** — 12 virtual WSIs (3 per HER2 score), each from a unique held-out patient.
- **Uses H-score?** No.
- **Code available?** Yes — https://github.com/baibijie/HER2-virtual-staining
- **Relation to virtual staining:** Label-free → virtual IHC (not H&E → IHC).
- **Transferable to H&E→IHC?** Partially — different input modality, but the **evaluation template (blinded 3-pathologist HercepTest grading + feature-level DAB analysis)** is directly transferable.
- **Value for your research:** This is the clearest existing example of "did the model get the *protein score* right?" — with a confusion matrix, χ² test, and a feature-based (nucleus/membrane) analysis independent of pathologists.

### 3.2 Martino et al. 2024 — Ki-67 in OSCC — *the closest to a clinical biomarker-concordance study*
- **Paper:** Martino F. et al., J Pathol Inform 2024;15:100354.
- **Year:** 2024.
- **Biomarker:** Ki-67.
- **Disease-Tissue:** Oral squamous cell carcinoma; 4 TMAs from 175 cases; **same slide re-stained** H&E then anti-Ki-67 (so pairs are near-perfectly registered).
- **Scoring System:** Ki-67 positivity % with clinical cut-offs 5%, 10%, 15%.
- **Input:** H&E.
- **Method:** Pix2Pix.
- **Output:** Synthetic Ki-67 IHC.
- **Automation level:** Automated generation; **QuPath** for quantification; pathologists for the likelihood test.
- **Uses 0-1+-2+-3+?** No (continuous % + cut-offs).
- **Uses H-score?** No.
- **Code available?** Not stated.
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** **Yes, directly.**
- **Value:** Demonstrates the exact evaluation you want: quantify the biomarker (QuPath positivity %) on synthetic vs genuine IHC, check agreement, and test categorical clinical cut-offs (PPV). Plus a pathologist likelihood test (≈50% = indistinguishable).

### 3.3 Peng et al. 2024 (TDKstain) — HER2 scoring with task-specific domain knowledge
- **Paper:** Peng Q. et al., MICCAI 2024, 3–13 (RegH2I dataset: 2,592 registered H&E-IHC pairs).
- **Year:** 2024.
- **Biomarker:** HER2 (SP3 / CB11 antibodies on external set).
- **Disease-Tissue:** Breast cancer.
- **Scoring System:** 4-class **membrane staining intensity** aligned with HER2 guideline scoring.
- **Input:** H&E.
- **Method:** GAN + nuclei-density estimator + membrane-staining-enhancement branch (uses DAB channel / HED deconvolution).
- **Output:** Virtual HER2 IHC.
- **Automation level:** Fully automated generation; downstream classifier automated.
- **Uses 0-1+-2+-3+?** Effectively yes (4-class membrane intensity).
- **Uses H-score?** No.
- **Code available?** Yes — https://github.com/balball/TDKstain
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** Shows that a classifier trained **only on generated IHC** can score HER2 (4-class) as well as one trained on real IHC (ACC 0.7263 vs 0.7228; F1 0.6795 vs 0.7298), while raw H&E is far worse (ACC 0.4246). This is the strongest "expression-level downstream" evidence.

### 3.4 Chen et al. 2024 (PSPStain) — explicit protein-expression preservation
- **Paper:** Chen F. et al., MICCAI 2024, 384–394 (arXiv 2407.03655).
- **Year:** 2024.
- **Biomarker:** HER2.
- **Disease-Tissue:** Breast (BCI + MIST_HER2).
- **Scoring System:** None clinical; uses continuous DAB-derived OD measures.
- **Input:** H&E.
- **Method:** ASP-based; **Protein-Aware Learning Strategy (PALS)** with **Focal Optical Density (FOD)** map from colour deconvolution; Multi-Level Protein Awareness loss (average / histogram / block).
- **Output:** Virtual HER2 IHC.
- **Automation level:** Fully automated.
- **Uses 0-1+-2+-3+?** No.
- **Uses H-score?** No (uses IOD/mIOD instead).
- **Code available?** Yes — https://github.com/ccitachi/PSPStain
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** Defines the "three clinically relevant metrics" = **IOD, mIOD, Pearson-R on the DAB channel**, explicitly "to assess the pathological correlation with protein expression level rather than just the size of the positive area." Highest Pearson-R (0.7553 BCI, 0.8303 MIST) and lowest IOD/mIOD deviation. Also notes PSNR/SSIM "do not always strictly correlate with high-quality virtual staining results."

### 3.5 Chen et al. 2026 (PGVMS) — unified multiplex + protein-level metrics + pathologist scoring
- **Paper:** Chen F. et al., IEEE TMI 2026 (arXiv 2602.23292).
- **Year:** 2026.
- **Biomarkers:** HER2, ER, PR, Ki67 (MIST, IHC4BC) + HepPar1, EBER, CK, PD-L1 (private clinical).
- **Disease-Tissue:** Breast, colorectal, HCC, NPC, HNSCC.
- **Scoring System:** OD-threshold-based classes — HER2 4-class (OD 500/2000/5000), ER/PR binary (OD 1000), Ki67 binary (OD 2000).
- **Input:** H&E.
- **Method:** Prompt-guided (CONCH vision-language model) + PALS/FOD + prototype consistency.
- **Output:** Multiple virtual IHC stains from one model.
- **Automation level:** Fully automated; labels reviewed by board-certified pathologists.
- **Uses 0-1+-2+-3+?** Yes for HER2 (OD-thresholded).
- **Uses H-score?** No.
- **Code available?** Yes — https://github.com/ccitachi/PGVMS
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** The most complete multi-level evaluation protocol found: PSNR/SSIM (explicitly downgraded), **IOD + Pearson-R + cumulative-OD curves**, FID/DISTS, CONCH-FID, downstream classification with OD cut-offs, and pathologist 1–5 scoring on localization/heterogeneity/intensity. Also reports a **Gaussian-blur experiment showing PSNR/SSIM increase while biological faithfulness decreases** — a clean demonstration that pixel metrics are misleading.

### 3.6 Ma et al. 2024 (DSFF-GAN) — Ki-67, endometrial cancer, pathologist positive-cell ratio
- **Paper:** Ma Y. et al., Comput Biol Med 2024;170:108046.
- **Year:** 2024.
- **Biomarker:** Ki-67.
- **Disease-Tissue:** Endometrial cancer (16 patients) + breast MIST.
- **Scoring System:** Positive-cell ratio (per patch).
- **Input:** H&E.
- **Method:** Cycle-consistency + structure-colour (XYZ) loss, dual-scale feature fusion, pathological feature attention; positive-region labels as prior.
- **Output:** Virtual Ki-67 IHC.
- **Automation level:** Automated generation; **two pathologists quantify positive-cell ratio** per patch.
- **Uses 0-1+-2+-3+?** No.
- **Uses H-score?** No.
- **Code available?** Yes — https://github.com/YihaoMa0512/DSFF-GAN
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** Reports that the generated Ki-67 reproduces "similar positive and negative expressions in the corresponding regions" and that two pathologists' positive-cell ratios showed the "smallest deviation and lowest variation" among models.

### 3.7 Pati et al. 2024 (VirtualMultiplexer) — multiplex IHC + cell-level expression concordance
- **Paper:** Pati P. et al., Nat Mach Intell 2024;6:1077–1093.
- **Year:** 2024.
- **Biomarkers:** AR, NKX3.1, ERG, p53, CD44, CD146.
- **Disease-Tissue:** Prostate cancer (EMPaCT TMA → WSI transfer).
- **Scoring System:** Cell-level positive/negative classification (intensity), not a clinical score.
- **Input:** H&E.
- **Method:** Multiscale GAN with neighbourhood/global/local consistency losses.
- **Output:** Virtually multiplexed IHC (multiple markers from one H&E).
- **Automation level:** Automated generation; experts for Turing test / quality.
- **Uses 0-1+-2+-3+?** No.
- **Uses H-score?** No.
- **Code available?** Yes.
- **Relation to virtual staining:** H&E → IHC (multiplex).
- **Transferable to H&E→IHC?** Yes.
- **Value:** Compares **staining-intensity distributions of positive and negative cells** (concordance + separability) between real and virtual, plus a 4-expert visual Turing test (sensitivity 52.1%, specificity 54.1%) and a downstream biochemical-recurrence prediction using virtual IHC. Strong template for cell-level expression validation.

### 3.8 Yellapragada, Graikos et al. 2025 (PixCell) — foundation model + clinical expression thresholds
- **Paper:** PixCell, arXiv 2506.05127 (2025).
- **Year:** 2025.
- **Biomarkers:** HER2, ER, PR, Ki67 (MIST, HER2Match).
- **Disease-Tissue:** Breast (BRCA), prostate (PRAD).
- **Scoring System:** ER ≥10%, PR >1%, Ki67 >30% positive-nucleus thresholds; HER2 not numerically scored.
- **Input:** H&E (embeddings → rectified flow → diffusion).
- **Method:** Diffusion generative foundation model + LoRA + rectified-flow embedding translation.
- **Output:** Virtual IHC (and H&E).
- **Automation level:** Automated; **DeepLIIF** cell counting; pathologist validation.
- **Uses 0-1+-2+-3+?** No for HER2 (not scored).
- **Uses H-score?** No.
- **Code available?** Yes — https://github.com/cvlab-stonybrook/PixCell
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** Uses **Cohen's κ / weighted κ / MCC** on expression-category labels derived from automated positive-nucleus percentages, plus a blinded 2-pathologist quality study and a 94.4%-concordant subtype classification. Note the honest gap: **HER2 gets no numeric score.**

### 3.9 Liu et al. 2025 (Star-Diff) — "From pixels to pathology"
- **Paper:** Liu J. et al., Comput Biol Med 2025 (PII S001048252501618X).
- **Year:** 2025.
- **Biomarker:** HER2 (binarised 2+/3+ vs 0/1+).
- **Disease-Tissue:** Breast (BCI).
- **Scoring System:** HER2 binary (clinical), plus **Semantic Fidelity Score (SFS)**.
- **Input:** H&E.
- **Method:** Structure-aware staining restoration diffusion model.
- **Output:** Virtual IHC.
- **Automation level:** Automated; uses pathologist-annotated classifier.
- **Uses 0-1+-2+-3+?** Yes (binarised).
- **Uses H-score?** No.
- **Code available?** Not confirmed.
- **Relation to virtual staining:** H&E → IHC.
- **Transferable to H&E→IHC?** Yes.
- **Value:** A **task-driven metric (SFS)** grounded in HER2 classification; explicit quantitative demonstration that SSIM/PSNR are unreliable (5 px shift → 47.9% SSIM drop). This is a model for "evaluate the biomarker, not the pixels."

### 3.10 Klöckner et al. 2025 (npj Digital Medicine) — the review/benchmark to cite
- **Paper:** Klöckner P. et al., npj Digit Med 2025;8:384.
- **What it does:** Reviews 60+ H&E→IHC breast models (HER2, ER, PgR, Ki-67) and **re-benchmarks pyramid Pix2Pix, ASP, PSPStain** on MIST + BCI using LPIPS, FID, SSIM, PSNR and **JSD on the DAB-channel intensity distribution**.
- **Key evaluation statements (verbatim):**
  - "…metrics such as FID or KID are an improvement … but fail at assessing the most important characteristic of a generated image, e.g., whether the pathological information from the source is accurately preserved and highlighted."
  - "Some studies approach this issue by calculating metrics on the DAB channel or getting qualitative assessments by Pathologists, but so far, no method has emerged that can claim to be the golden standard for assessing the performance of preserving pathological information in virtual staining."
  - "While the assessment of downstream tasks is useful and important … **most methods do not provide such evaluations**, which might also be partly due to insufficient virtual staining quality across many methods."
  - On the fundamental assumption: "Pathologists cannot assess whether a cell is expressing HER2 just based on its appearance in an H&E image. Thus … it must be assumed that there are hidden patterns … This fundamental assumption is not necessarily true."
- **Also reports:** Liu et al.'s pyramid Pix2Pix → "when assessed by two pathologists, **less than 40% of the generated images were evaluated with the same HER2 expression** as the corresponding real image."
- **Value for you:** This is your single best citation for "the field's evaluation is dominated by pixel metrics and lacks a protein-expression gold standard."

### 3.11 Zhang et al. 2022 (MVFStain) — earliest multi-stain + mIOD + pathologist
- **Paper:** Zhang R. et al., Med Image Anal 2022;80:102520.
- **Biomarker:** HER2, ER, PgR, Ki67.
- **Method:** Style/content encoders + histogram loss; first to generate multiple IHC stains from H&E.
- **Evaluation:** PSNR, HTI, **mIOD (mean integrated optical density)**, plus **two pathologists blindly graded stain quality 1–3** on both virtual and real sections.
- **Value:** One of the earliest papers to combine an optical-density (protein-amount proxy) metric with blinded pathologist grading.

### 3.12 VihcGAN 2026 (Scientific Reports) — Stain IoU + positive-area correlation
- **Paper:** Sci Rep 2026 (DOI 10.1038/s41598-025-32233-1).
- **Biomarkers:** CD3 (T cells), PAX5 (B cells).
- **Disease-Tissue:** Canine lymph node (lymphoma).
- **Method:** Conditional GAN.
- **Evaluation:** PSNR, SSIM, FSIM, FSIMc, VSI + a **novel "Stain IoU"** computed on positive-stained masks (cell position + positive/negative type) + a sliding-window **positive-stained-ratio correlation** (R² = 0.85 CD3, 0.70 PAX5) + expert grading by 2 veterinary pathologists.
- **Value:** A concrete "stain-level / positive-area" metric that is closer to biology than PSNR, plus a pathologist grading.

### 3.13 Ji et al. 2024 (J. Med. Imaging) — Ki-67 labeling index validation
- **Paper:** Ji C. et al., J Med Imaging 2024;11(4):047501.
- **Biomarker:** Ki-67.
- **Method:** H&E → digital H-DAB Ki-67 IHC.
- **Evaluation:** Explicitly "experimental validation on the **labeling index**" — i.e., the Ki-67 labeling index computed on generated vs real IHC.
- **Value:** Directly on-point for "quantitative biomarker score on generated IHC," and adds to the Ki-67 cluster (Martino, Ma, DSFF-GAN).

---

## 4. Synthesis — "Do any existing virtual-staining papers evaluate protein expression? What exactly did they do? What is still missing?"

### 4.1 Do they evaluate protein expression? — Yes, but in a minority, and at different depths.

**(a) Stain-channel / optical-density level (most common "beyond pixels" approach).**
The chromogen (DAB) concentration is linked to protein expression, so several papers map RGB → HED (haematoxylin-eosin-DAB) via colour deconvolution and compare the **DAB channel**:
- **IOD / mIOD / Pearson-R on DAB** — PSPStain (Chen 2024), PGVMS (Chen 2026), MVFStain (Zhang 2022, mIOD).
- **Jensen–Shannon divergence on DAB-intensity histograms** — Klöckner 2025 benchmark; also used in some reviewed models (e.g., WPCC).
- **DAB-channel mask segmentation (DICE/IoU)** — VIMs (Dubey 2024).
- **DAB intensity distribution matching / membrane-staining-intensity error** — TDKstain (Peng 2024), UNIStainNet (Saurav et al., DAB intensity Pearson-r + DAB KL).
- **Positive-stained-area / Stain IoU** — VihcGAN (2026).

**(b) Biomarker-score level (the "holy grail" — fewer papers).**
- **HER2 0/1+/2+/3+** — Bai 2022 (blinded pathologist HercepTest grading), TDKstain 2024 (4-class membrane intensity via downstream classifier), Zeng/PR (positivity status), Liu/BCI (pathologist HER2 expression, <40% agreement).
- **Ki-67 index / positivity %** — Martino 2024 (QuPath %, 5/10/15% cut-offs, PPV), Ma 2024 (pathologist positive-cell ratio), Ji 2024 (labeling index).
- **ER/PR/Ki-67 clinical thresholds** — PixCell 2025 (DeepLIIF positive-nucleus % with clinical cut-offs; κ/weighted-κ/MCC).
- **Task-driven diagnostic consistency** — Star-Diff 2025 (SFS from HER2 classifier), TDKstain 2024 (downstream HER2 classifier), PGVMS 2026 (OD-cutoff classification).
- **H-score / Allred:** **No virtual-staining paper found that computes a classical H-score or Allred score on generated IHC.** (H-score papers found — e.g., "Deep Learning–Based H-Score Quantification," Modern Pathology 2024 — are *IHC quantification* methods, not virtual-staining evaluation.)

**(c) Pathologist level (common, but usually only "can they tell it's fake / is quality acceptable").**
- **Blinded scoring of the biomarker** — Bai 2022 (3 breast pathologists, HercepTest), Zeng 2022 (PgR positivity concordance), Liu/BCI 2022 (HER2 expression).
- **Visual Turing test** — VirtualMultiplexer (4 experts; sensitivity 52.1%, specificity 54.1%), DGR 2026 (52%), Martino 2024 (≈50%), Martino-style likelihood tests.
- **Staining-quality grading (1–3 / 1–4 / 1–5)** — Bai 2022, MVFStain 2022, VirtualMultiplexer 2024, VIMs 2024, VihcGAN 2026, PGVMS 2026, FLIM→H&E 2024, PixCell 2025.
- **Diagnostic equivalence / subtype** — VSM-MTL 2026 (p40, "diagnostically equivalent"), PixCell 2025 (94.4% subtype concordance).

### 4.2 What exactly did they do? (Representative protocols)
- **Bai 2022:** generate 12 virtual HER2 WSIs (3 per score, held-out patients) → 3 pathologists blindly grade 0/1+/2+/3+ → confusion matrix + two-sided χ² → no significant difference vs real IHC; plus feature-based nucleus/membrane analysis (independent of pathologists).
- **Martino 2024:** re-stain the *same* slide H&E → Ki-67 → train Pix2Pix → pathologist likelihood test (~50% = indistinguishable) → **QuPath quantification of positivity %** → agreement between genuine and synthetic → categorical 5/10/15% cut-offs with PPV.
- **TDKstain 2024:** train a ResNet50 on generated IHC to classify 4 membrane-intensity classes (= HER2 scoring), evaluate on an **external** IHC set; generated-IHC classifier ≈ real-IHC classifier (ACC 0.73 vs 0.72), while H&E alone fails (0.42).
- **PSPStain 2024:** colour-deconvolve DAB → Focal OD map → match average/histogram/block OD between generated and real → report IOD, mIOD, Pearson-R.
- **PGVMS 2026:** same OD philosophy + OD-threshold classification + CONCH-FID + pathologist 1–5 scoring + a blur experiment showing PSNR↑/fidelity↓.
- **VirtualMultiplexer 2024:** compare **positive vs negative cell intensity distributions** between real and virtual + visual Turing test + staining-quality grading + downstream recurrence prediction.

### 4.3 What is still missing (the gaps your work can fill)
1. **No H-score / Allred evaluation on generated IHC.** The clinically standard ER/PR (Allred, H-score) and HER2 (0/1+/2+/3+) scores are essentially never computed as a *primary* virtual-staining metric. IOD/Pearson-R are proxies, not clinical scores.
2. **Most papers report pixel/perceptual metrics only.** The arXiv 2508.00164 study states: "In most reported studies, virtually stained images have been assessed only using traditional image quality measures such as structural similarity or signal-to-noise ratio."
3. **No field-wide benchmark for protein-expression fidelity.** Klöckner 2025: "no method has emerged that can claim to be the golden standard for assessing the performance of preserving pathological information."
4. **No standardisation / no reporting guideline.** The 2026 *Biomedical Engineering Letters* review frames this as a "standardization blueprint" problem; Latonen 2024 lists it as an open question.
5. **Pathologist studies are usually "realism/quality," not "expression correctness."** Only a handful (Bai 2022, Zeng 2022, Liu/BCI 2022, Martino 2024, Ma 2024) ask whether the *biomarker call* is right.
6. **Ki-67 is the best-served biomarker** (Martino, Ma, Ji, plus PixCell); **HER2 is second** (Bai, Peng, Star-Diff, BCI); **ER/PR/PD-L1 have the least direct expression-level validation on generated images.**
7. **Pairing/registration confounds everything.** Consecutive-section datasets (BCI, MIST) cannot support pixel- or cell-level expression scoring; re-stained / same-section datasets (Martino, HER2Match) are the only ones that can — and Klöckner 2025 explicitly calls for more of them.
8. **No work (found) validates that generated DAB intensity *quantitatively* tracks true protein abundance** (e.g., against a biochemical or mIF ground truth) — only against another IHC stain.

**Direct answer to your research question:** *Yes, a minority of papers do evaluate protein expression on generated IHC — via DAB/optical-density metrics (IOD, mIOD, Pearson-R, JSD), via clinical score categories (HER2 0–3+, Ki-67 index, ER/PR positivity thresholds), and via blinded pathologist biomarker scoring or downstream classifiers. But no paper computes a classical H-score/Allred on generated IHC, and the field still lacks a standardised, protein-expression-level benchmark. Most papers remain pixel-metric-driven.*

---

## 5. Verification & uncertainty

**Verified via full text retrieved and read during this review:** Klöckner et al. 2025 (npj Digit Med, full PDF); Bai et al. 2023 (Light Sci Appl, full PDF); Pati et al. 2024 (VirtualMultiplexer, full PDF); Peng et al. 2024 (TDKstain, full PDF from papers.miccai.org); Chen et al. 2024 (PSPStain, arXiv HTML v2); Chen et al. 2026 (PGVMS, arXiv HTML); Dubey et al. 2024 (VIMs, arXiv HTML); VihcGAN 2026 (Sci Rep, full PDF); arXiv 2508.00164 (full PDF); arXiv 2507.12624 (HTML); Bai et al. 2022 (abstract + evaluation details via ScienceDirect mirror); Liu et al. 2022 (CVPRW abstract + bibliographic record); Liu et al. 2025 (Star-Diff, ScienceDirect abstract/section snippets).

**Verified at abstract/metadata level only (full text behind paywall or bot-blocked):**
- **Martino et al. 2024** (J Pathol Inform) — abstract confirms QuPath positivity quantification and 5/10/15% cut-offs, but the exact agreement statistics (correlation/ICC) and PPV values are in the full text, which was not retrievable (NCBI/PMC blocked, PDF mirror corrupted). **The abstract claims "remarkable levels of agreement" and "high positive-predictive values" without numbers in the abstract.**
- **Ma et al. 2024 (DSFF-GAN)** — the phrase "To further evaluate the difference in protein expression levels between the generated Ki-67 stained images and the …" appears in the ScienceDirect snippet, and Klöckner et al. 2025 independently reports that two pathologists quantified positive-cell ratio per patch. Exact statistics not confirmed.
- **Ji et al. 2024** (J Med Imaging) — title confirms "experimental validation on the labeling index"; full numeric results not retrieved (SPIE page blocked).
- **Zeng et al. 2022** (MICCAI PR) — bibliographic record and Klöckner's summary confirm pathologist positivity concordance; primary full text not retrieved (Springer blocked).
- **Liu et al. 2026** (VSM-MTL, p40) — pathologist "diagnostic equivalence" is a qualitative claim in the abstract; **no statistics were available** in the accessible content.
- **ROSIE 2025** (Nat Commun) — abstract confirms protein-expression imputation and phenotype validation; detailed metrics not retrieved (Nature blocked; bioRxiv abstract obtained).
- **Lin et al. 2025** (Intelligent Oncology) — abstract/highlights confirm a focus on "models, datasets, and evaluation methods"; **full text not retrievable** (ScienceDirect paywall + mirrors blocked), so I could not extract exact sentences.
- ***Virtual histological staining: toward standardization and clinical translation*** (Biomed Eng Lett 2026) — citation and framing verified via search results; **full text not retrieved** (Springer PDF blocked).
- **DGR 2026** (Nat Commun) — abstract confirms pathologists' 52% discrimination accuracy; detailed evaluation not fully extracted.
- **Wang et al. 2024** (npj Imaging FLIM→H&E) — verified via PMC mirror summary; this is the reverse direction (→H&E), included for the pathologist-evaluation template.

**Could not verify / do not cite as confirmed:**
- I found **no paper** that computes a classical **H-score** or **Allred score** on virtually generated IHC. If such a paper exists, I did not find it through the specified search terms. Treat "no H-score virtual-staining paper found" as a *negative* result of this search, not proof of non-existence.
- The exact **DOI for Ji et al. 2024** is reported as 10.1117/1.JMI.11.4.047501 (consistent with the SPIE URL); I did not open the DOI resolver to confirm.
- **arXiv:2602.23292 (PGVMS)** and **arXiv:2603.12716 (UNIStainNet)** use arXiv ID prefixes (2602/2603) that imply February/March 2026 — consistent with the "TMI 2026 in press" status, but these are very recent and the identifiers should be re-checked against arXiv directly.
- Author lists for **DGR 2026** and **ROSIE 2025** were not fully extracted (only the framing was); I have listed them as "DGR authors" / "ROSIE authors" rather than inventing names.
- **VihcGAN** first-author name was not confirmed from the retrieved text (PMC mirror was blocked; only the Sci Rep PDF text was read). I have therefore not asserted a first author.

**Papers referenced inside reviews but not independently opened** (cited from Klöckner et al. 2025 reference list, which is reliable): Liu et al. 2021 PC-StainGAN (IEEE TMI 40:1977–1989); Zhang et al. 2022 MVFStain (Med Image Anal 80:102520); Wei et al. 2024 DeReStainer; Li et al. 2024 Confusion-GAN (CVPR); He et al. 2024 PST-Diff (IEEE TMI 43:3634–3647); Li et al. 2024 WPCC; Wang et al. 2024 MDCL; Zhang et al. 2024 PPT; Li et al. 2023 ASP/MIST (arXiv 2303.06193). Their evaluation characteristics are as summarised by Klöckner et al.
