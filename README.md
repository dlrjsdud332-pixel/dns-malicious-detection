# DNS Malicious Behavior Detection

CIC-Bell-DNS-EXF-2021 데이터셋을 활용하여 정상 DNS 통신과 DNS를 이용한 비정상 데이터 전송 및 터널링 행동을 분석하고, 머신러닝·딥러닝 기반 탐지 모델을 비교한 프로젝트입니다.

## 1. 프로젝트 목표

- 정상 DNS 행동과 비정상 DNS Query 차이 분석
- DNS Tunneling 및 DNS 기반 Data Exfiltration 특성 분석
- Stateless / Stateful DNS Feature 비교
- 통계적 유의성 검정 및 Effect Size 분석
- 다양한 머신러닝 모델 비교
- DNN 기반 분류 모델 확장
- INT8 Quantization을 통한 경량화 가능성 검토
- 향후 실시간 보안 관제 시스템에 부착 가능한 탐지 모듈 기반 마련

## 2. Dataset

- Dataset: CIC-Bell-DNS-EXF-2021
- 주요 분석 대상
  - Benign DNS
  - Text
  - Audio
  - Image
  - Video
  - Compressed
  - EXE

대표 실험에서는 정상 DNS와 Heavy Text Attack 데이터를 이용하여 Binary Classification을 수행했습니다.

> 현재 모델 성능은 전체 공격 유형을 통합한 최종 일반화 성능이 아니라, 대표 Normal vs Heavy Text 비교 실험 결과입니다.

## 3. Main Features

### Stateless Features

- FQDN_count
- subdomain_length
- numeric
- entropy
- special
- labels
- labels_max
- labels_average
- len

### Stateful Features

- ttl_mean
- ttl_variance
- unique_ttl_count

## 4. EDA & Statistical Analysis

### Mann–Whitney U Test

Normal vs Heavy Text 비교에서 9개 Stateless Feature에 대해 Mann–Whitney U Test를 수행했습니다.

Benjamini–Hochberg FDR 보정을 적용했으며 모든 Feature가 통계적으로 유의했습니다.

다만 표본 수가 크기 때문에 p-value만으로 판단하지 않고 Effect Size를 함께 확인했습니다.

주요 Effect Size:

| Feature | Effect Size |
|---|---:|
| FQDN_count | -0.544 |
| numeric | -0.535 |
| subdomain_length | -0.524 |
| special | -0.513 |
| labels | -0.508 |
| labels_average | 0.327 |
| len | -0.303 |
| labels_max | 0.039 |
| entropy | 0.038 |

FQDN_count, numeric, subdomain_length, special, labels는 Normal과 Attack을 구분하는 상대적으로 강한 차이를 보였습니다.

반면 entropy와 labels_max는 통계적으로 유의했지만 Effect Size가 매우 작아 실제 구분력은 제한적이었습니다.

### Kruskal–Wallis Test

Normal, Text, Audio, Image, Video, Compressed, EXE 총 7개 그룹을 대상으로 Kruskal–Wallis Test를 수행했습니다.

주요 Epsilon-Squared:

| Feature | Epsilon² |
|---|---:|
| special | 0.316 |
| labels | 0.309 |
| FQDN_count | 0.211 |
| numeric | 0.205 |
| subdomain_length | 0.197 |
| labels_average | 0.076 |
| len | 0.066 |
| labels_max | 0.002 |
| entropy | 0.001 |

Binary 비교에서는 FQDN_count가 강하게 나타났지만, 여러 공격 유형을 함께 비교했을 때는 special과 labels의 차이가 더 크게 나타났습니다.

### Stateful Statistical Analysis

| Feature | Effect Size | Direction |
|---|---:|---|
| ttl_mean | 0.636 | Normal > Attack |
| ttl_variance | 0.313 | Normal > Attack |
| unique_ttl_count | -0.301 | Attack > Normal |

특히 ttl_mean은 대표 Binary 비교에서 Stateless Feature보다 큰 차이를 보여 Stateful Feature 활용 가능성을 확인했습니다.

## 5. Models

### Supervised Learning

- Logistic Regression
- RandomForest
- XGBoost
- LightGBM
- HistGradientBoosting

### Unsupervised Learning

- IsolationForest

### Deep Learning

- Dense 64 + ReLU
- Dropout 0.3
- Dense 32 + ReLU
- Dropout 0.2
- Dense 16 + ReLU
- Dense 1 + Sigmoid

총 파라미터 수: **3,265**

## 6. Model Comparison

| Model | Accuracy | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| RandomForest | 0.7163 | 0.5519 | 0.9969 | 0.7105 | 0.4343 | 0.7824 | 0.5549 |
| XGBoost | 0.7163 | 0.5519 | 0.9972 | 0.7106 | 0.4344 | 0.7825 | 0.5553 |
| LightGBM | 0.7162 | 0.5519 | 0.9969 | 0.7105 | 0.4344 | 0.7826 | 0.5554 |
| LogisticRegression | 0.7144 | 0.5510 | 0.9850 | 0.7066 | 0.4308 | 0.7789 | 0.5479 |
| HistGradientBoosting | 0.7163 | 0.5519 | 0.9970 | 0.7105 | 0.4343 | 0.7827 | 0.5554 |
| DNN | 0.7155 | 0.5511 | 0.9989 | 0.7103 | 0.4366 | 0.7836 | 0.5558 |
| IsolationForest | 0.5354 | 0.2084 | 0.1181 | 0.1507 | 0.2406 | - | - |

### Interpretation

Supervised 모델들은 Accuracy와 F1 기준으로 약 0.71 수준의 유사한 성능을 보였습니다.

