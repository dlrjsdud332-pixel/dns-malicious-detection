# On-Device Network Threat Intelligence AI

대규모 네트워크 보안 데이터를 분석하고 공격 행동을 탐지하는 **경량 Machine Learning 기반 Security AI**를 개발하는 팀 프로젝트입니다.

단순 IDS 분류 모델 구축을 넘어 **데이터 분석 → ML → 모델 해석 → Feature Reduction → On-Device Benchmark → Security AI 연동**까지 하나의 파이프라인으로 구현하는 것을 목표로 합니다.

현재 프로젝트는 다음 두 보안 데이터셋을 중심으로 진행합니다.

- **CSE-CIC-IDS2018**: Network Attack Classification
- **CIC-Bell-DNS-EXF-2021**: DNS Malicious Behavior Detection

최종적으로 개발된 모델은 **Autonomous SOC Agent**와 **Drone On-Device Cybersecurity Module**에 재사용 가능한 Security AI 형태로 확장하는 것을 목표로 합니다.

---

## Project Pipeline

```text
Security Dataset
      ↓
Data Quality Analysis
      ↓
EDA & Attack Behavior Analysis
      ↓
Feature Engineering
      ↓
Train / Validation / Test Design
      ↓
ML Training
      ↓
Explainability
      ↓
Feature Reduction
      ↓
Model Comparison
      ↓
On-Device Benchmark
      ↓
Security AI Adapter
      ↓
Autonomous SOC Agent / Drone AI
```

---

## Dataset

### 1. CSE-CIC-IDS2018

네트워크 Flow 기반 **Multi-Class Attack Classification**에 사용합니다.

주요 분석 대상은 Flow Duration, Packet/Byte Rate, Packet Length, IAT, TCP Flags, Active/Idle Time 등입니다.

주요 공격 유형:

- Bot
- Brute Force - Web / XSS
- DDoS HOIC / LOIC
- DoS Hulk / GoldenEye / SlowHTTPTest / Slowloris
- FTP-BruteForce
- SSH-Bruteforce
- Infilteration
- SQL Injection

통합 데이터 기준:

- **16,232,943 flows**
- **15 classes**
- **78 model features**
- Benign 약 **83.07%**
- 심각한 Class Imbalance 존재
- 일부 동일 Feature Vector에서 서로 다른 Label이 관측됨

현재 Network Classification 파트에서는 Feature Reduction과 다중 모델 비교를 수행했으며, Validation 기준 **LightGBM Top40**을 우선 후보 모델로 유지하고 있습니다.

---

### 2. CIC-Bell-DNS-EXF-2021

정상 DNS 통신과 DNS를 이용한 비정상 데이터 전송 및 터널링 행동의 차이를 분석합니다.

주요 분석 대상:

- 정상 DNS 행동
- 비정상 DNS Query
- DNS Tunneling
- DNS 기반 Data Exfiltration
- 시간 Window 기반 DNS 행동

현재 DNS 파트에서는 대표 정상 데이터와 Heavy Text 공격 데이터를 중심으로 1차 EDA 및 ML 모델 비교를 완료했습니다.

사용 모델:

**Supervised**
- RandomForest
- XGBoost
- LightGBM

**Unsupervised**
- IsolationForest

두 접근법을 비교하여 알려진 공격 패턴 분류와 라벨에 의존하지 않는 이상행동 탐지의 역할 차이를 확인합니다.

---

## Analysis & Modeling

### 1. Data Quality Analysis

두 데이터셋을 바로 모델에 입력하지 않고 먼저 데이터 품질을 분석합니다.

주요 확인 항목:

- 데이터 크기
- Feature 수 및 데이터 타입
- 결측치
- ±Inf
- 중복 데이터
- 이상값
- Label 분포
- 클래스 불균형
- Feature 분포
- Feature 상관관계

CSE-CIC-IDS2018 통합 데이터에서 확인한 주요 결과:

```text
Rows                : 16,232,943
Classes             : 15
NaN                 : 59,721
±Inf                 : 131,799
Generic Duplicates  : 422,815
Benign Ratio        : 83.07%
```

---

## Network Security EDA

Network Traffic EDA에서는 다음 영역을 분석했습니다.

