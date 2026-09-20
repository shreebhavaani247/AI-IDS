# AI-Based Hybrid Intrusion Detection System for Cloud Networks

A cloud-based Hybrid Intrusion Detection System (IDS) that combines **Aho-Corasick signature-based detection** with **XGBoost-based anomaly classification** to detect known and anomalous network threats from cloud traffic.

## Overview

Cloud environments are continuously exposed to cyber threats such as DDoS attacks, brute-force attacks, port scanning, botnet activity, web attacks, and infiltration attempts.

Traditional Intrusion Detection Systems generally use either:

- **Signature-based detection** — Effective for known attacks but unable to detect previously unseen attack patterns.
- **Anomaly-based detection** — Capable of identifying abnormal traffic behavior but may introduce additional computational overhead and false positives.

This project proposes a **Hybrid Intrusion Detection System** that combines both approaches in a unified detection pipeline.

The system captures live network traffic from an **AWS EC2 environment**, processes the traffic into network-flow features, performs high-speed signature matching using the **Aho-Corasick algorithm**, and analyzes traffic not identified by known signatures using an **XGBoost machine-learning classifier** trained on the **CICIDS2017 dataset**.

A monitoring dashboard is used to visualize network activity and detected threats.

## Objectives

- Detect known attacks using signature-based detection.
- Detect anomalous network behavior using machine learning.
- Combine signature-based and anomaly-based detection in a single pipeline.
- Capture and analyze live network traffic from AWS EC2.
- Train and evaluate the anomaly detection model using CICIDS2017.
- Provide visualization of detected attacks and network activity.
- Reduce unnecessary machine-learning processing through signature-based triage.

## System Architecture

```text
                    AWS EC2 Instance
                           │
                           ▼
                  Live Network Traffic
                           │
                           ▼
                    Packet Capture
                           │
                           ▼
                    Flow Generation
                           │
                           ▼
                   Feature Extraction
                           │
                           ▼
                  Data Preprocessing
                           │
                           ▼
             ┌─────────────────────────┐
             │   Aho-Corasick Layer    │
             │   Signature Detection   │
             └────────────┬────────────┘
                          │
                  Signature Match?
                    /           \
                  YES            NO
                   │              │
                   ▼              ▼
                 ALERT         XGBoost
                                  │
                                  ▼
                         Attack Classification
                                  │
                                  ▼
                         Detection Result
                                  │
                                  ▼
                              Dashboard
```

## System Workflow

### 1. Live Traffic Acquisition

The system captures live network traffic from an AWS EC2 environment.

The captured traffic provides real network data for monitoring and analysis instead of relying exclusively on static datasets.

### 2. Packet and Flow Processing

Raw network traffic is converted into structured network-flow information.

Relevant traffic characteristics are extracted to represent the behavior of each communication flow.

Representative features include:

- Flow duration
- Packet count
- Byte count
- Packet length statistics
- Forward and backward traffic statistics
- Inter-arrival time characteristics

### 3. Data Preprocessing

The extracted flow data is prepared for machine-learning analysis.

The preprocessing pipeline includes:

- Handling missing values
- Handling infinite values
- Removing zero-variance features
- Correlation-based feature reduction
- Feature selection
- Class-imbalance handling using ADASYN during model training

### 4. Layer 1 – Aho-Corasick Signature Detection

The first detection layer uses the **Aho-Corasick multi-pattern matching algorithm**.

A collection of known malicious signatures is represented using a Trie-based finite-state structure with failure links.

Incoming traffic is checked against multiple signatures efficiently.

```text
Incoming Traffic
       │
       ▼
Aho-Corasick Engine
       │
       ├── Signature Match ──► Malicious Alert
       │
       └── No Match ─────────► XGBoost Layer
```

If a known signature is detected, the traffic is immediately flagged as malicious.

If no signature is matched, the traffic is forwarded to the XGBoost anomaly detection layer.

### 5. Layer 2 – XGBoost Anomaly Detection

Traffic not detected by the signature layer is analyzed using an **XGBoost classifier**.

The model is trained using the **CICIDS2017 dataset** and performs multi-class attack classification.