DNN은 가장 높은 Recall, ROC-AUC, PR-AUC를 보였지만 FPR 역시 약 0.44로 높았습니다.

따라서 현재 실험에서는 모델 종류 자체를 변경하는 것만으로 False Positive 문제가 해결되지는 않았으며, Feature 개선, Threshold 조정, Dataset 구성 개선이 추가로 필요합니다.

IsolationForest는 현재 Normal과 Attack이 섞인 학습 데이터를 사용한 Baseline 실험이므로 성능이 낮게 나타났습니다. 향후 정상 데이터만 이용한 재학습이 필요합니다.

## 7. RandomForest Feature Importance

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

통계분석에서 차이가 크게 나타난 Feature들이 RandomForest Feature Importance에서도 대체로 상위에 위치하여 두 분석 결과가 전반적으로 일치했습니다.

## 8. INT8 Quantization

DNN 모델을 TensorFlow Lite INT8 모델로 변환했습니다.

- INT8 TFLite model size: **9.16 KB**
- INT8 Accuracy: **0.7156**
- INT8 Precision: **0.5511**
- INT8 Recall: **0.9994**
- INT8 F1: **0.7105**

FP32 DNN과 비교했을 때 성능 저하는 거의 나타나지 않았습니다.

### Local CPU Latency Benchmark

Single-sample inference 기준:

| Model | Avg Latency | Median Latency |
|---|---:|---:|
| FP32 Keras DNN | 1.461 ms/sample | 1.393 ms/sample |
| INT8 TFLite | 0.00184 ms/sample | 0.00175 ms/sample |

INT8 TFLite가 현저히 낮은 latency를 보였지만, FP32는 Keras runtime, INT8은 TFLite runtime을 사용했기 때문에 이 차이를 순수한 Quantization 효과만으로 해석하지 않았습니다.

경량 배포 환경에서 INT8 모델의 실행 효율 가능성을 확인한 결과로 해석했습니다.

## 9. Project Structure

```text
dns-malicious-detection/
├── data/
├── notebooks/
│   ├── CIC-Bell-DNS-EXF-2021_DNS_Security_EDA.ipynb
│   └── CIC-Bell-DNS-EXF-2021_DNS_Security_ML.ipynb
├── results/
│   ├── images/
│   ├── feature_importance.csv
│   ├── model_comparison.csv
│   ├── dnn_int8_comparison.csv
│   └── dnn_int8.tflite
├── src/
├── .gitignore
├── README.md
└── requirements.txt
```

## 10. Current Progress

- [x] 대표 Dataset 구조 확인
- [x] Stateless DNS Security EDA
- [x] Stateful DNS Feature 비교
- [x] Attack Type 확장 EDA
- [x] Feature Correlation 분석
- [x] Mann–Whitney U Test
- [x] Benjamini–Hochberg FDR
- [x] Effect Size 분석
- [x] Kruskal–Wallis Test
- [x] Logistic Regression
- [x] RandomForest
- [x] XGBoost
- [x] LightGBM
- [x] HistGradientBoosting
- [x] IsolationForest Baseline
- [x] DNN
- [x] Model Comparison
- [x] Confusion Matrix
- [x] ROC-AUC 분석
- [x] PR-AUC 분석
- [x] FPR 분석
- [x] RandomForest Feature Importance
- [x] INT8 Quantization
- [x] Local CPU Latency Benchmark
- [x] 결과 CSV 및 대표 이미지 저장
- [ ] 전체 Attack Type 통합 모델 검증
- [ ] Stateful + Stateless 통합 모델
- [ ] False Positive 개선
- [ ] 정상 데이터 기반 IsolationForest 재실험
- [ ] Threshold 최적화
- [ ] 실시간 탐지 모듈 패키지화

## 11. Limitations

- 현재 주요 분류 모델은 Normal vs Heavy Text 대표 Binary 실험입니다.
- 전체 공격 유형에 대한 일반화 성능으로 해석할 수 없습니다.
- 대규모 표본에서는 매우 작은 차이도 통계적으로 유의하게 나타날 수 있으므로 Effect Size를 함께 고려했습니다.
- 일부 Feature는 상관관계 또는 중복 정보가 존재할 수 있습니다.
- `distinct_ip`는 현재 데이터에서 실질적인 분석에 활용하기 어려웠습니다.
- `unique_ttl_count`는 `unique_ttl` 필드에서 파싱한 항목 수를 이용한 파생 Feature입니다.
- INT8 latency 결과는 로컬 Mac CPU 환경 및 서로 다른 Runtime에 영향을 받으므로 절대적인 하드웨어 성능 비교로 해석하지 않습니다.

## 12. Conclusion

본 프로젝트에서는 DNS 트래픽의 Stateless 및 Stateful Feature를 분석하고, 통계적 검정과 머신러닝·딥러닝 모델을 이용하여 악성 DNS 행동 탐지 가능성을 확인했습니다.

통계분석에서는 FQDN_count, numeric, subdomain_length, special, labels 및 ttl_mean이 주요 구분 Feature로 확인되었습니다.

다양한 Supervised 모델은 유사한 성능을 보였으며, DNN 역시 기존 Tree 기반 모델 대비 큰 성능 향상을 보이지 않았습니다. 이는 현재 성능 한계가 단순히 모델 종류보다는 데이터 구성, Feature 설계 및 Decision Threshold와 더 밀접할 가능성을 보여줍니다.

또한 DNN을 INT8 TFLite로 변환했을 때 분류 성능을 거의 유지하면서 경량 배포 가능성을 확인했습니다.

향후에는 전체 공격 유형 통합 학습, Stateful + Stateless Feature 결합, False Positive 개선 및 실시간 보안 관제 시스템 연동을 진행할 예정입니다.