- Class Distribution
- Traffic Volume
- Flow Duration
- Packet / Byte Rate
- Packet Length
- Inter Arrival Time
- TCP Flags
- Active / Idle Behavior
- Feature Correlation
- Attack / Benign Feature Distribution

공격 트래픽은 하나의 단순한 임계값으로 구분되는 것이 아니라 공격 유형에 따라 서로 다른 네트워크 행동 특성을 보였습니다.

대표적인 높은 상관관계 Feature Pair:

```text
RST Flag Cnt ↔ ECE Flag Cnt
Flow Duration ↔ Fwd IAT Tot
Idle Mean ↔ Idle Min
Tot Bwd Pkts ↔ TotLen Bwd Pkts
Pkt Len Mean ↔ Pkt Size Avg
Flow IAT Max ↔ Fwd IAT Max
Flow Pkts/s ↔ Fwd Pkts/s
```

이 결과는 이후 Feature Reduction 실험의 근거로 활용했습니다.

---

## Duplicate & Label Conflict Analysis

CSE-CIC-IDS2018 분석 과정에서 **동일한 78개 Feature Vector가 서로 다른 Label을 갖는 패턴**을 확인했습니다.

```text
Conflicting Patterns      : 22,373
Affected Rows             : 423,390
Max Labels per Pattern    : 3
```

대표적인 Label Conflict:

```text
SlowHTTPTest ↔ FTP-BruteForce
Benign ↔ Infilteration
FTP-BruteForce ↔ SSH-Bruteforce
SlowHTTPTest ↔ SSH-Bruteforce
Brute Force-Web ↔ SQL Injection
```

일부 클래스는 높은 Conflict Ratio를 보였습니다.

```text
FTP-BruteForce       : 90.60%
SlowHTTPTest         : 55.24%
Infilteration        : 25.64%
SQL Injection        : 10.34%
```

Conflict Sample을 임의로 제거하여 성능을 높이기보다, 해당 구조적 문제를 보존한 상태에서 평가하도록 설계했습니다.

---

## Split Redesign

### Feature-Only Hash Split V2

동일 Feature Vector가 서로 다른 Split으로 이동하지 않도록 다음 기준으로 Split을 재설계했습니다.

```text
hash(78 model features)
```

분할 결과:

```text
Train : 11,416,137
Valid :  2,390,002
Test  :  2,426,804
Total : 16,232,943
```

Feature Overlap 검증:

```text
Train ↔ Valid : 0
Train ↔ Test  : 0
Valid ↔ Test  : 0
```

최종 모델 선택 전까지 **Test V2는 모델 선택 및 Hyperparameter 조정에 사용하지 않습니다.**

---

## Unique-Pattern V3

일부 공격 클래스에서 특정 Feature Pattern이 수천 번 반복되는 문제를 확인하여 Feature 기준 Unique Pattern Dataset을 별도로 구성했습니다.

```text
Train : 702,217
Valid : 142,082
```

이 실험은 기존 데이터의 발생 빈도를 재현하는 것이 아니라 **새로운 Feature Pattern에 대한 Generalization**을 분석하기 위한 실험입니다.

---

## Network Machine Learning

현재 비교한 모델:

- XGBoost
- RandomForest
- HistGradientBoosting
- LightGBM

### XGBoost Baseline

Full 78 Feature 기반 XGBoost V3 Validation 결과:

```text
Accuracy        : 0.945546
Macro Precision : 0.841778
Macro Recall    : 0.854829
Macro F1        : 0.846377
Weighted F1     : 0.945503
```

---

## Feature Reduction

Feature Importance를 기준으로 Full78 → Top40 → Top20 → Top10 실험을 수행했습니다.

| Feature Set | Feature Count | Macro F1 |
|---|---:|---:|
| Full | 78 | 0.846377 |
| **Top40** | **40** | **0.859573** |
| Top20 | 20 | 0.849831 |
| Top10 | 10 | 0.808544 |

78개에서 40개로 약 **49%의 Feature를 제거했지만 Macro F1은 증가**했습니다.

따라서 이후 모델 비교에서는 **Top40 Feature Set**을 공통 입력으로 사용했습니다.

---

## Network Model Comparison

동일한 Top40 Feature와 V3 Train/Validation Dataset을 사용하여 모델을 비교했습니다.

