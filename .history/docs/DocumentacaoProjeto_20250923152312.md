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
