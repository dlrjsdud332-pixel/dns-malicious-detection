import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

benign_path = "data/Benign/stateless_features-benign_1.pcap.csv"
attack_path = "data/Attack_heavy_Benign/Attacks/stateless_features-heavy_text.pcap.csv"

benign = pd.read_csv(benign_path)
attack = pd.read_csv(attack_path)

print("정상 데이터:", benign.shape)
print("공격 데이터:", attack.shape)

print("\n정상 entropy 평균:", benign["entropy"].mean())
print("공격 entropy 평균:", attack["entropy"].mean())

sns.histplot(benign["entropy"], label="Benign", kde=True)
sns.histplot(attack["entropy"], label="Attack", kde=True)

plt.title("Entropy Distribution: Benign vs Attack")
plt.xlabel("Entropy")
plt.ylabel("Count")
plt.legend()
plt.show()