| Model | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|
| RandomForest Top40 | 0.942991 | 0.825171 | 0.942943 |
| HistGradientBoosting Top40 | 0.941294 | 0.844567 | 0.941231 |
| XGBoost Top40 | 0.943117 | 0.859573 | 0.943070 |
| **LightGBM Top40** | **0.945792** | **0.876563** | **0.945745** |

현재 Validation 기준 가장 높은 Macro F1은 **LightGBM Top40**에서 확인되었습니다.

> 위 결과는 Unique-pattern V3 Validation 결과이며 최종 Test 성능이 아닙니다.

---

## Ensemble Experiment

XGBoost와 LightGBM Soft Voting을 비교했습니다.

| Model | Accuracy | Macro F1 |
|---|---:|---:|
| **LightGBM Top40** | 0.945792 | **0.876563** |
| LGBM50 + XGB50 | 0.946095 | 0.864666 |
| LGBM80 + XGB20 | 0.946256 | 0.863183 |
| LGBM70 + XGB30 | **0.946453** | 0.861869 |
| XGBoost Top40 | 0.943117 | 0.859573 |

Soft Voting은 Accuracy를 높였지만 Macro F1이 감소했습니다.

따라서 Class Imbalance와 희소 공격 클래스 성능을 고려하여 현재 단계에서는 **LightGBM Top40 단일 모델**을 Validation 후보 모델로 유지합니다.

---

# DNS Security EDA

현재 DNS 분석은 대표 정상 DNS 데이터와 Heavy Text 공격 데이터를 중심으로 수행했습니다.

사용한 주요 Stateless Feature:

- `FQDN_count`
- `subdomain_length`
- `numeric`
- `entropy`
- `special`
- `labels`
- `labels_max`
- `labels_average`
- `len`

대표 평균 비교:

| Feature | Normal | Attack |
|---|---:|---:|
| FQDN_count | 18.447 | 25.331 |
| subdomain_length | 4.020 | 8.070 |
| numeric | 3.972 | 8.927 |
| entropy | 2.439 | 2.442 |
| special | 3.296 | 5.682 |
| labels | 3.840 | 5.715 |
| len | 11.277 | 13.174 |

Stateful 대표 비교에서는 TTL 관련 Feature에서도 차이가 확인되었습니다.

| Feature | Normal | Attack |
|---|---:|---:|
| ttl_mean | 92.196 | 12.152 |
| ttl_variance | 2.807 | 0.003 |
| unique_ttl_count | 2.526 | 3.758 |

EDA 결과 `numeric`, `subdomain_length`, `FQDN_count`, `special`, `labels` 등이 정상/공격 구분 후보 Feature로 확인되었습니다.

대표 EDA 이미지:

- `results/images/correlation_heatmap.png`
- `results/images/numeric_distribution_kde.png`
- `results/images/subdomain_length_boxplot.png`

---

# DNS Machine Learning

대표 정상 DNS와 Heavy Text 공격 데이터를 이용하여 1차 모델 비교를 수행했습니다.

사용한 Feature:

```text
FQDN_count
subdomain_length
numeric
entropy
special
labels
labels_max
labels_average
len
```

## DNS Model Comparison

| Model | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| RandomForest | 0.7163 | 0.5519 | 0.9969 | 0.7105 |
| XGBoost | 0.7163 | 0.5519 | 0.9972 | 0.7106 |
| LightGBM | 0.7162 | 0.5519 | 0.9969 | 0.7105 |
| IsolationForest | 0.5354 | 0.2084 | 0.1181 | 0.1507 |

### Interpretation

RandomForest, XGBoost, LightGBM은 매우 유사한 결과를 보였습니다.

세 지도학습 모델 모두 공격 Recall이 약 **0.997**로 매우 높아 테스트 데이터의 공격 샘플 대부분을 탐지했습니다.

반면 Precision은 약 **0.552** 수준으로 정상 DNS를 공격으로 잘못 판단하는 False Positive가 많이 발생했습니다.

따라서 현재 DNS 모델은 공격 탐지 민감도는 높지만 False Positive 개선이 필요한 상태입니다.

IsolationForest는 라벨을 사용하지 않는 비지도 이상탐지 Baseline으로 비교했으며 현재 설정에서는 지도학습 모델보다 낮은 공격 탐지 성능을 보였습니다.

