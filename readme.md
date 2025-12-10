# Traffic Intersection Simulation (DES) | 十字路口交通流離散事件模擬

**Project:** Final Project - Traffic Intersection Analysis

[English Version](#english-version) | [Chinese Version](#中文說明)

---

<a name="english-version"></a>
## 🇬🇧 English Version

### Project Description
This project implements a Discrete Event Simulation (DES) model for a specific 4-way traffic intersection using Python. The simulation models the interaction between vehicles and pedestrians under a specific traffic light cycle logic. It aims to analyze traffic congestion, queue lengths, and waiting times to evaluate intersection performance.

> **Note:** The core simulation libraries (`SimClasses.py`, `SimFunctions.py`, `SimRNG.py`) were provided by the course instructor. The logic implementation (`main.py`, `visualversion.py`) is the original work for this project.

### 🚦 Intersection Layout
The simulation models the intersection of **Guangfu Rd.** and **Jiangong Rd.** (near NTHU/Qingye):

```text
          │ NTHU  |
          │  (3)  |
          │   ↓   |
 ─────────┘       └─────────
 Interchange (1) →      ← (2) Downtown 
 ─────────┐       ┌─────────
          │   ↑   |
          │  (4)  |
          │ Qingye|
```

  * **Road 1:** Guangfu Rd. (Eastbound from Interchange)
  * **Road 2:** Guangfu Rd. (Westbound from Downtown)
  * **Road 3:** Jiangong Rd. (Southbound from NTHU)
  * **Road 4:** Jiangong Rd. (Northbound from Qingye)
  * **Directions:** Straight (s), Right Turn (r), Left Turn (l)

### ⚙️ Simulation Mechanism

#### 1\. Traffic Light Cycle (State Machine)

The simulation uses a state machine (`traffic_state`) to control the signals. One full cycle consists of 5 states:

| State | Duration | Description |
| :--- | :--- | :--- |
| **0** | 93s | Guangfu Rd. (1 & 2) Green. |
| **1** | 20s | Guangfu Rd. (1 & 2) Left Turn Green. |
| **2** | 12s | Jiangong Rd. (3 & 4) Red, but Pedestrian Green. |
| **3** | 14s | Jiangong Rd. (3 & 4) Green. |
| **4** | 12s | Jiangong Rd. (3 & 4) Green, Pedestrian Red. |

#### 2\. Statistical Distributions

Based on `main.py`, the following distributions are used:

  * **Vehicle Arrival:** Exponential Distribution.
  * **Vehicle Pass-through Time:** Normal Distribution (Separated into "Warm-up/Start-up" and "Saturation" phases).
  * **Pedestrian Arrival:** Exponential Distribution.
  * **Pedestrian Walking Time:** LogNormal Distribution.

#### 3\. Simulation Parameters

  * **Replications (`n_reps`):** 30 times
  * **Run Length:** 10,800 seconds (3 hours) per replication
  * **Warm-up Period:** 3,600 seconds (1 hour)
      * *Statistics collected during the warm-up period are discarded.*

### 📂 File Structure

| File Name | Description |
| :--- | :--- |
| **`main.py`** | **Main Entry Point.** Contains simulation logic, event handling, and statistical analysis (Matplotlib). |
| **`visualversion.py`** | **Real-time Visualization.** Runs the simulation in the terminal with an ASCII-based dashboard to visualize queues. |
| **`SimClasses.py`** | *Instructor Provided.* Core classes (Entity, EventCalendar, FIFOQueue, Stat objects). |
| **`SimFunctions.py`** | *Instructor Provided.* Helper functions for scheduling and clearing stats. |
| **`SimRNG.py`** | *Instructor Provided.* Random Number Generator (LCG algorithm). |
| **`requirements.txt`** | List of dependencies. |

### 🚀 Usage

#### 1. Install Dependencies
Requires Python 3.10+ (due to `match-case` syntax).

```bash
pip install -r requirements.txt
```

#### 2\. Run Statistical Simulation

To run the simulation and generate statistical plots:

```bash
python main.py
```

  * This will run 30 replications.
  * It generates **Convergence plots** and **CI (Confidence Interval) Bar charts** in the `figure/` directory.

#### 3\. Run Visual Simulation

To see the traffic flow in real-time (ASCII animation):

```bash
python visualversion.py
```

  * **Note:** The visual version runs in an infinite loop. Press **`Ctrl+C`** to exit.
  * It includes a warm-up phase (progress bar) before showing the animation.

-----

<a name="中文說明"></a>

## 🇹🇼 中文說明

### 專案簡介

本專案為 **IEEM531100 系統模擬** 課程的期末報告。我們使用 Python 實作了一個離散事件模擬 (Discrete Event Simulation, DES) 模型，旨在分析特定十字路口（光復路與建功路口）的交通流量、排隊長度與等待時間。

> **說明：** 核心模擬函式庫 (`SimClasses.py`, `SimFunctions.py`, `SimRNG.py`) 由授課教授提供。模擬邏輯 (`main.py`) 與視覺化呈現 (`visualversion.py`) 為本專案自行開發。

### 🚦 路口場景示意

模擬的十字路口結構如下：

```text
          │ 清  |
          │ 大  |
          │ (3) |
          │  ↓  |
 ─────────┘     └─────────
 交流道(1) →      ← (2) 市區 
 ─────────┐     ┌─────────
          │  ↑  |
          │ (4) |
          │ 清  |
          │ 夜  |
```

  * **道路 1**: 光復路 (往東，來自交流道)
  * **道路 2**: 光復路 (往西，來自市區)
  * **道路 3**: 建功路 (往南，來自清大)
  * **道路 4**: 建功路 (往北，來自清夜)
  * **行駛方向**: 直走 (s), 右轉 (r), 左轉 (l)

### ⚙️ 模擬機制

#### 1\. 交通號誌循環 (Traffic Cycle)

系統透過狀態機 (`traffic_state`) 控制紅綠燈循環，分為 5 個階段：

| 狀態 | 持續時間 | 描述 |
| :--- | :--- | :--- |
| **State 0** | 93秒 | 光復路（1 & 2）綠燈 |
| **State 1** | 20秒 | 光復路（1 & 2）左轉專用燈 |
| **State 2** | 12秒 | 建功路（3 & 4）紅燈，但行人綠燈（全向） |
| **State 3** | 14秒 | 建功路（3 & 4）綠燈 |
| **State 4** | 12秒 | 建功路（3 & 4）綠燈，但行人紅燈 |

#### 2\. 機率分佈 (Stochastic Distributions)

依據 `main.py` 設定：

  * **車輛到達**: 指數分佈 (Exponential)
  * **車輛通過時間**: 常態分佈 (Normal)，區分為「起步/暖身 (Warmup)」與「飽和車流 (Passthrough)」兩種速率參數。
  * **行人到達**: 指數分佈 (Exponential)
  * **行人通過時間**: 對數常態分佈 (LogNormal)

#### 3\. 實驗參數

  * **重複次數 (Replications):** 30 次
  * **單次模擬時長:** 10,800 秒 (3小時)
  * **暖身期 (Warm-up):** 3,600 秒 (1小時)
      * *暖身期間收集的統計數據會在開始計算前被清除，以確保數據穩定性。*

### 📂 檔案結構說明

| 檔案名稱 | 說明 |
| :--- | :--- |
| **`main.py`** | **主要程式。** 定義了路口邏輯、事件處理、參數設定與結果繪圖 (Matplotlib)。 |
| **`visualversion.py`** | **視覺化版本。** 在終端機中以動態文字顯示當前的紅綠燈狀態與排隊車輛數。 |
| **`SimClasses.py`** | *老師提供*。模擬核心類別 (Entity, EventCalendar, FIFOQueue 等)。 |
| **`SimFunctions.py`** | *老師提供*。模擬輔助函式 (排程 Schedule, 清除統計 ClearStats)。 |
| **`SimRNG.py`** | *老師提供*。隨機數生成器 (LCG 演算法)。 |
| **`requirements.txt`** | 專案依賴套件列表。 |

### 🥺 前提假設 (Assumptions)

1.  所有車輛與行人皆嚴格遵守交通號誌與規則。
2.  轉彎車輛會禮讓直行車輛；車輛會禮讓行人。
3.  車輛開始通過停止線後，視為離開系統，不考慮路口內的空間佔用 (Point Queue Model)。

### 🚀 安裝與執行

#### 1\. 安裝依賴環境

需使用 Python 3.10 或以上版本（因使用 `match-case` 語法）：

```bash
pip install -r requirements.txt
```

#### 2\. 執行模擬與統計

若要執行完整的統計模擬並產出圖表：

```bash
python main.py
```

  * 程式將執行 30 次重複實驗。
  * 執行完畢後，會自動在 `figure/` 資料夾內生成 **信賴區間收斂圖 (Convergence Plots)** 與 **最終結果長條圖 (CI Bar Charts)**。

#### 3\. 執行視覺化演示

若要觀察路口運作的即時狀態：

```bash
python visualversion.py
```

  * **注意：** 此模式為無窮迴圈演示，請按 **`Ctrl+C`** 結束。
  * 啟動時會有進度條顯示暖身進度。

-----


**⚠️Partial created by Gemini 3 pro**
