# General Documentation - MeivRecomendation

## Movement Types:

The main entities involved in the movement are: **Warehouse**, **Job**, **Worker**, and **Container**.

Below are the rules for tool movement, categorized by point of origin:

### **1. Movements from the WAREHOUSE**

The Warehouse functions as a central initial distribution point for tools.

  * **Origin:** Warehouse
  * **Possible Destinations:**
      * **Worker:** Tools can be allocated directly to a worker.
          * *Movement Type:* Exit (registered with code 3).
      * **Container:** Tools can be sent to a container.
          * *Movement Type:* Exit (code 3), Transfer (code 5), and Deposit (code 1).
      * **Worksite:** Tools can be sent to a worksite.
          * *Movement Type:* Exit (code 3) and Repair (Dispatch) (code 6)

### **2. Movements from the JOB**

The JOB is a place of intensive tool use, with several entry and exit movements.

  * **Origin:** JOB
  * **Possible Destinations:**
      * **Worker:** There is no movement from `job` to `worker`.

      * **Container:** Tools can be stored or moved to a container.

          * *Movement Type:* Transfer (code 5), Deposit (code 1), or Entry (code 4).

      * **Warehouse:** Return of tools to the Warehouse.

          * *Associated Movement Types:*
              * Loss (code 9)
              * Repair (code 7)
              * Entry (code 4) - [at the Warehouse]

### **3. Movements from the WORKER**

The worker is a carrier of tools, but seems to have a more restricted movement flow or one that does not generate a formal "origin" record in the system.

  * **Origin:** Worker

  * **Possible Destinations:**

      * **Worker:** There is no movement from `worker` to `worker`.
      * **warehouse:** Tools can be entry (code 4) in warehouse from `worker`.
      * **Job:** There is no movement from `worker` to `job`.
      * **Container:** Tools can be stored or moved to a container.
          * *Movement Type:* Entry (code 4).

  * **Crucial Observation:** The note "has no origin movement" indicates that, although a worker can pass a tool to another location or person, the system **does not register the worker as the official starting point** of the movement. The movement is likely registered from the worker's location (e.g., the Worksite).

### **4. Movements from the CONTAINER**

The Container acts as a mobile or localized storage unit, with outbound flows to work locations.

  * **Origin:** Container
  * **Possible Destinations:**
      * **Job:** Sending tools to the work front.
          * *Movement Type:* Exit (code 3), Transfer (code 5), Deposit (Removal) (code 2), and Loss (code 8).
      * **Worker:** Allocation of tools directly to a worker.
          * *Movement Type:* Exit (code 3).
      * **Container:** Movement between containers (transfer).
          * *Movement Type:* There is no direct movement between containers.

### **Summary of Identified Movement Codes:**

  * **1:** Deposit
  * **2:** Deposit (Removal)
  * **3:** Exit
  * **4:** Entry
  * **5:** Transfer
  * **6:** Repair (Dispatch)
  * **7:** Repair (Return)
  * **8:** Loss
  * **9:** Loss (Recovery)
  * **10:** Return

This set of rules governs the logistics and tracking of the business's tools, clearly defining the permitted flows and the types of transactions associated with each movement.

## 🎯 What does "most used globally" mean?

We want to measure **real usage**, the focus should be on movements that **put the tool in the hands of those who will work with it** (job, worker, work front via container).

📌 This is different from counting returns, losses, or repairs → these do not signify use, only an administrative cycle.

-----

## 🔑 Rules for counting usage

### Counts as **usage**:

1.  **Warehouse → Job / Container / Worker**

      * `statusid = 3 (Exit)`
      * `statusid = 5 (Transfer)` *(if it's an actual allocation, not just logistics)*

2.  **Container → Job / Worker**

      * `statusid = 3 (Exit)`
      * `statusid = 5 (Transfer)`

-----

### Do not count as usage:

  * `statusid = 1 (Deposit)` → entry into stock.
  * `statusid = 4 (Entry)` → returns/devolutions.
  * `statusid = 7 (Repair Return)`.
  * `statusid = 8/9 (Loss/Recovery)`.
  * `statusid = 10 (Return)`.

-----

# 📘 Complementary Documentation

## 🔎 Difference between the Queries

### 1\. **Query by Job/Manager/Tool Type**

👉 Objective: understand **how and where** each tool was used, providing granularity.

  * **Dimensions**: Job (`DESTINATIONJOBID`), Manager (`RESPONSIBLEID`), Tool (`ti.NAME`), Type (`Serialized` or `NonSerialized`).
  * **Metric**: `RequestedVolume = SUM(QUANTITY)` → how many units were requested at that job, by that manager.

<!-- end list -->

```sql
SELECT
    tm.DESTINATIONJOBID AS Worksite,
    j.RESPONSIBLEID AS Manager,
    ti.NAME,
    ROUND(SUM(tmi.QUANTITY), 0) AS RequestedVolume,
    CASE 
        WHEN ti.SERIALNUMBER = '' THEN 'NonSerialized'
        ELSE 'Serialized'
    END AS ToolType
FROM OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT tm
JOIN OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT_TOOLINGITEM tmi 
    ON tm.ID = tmi.MOVEMENTID
JOIN OSUSR_CEQ_TOOLINGITEM ti 
    ON ti.ID = tmi.TOOLINGITEMID
JOIN OSUSR_8DK_JOB j
    ON j.ID = tm.DESTINATIONJOBID AND j.ISDELETED = 0
WHERE ti.INTERNALCOMPANYID = 1
  AND ti.ISDELETED = 0
  AND tm.TYPEID IN (3, 5) -- 3 = Exit, 5 = Transfer
  AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL)
  AND tm.STATUSID = 2
  AND j.JOBSTATUSID IN (3, 4, 5)
GROUP BY tm.DESTINATIONJOBID, j.RESPONSIBLEID, ti.NAME, 
         CASE WHEN ti.SERIALNUMBER = '' THEN 'NonSerialized' ELSE 'Serialized' END
ORDER BY tm.DESTINATIONJOBID, j.RESPONSIBLEID, RequestedVolume DESC;
```

📌 **Typical uses**:

  * Jaccard Similarity → to build the worksite × tool matrix (binary or weighted by volume).
  * Apriori / Association Rules → to discover frequent combinations of tools.
  * Usage analyses segmented by **worksite** or **manager**.

-----

### 2\. **Global Popularity Query**

👉 Objective: measure the **aggregate popularity** of the tool across its entire history.

  * **Dimensions**: Tool (`ti.NAME`).

  * **Metrics**:

      * `DistinctWorksites` = how many different jobs used the tool.
      * `DistinctManagers` = how many managers requested the tool.
      * `TotalVolume` = sum of all quantities requested.
      * `PopularityScore` = combined metric (e.g., jobs + log(volume)).

    <!-- end list -->

    ````sql
    SELECT
      ti.NAME AS Tool,
      COUNT(DISTINCT tm.DESTINATIONJOBID) AS DistinctWorksites,
      COUNT(DISTINCT j.RESPONSIBLEID) AS DistinctManagers,
      SUM(tmi.QUANTITY) AS TotalVolume,
      -- Combined score: no. of worksites + log(total_volume + 1)
      COUNT(DISTINCT tm.DESTINATIONJOBID) 
          + 0.5 * LOG(1 + SUM(tmi.QUANTITY)) AS PopularityScore
      FROM OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT tm
      JOIN OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT_TOOLINGITEM tmi 
          ON tm.ID = tmi.MOVEMENTID
      JOIN OSUSR_CEQ_TOOLINGITEM ti 
          ON ti.ID = tmi.TOOLINGITEMID
      JOIN OSUSR_8DK_JOB j
          ON j.ID = tm.DESTINATIONJOBID AND j.ISDELETED = 0
      WHERE ti.INTERNALCOMPANYID = 1
          AND ti.ISDELETED = 0
          AND tm.TYPEID IN (3, 5) -- Exit or Transfer
          AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL) -- only real use
          AND tm.STATUSID = 2
          AND j.JOBSTATUSID IN (3, 4, 5)
      GROUP BY ti.NAME
      ORDER BY PopularityScore DESC;```


    ````

📌 **Typical uses**:

  * Global ranking of the most used tools.
  * Criterion for **popularity-based** recommendation (Top-N).
  * Trend analysis (which tools are usage "champions").

-----

## 🎯 Connection with Movement Rules

Both queries respect the same logic:

  * **Count as real use** only `Exit (3)` and `Transfer (5)` movements with a **Worksite** or **Worker** destination.
  * **Ignore** returns, repairs, losses, deposits, etc., because they do not represent effective use.

In other words: **real use = tool delivered to the work front**.

-----

## 🛠️ How to use these queries together

1.  **Global Popularity**

      * Gives the **overall Top 20** most requested tools across the entire company.
      * Useful for "standard recommendations" or as a baseline in recommendation analyses.

2.  **Popularity by Worksite/Manager**

      * Allows for the creation of a **local usage profile** (by worksite) and management profile (by responsible person).
      * Basis for **personalization**: recommending tools that similar worksites/managers usually request.

3.  **Similarity (Jaccard) + Apriori**

      * The detailed query by worksite/manager serves as a basis for generating **tool baskets** and applying association techniques.
      * Example: if 80% of the worksites that requested "Drill" also requested "12mm Drill Bit," the system automatically suggests it.

-----

# 🔄 Data Flow for Tool Recommendation

```plaintext
                   ┌─────────────────────┐
                   │     Raw Movements   │
                   │  (tables tm, tmi, ti│
                   │      and job)       │
                   └─────────┬───────────┘
                             │
             ┌───────────────┼─────────────────┐
             │                                 │