IsolationForest는 향후 **정상 행동 중심 학습 및 알려지지 않은 이상행동 탐지** 관점에서 추가 검증할 예정입니다.

---

## DNS Feature Importance

RandomForest Feature Importance 상위 Feature:

| Feature | Importance |
|---|---:|
| FQDN_count | 0.3244 |
| subdomain_length | 0.2370 |
| special | 0.2145 |
| labels | 0.0972 |
| numeric | 0.0580 |
| labels_average | 0.0338 |
| len | 0.0163 |
| entropy | 0.0118 |
| labels_max | 0.0071 |

EDA에서 확인된 주요 Feature 후보 중 일부가 RandomForest에서도 높은 중요도를 보여 EDA와 모델링 결과가 일부 연결되는 것을 확인했습니다.

대표 ML 결과 이미지:

- `results/images/confusion_matrix_rf.png`
- `results/images/confusion_matrix_xgb.png`
- `results/images/confusion_matrix_lgbm.png`
- `results/images/confusion_matrix_iso.png`
- `results/images/feature_importance_rf.png`

---

## DNS Analysis Limitations

현재 DNS 분석은 다음 한계를 가집니다.

- 대표 정상 데이터와 Heavy Text 공격 중심의 1차 분석
- 전체 Attack Type에 대한 모델 일반화 검증 미완료
- 현재 IsolationForest는 정상 데이터만으로 학습한 구조가 아님
- 지도학습 모델에서 높은 False Positive 발생
- Stateful Feature를 포함한 통합 모델 비교 미완료
- Light / Heavy 및 여러 Payload Type에 대한 추가 검증 필요

따라서 현재 결과를 CIC-Bell-DNS-EXF-2021 전체 공격 유형에 대한 최종 성능으로 일반화하지 않습니다.

---

## Evaluation Strategy

클래스 불균형을 고려하여 Accuracy만으로 모델을 평가하지 않습니다.

Classification:

- Precision
- Recall
- F1 Score
- Macro F1
- Weighted F1
- Confusion Matrix
- PR-AUC
- ROC-AUC
- False Positive Rate

Anomaly Detection:

- Precision
- Recall
- F1
- False Positive Rate
- False Negative Rate
- PR-AUC

특히 보안 시스템 특성을 고려하여 **Attack Recall과 False Positive Rate**를 중요하게 분석합니다.

---

## Explainability & Lightweight AI

Feature Importance와 필요 시 SHAP을 활용하여 모델이 어떤 네트워크 특징을 기반으로 공격을 판단했는지 분석합니다.

최종 후보 모델은 탐지 성능뿐 아니라 실제 디바이스 비용까지 함께 측정합니다.

```text
Full Features
      ↓
Reduced Features
      ↓
Lightweight Model
      ↓
F1 / Recall / FPR
Latency / RAM / CPU / Model Size
```

---

## On-Device Benchmark

최종 후보 모델에 대해 다음 항목을 실제 측정할 예정입니다.

- Model Size
- RAM Usage
- CPU Usage
- Average Inference Latency
- P95 Inference Latency
- Throughput
- Feature Extraction Time

측정되지 않은 성능 수치는 사용하지 않습니다.

---

## Integration

최종 모델은 독립적인 ML 모델로 끝내지 않고 기존 **Autonomous SOC Agent**의 Security AI 입력으로 연결하는 것을 목표로 합니다.

```text
Network / DNS
      ↓
Lightweight Security AI
      ↓
Security Signal
      ↓
Multi-Model Evidence Fusion
      ↓
Autonomous SOC Agent
```

각 모델의 원래 Score 의미와 Evidence Provenance를 유지하며 probability와 anomaly score를 단순 합산하여 임의의 공격 확률을 만들지 않습니다.

---

## Drone AI Extension

동일한 경량 ML 구조를 향후 **Drone On-Device Cybersecurity Module**로 확장할 계획입니다.

적용 가능 대상:

- Drone ↔ Ground Control Station 통신
- Drone ↔ Edge Server 통신
- 드론 내부 네트워크
- 드론이 사용하는 IP 기반 서비스

CSE-CIC-IDS2018 및 CIC-Bell-DNS-EXF-2021에서 학습한 결과를 직접 드론 환경의 탐지 성능으로 간주하지 않습니다.