The classification categories include:

- Benign
- DDoS
- Port Scan / Probe
- Botnet
- Web Attack
- Infiltration
- Brute Force / Patator traffic

The model analyzes network-flow features and produces an attack classification for incoming traffic.

### 6. Alert Generation

When malicious traffic is identified, the system records relevant detection information such as:

- Timestamp
- Source information
- Destination information
- Attack category
- Detection method
- Classification result
- Confidence/probability information where applicable

### 7. Dashboard Visualization

The detection results are displayed through a monitoring dashboard.

The dashboard provides visibility into:

- Network traffic
- Total traffic analyzed
- Detected attacks
- Attack categories
- Detection events
- Classification results

This allows security analysts to monitor the cloud environment and inspect detected threats.

## Technologies Used

| Category             | Technology                                |
| --------------------- | ------------------------------------------ |
| Programming Language | Python                                    |
| Signature Detection  | Aho-Corasick                              |
| Machine Learning     | XGBoost                                   |
| Dataset              | CICIDS2017                                |
| Cloud Platform       | AWS                                       |
| Cloud Instance       | Amazon EC2                                |
| Data Processing      | Pandas, NumPy                             |
| ML Support           | Scikit-learn                              |
| Class Balancing      | ADASYN                                    |
| Traffic Capture      | Packet Capture / Network Monitoring Tools |
| Visualization        | Monitoring Dashboard                      |
| Version Control      | Git / GitHub                              |

## Dataset

### CICIDS2017

The **CICIDS2017** dataset from the Canadian Institute for Cybersecurity is used for training and evaluating the anomaly detection component.

The dataset contains realistic benign traffic and multiple attack scenarios, including:

- Brute Force FTP/SSH
- DoS
- DDoS
- Web Attacks
- Botnet
- Infiltration
- Port scanning/probing

The dataset provides a large number of network-flow features suitable for machine-learning-based intrusion detection.

## Data Preprocessing

The CICIDS2017 data is processed before model training.

### Data Cleaning

- Remove missing values.
- Handle infinite values.
- Remove features with no predictive variation.

### Feature Reduction

Highly correlated features are identified and redundant attributes are removed to reduce dimensionality and improve computational efficiency.

### Feature Selection

Statistical relevance and tree-based feature importance are used to identify useful features for classification.

### Class Balancing

**ADASYN (Adaptive Synthetic Sampling)** is applied to the training data to improve the representation of minority attack classes.

## Machine Learning Model

### XGBoost

**XGBoost (Extreme Gradient Boosting)** is used as the anomaly classification model.

It is suitable for:

- Structured network-flow data
- High-dimensional feature spaces
- Multi-class classification
- Fast inference
- Regularized gradient boosting

The model learns relationships between network-flow characteristics and attack categories using the CICIDS2017 dataset.

## Signature Detection

### Aho-Corasick Algorithm

Aho-Corasick is a multi-pattern string matching algorithm.

Instead of checking each attack signature independently, it constructs a pattern-matching automaton using:

- Trie structure
- Failure links
- Matching/output states

This allows multiple known attack signatures to be searched efficiently within incoming traffic.

### Role in the Project

The Aho-Corasick layer acts as the first stage of the Hybrid IDS:

```text
Known Attack Pattern
        │
        ▼
 Aho-Corasick Engine
        │
        ▼
 Malicious Alert
```

Traffic that does not match known signatures is forwarded to the XGBoost anomaly detection layer.

## Why a Hybrid IDS?

The two detection approaches complement each other.

| Detection Method | Strength                                                             | Limitation                                                         |
| ----------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Aho-Corasick      | Fast detection of known signatures                                   | Cannot identify unknown patterns without corresponding signatures |
| XGBoost           | Learns complex traffic patterns and classifies multiple attack types | Requires feature extraction and model inference                    |
| Hybrid Approach   | Combines signature detection with ML-based classification            | Requires integration of both detection stages                      |

The resulting pipeline provides two levels of threat detection:

```text
Known Threats
     │
     ▼
Aho-Corasick
     │
     ▼
Fast Signature Detection


Unmatched / Anomalous Traffic
     │
     ▼
XGBoost
     │
     ▼
Attack Classification
```