┌─────────────────────┐             ┌─────────────────────┐
│ Query 1: Detailed   │             │ Query 2: Global     │
│ by Worksite/Manager │             │ Popularity          │
│ - Worksite          │             │ - Tool              │
│ - Manager           │             │ - TotalVolume       │
│ - Tool              │             │ - DistinctWorksites │
│ - Type (Ser/NSer)   │             │ - PopScore          │
│ - RequestedVolume   │             └─────────┬───────────┘
└─────────┬───────────┘                       │
          │                                   │
          │                                   │
          ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│ Similarity (Jacc.)  │             │ Global Ranking      │
│ - worksite×tool matrix│             │ - Top N Tools       │
│ - Profile by manager│             │ - Default suggestions│
└─────────┬───────────┘             └─────────┬───────────┘
          │                                   │
          ▼                                   │
┌─────────────────────┐                       │
│ Association Rules   │                       │
│ (Apriori/FP-Growth) │                       │
│ - Tools that appear │                       │
│   together          │                       │
└─────────┬───────────┘                       │
          │                                   │
          └──────────────────┬────────────────┘
                             ▼
                   ┌─────────────────────┐
                   │  Suggestion System  │
                   │ - Popularity        │
                   │ - Similarity        │
                   │ - Associations      │
                   └─────────────────────┘
```

-----

## 📌 Flow Explanation

1.  **Raw movement data** → extracted from the tables (`tm`, `tmi`, `ti`, `job`)

      * Filtered for **real use** (`TYPEID IN (3,5)`, `STATUSID=2`, destination worksite/worker).

2.  **Query 1 (Detailed by worksite/manager)** → generates the transactional base:

      * Allows seeing which tools **were requested together** at each worksite.
      * Serves for **similarity (Jaccard)** and **association rules (Apriori)**.

3.  **Query 2 (Global Popularity)** → generates the aggregate rankings:

      * Identifies the **most requested tools overall**.
      * Useful for a **Top N** ranking and as a fallback (when there is no history for the worksite).

4.  **Recommendation Modules**:

      * **Popularity** = baseline (always recommends the most requested).
      * **Similarity (Jaccard)** = recommends tools with a similar history on other worksites.
      * **Associations (Apriori)** = recommends frequent combinations of tools.

5.  **Final system** can merge the approaches:

      * **If there is no worksite history** → uses Global Popularity.
      * **If there is little history** → mixes Popularity + Similarity.
      * **If there is a lot of history** → applies Associations for more refined recommendations.

-----