드론 적용 단계에서는 별도의 Drone Network Dataset 또는 Testbed를 통해 Domain Shift를 검증합니다.

---

## Current Progress

### CSE-CIC-IDS2018

- [x] 데이터 수집
- [x] CSV 통합 및 스키마 정리
- [x] 데이터 품질 분석
- [x] 클래스 불균형 분석
- [x] Network Traffic EDA
- [x] Feature 분포 및 상관관계 분석
- [x] Preprocessing
- [x] Duplicate Pattern 분석
- [x] Label Conflict 분석
- [x] Feature-only Hash Split V2
- [x] Train / Valid / Test Feature Overlap 검증
- [x] Unique-pattern V3 Dataset 구축
- [x] XGBoost Baseline
- [x] Feature Importance
- [x] Feature Reduction
- [x] RandomForest 비교
- [x] HistGradientBoosting 비교
- [x] LightGBM 비교
- [x] XGBoost + RandomForest Ensemble
- [x] XGBoost + LightGBM Ensemble
- [x] Validation Candidate 선정
- [ ] 추가 Model Diversity 실험
- [ ] Conflict-aware Final Evaluation
- [ ] Untouched Test V2 Evaluation
- [ ] PR-AUC / ROC-AUC / FPR 분석
- [ ] On-Device Benchmark

### CIC-Bell-DNS-EXF-2021

- [x] 대표 Dataset 구조 확인
- [x] Stateless DNS Security EDA
- [x] Stateful DNS Feature 비교
- [x] Attack Type 확장 EDA
- [x] Feature Correlation 분석
- [x] RandomForest
- [x] XGBoost
- [x] LightGBM
- [x] IsolationForest Baseline
- [x] Model Comparison
- [x] Confusion Matrix
- [x] RandomForest Feature Importance
- [x] 결과 CSV 및 대표 이미지 저장
- [ ] 전체 Attack Type 통합 모델 검증
- [ ] Stateful + Stateless 통합 실험
- [ ] False Positive 개선
- [ ] 정상 중심 IsolationForest 재실험
- [ ] PR-AUC / ROC-AUC / FPR 분석

### Integration

- [ ] Security AI Adapter
- [ ] SOC Agent Integration
- [ ] On-Device Benchmark
- [ ] Drone AI Prototype

---

## Tech Stack

`Python` · `Pandas` · `NumPy` · `Scikit-learn` · `XGBoost` · `LightGBM` · `Matplotlib` · `Seaborn` · `PyArrow` · `Jupyter` · `uv`

---

## Repository Structure

```text
project/
├── notebooks/
│   ├── CIC-Bell-DNS-EXF-2021_DNS_Security_EDA.ipynb
│   └── CIC-Bell-DNS-EXF-2021_DNS_Security_ML.ipynb
├── results/
│   ├── model_comparison.csv
│   ├── feature_importance.csv
│   └── images/
│       ├── confusion_matrix_rf.png
│       ├── confusion_matrix_xgb.png
│       ├── confusion_matrix_lgbm.png
│       ├── confusion_matrix_iso.png
│       ├── feature_importance_rf.png
│       ├── correlation_heatmap.png
│       ├── numeric_distribution_kde.png
│       └── subdomain_length_boxplot.png
├── src/
├── requirements.txt
└── README.md
```

대용량 원본 데이터와 학습된 Model Artifact는 Git 저장소에서 제외합니다.

---

## Next Steps

```text
Network Final Evaluation
        ↓
DNS Full Attack-Type Validation
        ↓
False Positive Reduction
        ↓
Explainability
        ↓
Feature Reduction
        ↓
On-Device Benchmark
        ↓
Security AI Adapter
        ↓
SOC Agent Integration
        ↓
Drone AI Extension
```

---

## Goal

> **대규모 네트워크 및 DNS 보안 데이터에서 공격 행동의 특징을 발견하고, 실제 제한된 환경에서 실행 가능한 경량 Security AI로 발전시킬 수 있는가?**

데이터 분석, Machine Learning, Cybersecurity, Explainable AI, On-Device AI 및 AI Agent Integration을 하나의 프로젝트에서 연결하는 것을 최종 목표로 합니다.