## Cloud Integration

The project uses **AWS EC2** to provide a cloud environment for live traffic capture and monitoring.

```text
AWS EC2
   │
   ▼
Live Network Traffic
   │
   ▼
Packet Capture
   │
   ▼
Feature Extraction
   │
   ▼
Hybrid IDS
   │
   ├── Aho-Corasick
   │
   └── XGBoost
        │
        ▼
 Detection Results
        │
        ▼
    Dashboard
```

## Performance Evaluation

The XGBoost anomaly detection component was evaluated using the CICIDS2017 benchmark dataset.

The associated research evaluation reported high classification performance for major attack categories:

| Attack Category               | Reported Accuracy |
| ------------------------------ | ------------------: |
| DDoS                          |            99.62% |
| Patator / FTP-SSH Brute Force |            99.40% |

The evaluation considers standard IDS performance metrics including:

- Accuracy
- Precision
- Recall
- F1-Score
- False Positive Rate (FPR)

> **Note:** The reported accuracy values correspond to the XGBoost anomaly-detection evaluation described in the associated research work. They should not be interpreted as the measured accuracy of the complete live hybrid pipeline unless separately evaluated.

## Key Features

- Hybrid signature and anomaly detection
- Aho-Corasick multi-pattern matching
- XGBoost-based attack classification
- CICIDS2017-based model training
- Live AWS EC2 traffic monitoring
- Network-flow feature extraction
- Data preprocessing and feature optimization
- ADASYN-based class balancing
- Multi-class attack classification
- Real-time monitoring dashboard

## Project Structure

```text
AI-Hybrid-IDS/
│
├── data/
│   ├── CICIDS2017/
│   └── processed/
│
├── aho_corasick/
│   ├── signatures/
│   └── detector.py
│
├── xgboost_model/
│   ├── preprocessing.py
│   ├── train.py
│   ├── predict.py
│   └── model/
│
├── packet_capture/
│   └── capture.py
│
├── pipeline/
│   └── hybrid_pipeline.py
│
├── dashboard/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

> The exact directory structure may vary depending on the final organization of the implementation.

## Getting Started

### Prerequisites

Make sure the following are installed:

- Python 3.9+
- pip
- Git
- AWS account for cloud traffic testing
- Required Python packages

### Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the System

### Train the XGBoost Model

```bash
python xgboost_model/train.py
```

### Run the Aho-Corasick Detector

```bash
python aho_corasick/detector.py
```

### Run the Hybrid Pipeline

```bash
python pipeline/hybrid_pipeline.py
```

### Launch the Dashboard

If the dashboard uses Streamlit:

```bash
streamlit run dashboard/app.py
```

> Update the commands above according to the actual filenames and entry points in the repository.

## Security and Ethical Considerations

This project is intended for **authorized cybersecurity research, education, and defensive security monitoring**.

Live traffic capture should only be performed on systems and networks for which the user has explicit authorization.

The project should not be used to monitor or inspect third-party network traffic without appropriate permission.

## Research

This project is associated with the research work:

**"AI-Based Hybrid Intrusion Detection System for Cloud Networks: A High-Fidelity Architecture Combining Aho-Corasick Signature Detection and Gradient-Boosted Anomaly Classification."**

The research explores the integration of deterministic signature detection, machine-learning-based anomaly classification, and cloud-based traffic monitoring.

## Future Enhancements

Potential future extensions include:

- Deep-learning-based anomaly detection
- Automated model retraining
- Real-time adaptive thresholds
- SIEM integration
- Automated incident response
- Intrusion Prevention System (IPS) capabilities
- Hardware acceleration for high-throughput signature matching
- Expanded cloud deployment and orchestration
- Continuous monitoring across multiple cloud instances

## Contributors

**P. Keerthana**
**Dr. S. Rahmath Nisha**
**Sajitha V**
**P. Shree Bhavaani**

Department of Computer Science
SRM Institute of Science and Technology, Tiruchirappalli

## License

This project is developed for academic and research purposes.

Add an appropriate open-source license if the project is intended to be publicly reused or distributed.
