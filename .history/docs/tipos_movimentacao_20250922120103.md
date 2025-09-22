# Tipos de Movimentação:

As entidades principais envolvidas na movimentação são: **Estaleiro**, **Obra**, **Trabalhador** (Trabalhador) e **Container**.

A seguir, apresento as regras de movimentação de ferramentas, categorizadas por ponto de origem:

### **1. Movimentações a partir do ESTALEIRO**

O Estaleiro funciona como um ponto central de distribuição inicial de ferramentas.

* **Origem:** Estaleiro
* **Destinos Possíveis:**
    * **Worker:** Ferramentas podem ser alocadas diretamente a um trabalhador.
        * *Tipo de Movimentação:* Saída (registrada com o código 3).
    * **Container:** Ferramentas podem ser enviadas para um container.
        * *Tipo de Movimentação:* Saída (código 3), Transferência (código 5) e Depósito (código 1).
    * **Obra:** Ferramentas podem ser enviadas para uma obra.
        * *Tipo de Movimentação:* Saída (código 3) e Reparação (Envio) (código 6)

### **2. Movimentações a partir da OBRA**

A Obra é um local de uso intenso de ferramentas, com diversas movimentações de entrada e saída.

* **Origem:** Obra
* **Destinos Possíveis:**
    * **Worker:** Não há movimentação de `obra` para `worker`.

    * **Container:** As ferramentas podem ser guardadas ou movidas para um container.
        * *Tipo de Movimentação:* Transferência (código 5), Depósito (código 1) ou Entrada (código 4).
    
    * **Estaleiro:** Retorno de ferramentas para o Estaleiro.
        * *Tipos de Movimentação Associados:*
            * Perda (código 9)
            * Reparação (código 7)
            * Entrada (código 4) - [no estaleiro]

### **3. Movimentações a partir do WORKER (Trabalhador)**

O trabalhador é um portador de ferramentas, mas parece ter um fluxo de movimentação mais restrito ou que não gera um registro de "origem" formal no sistema.

* **Origem:** Worker
* **Destinos Possíveis:**
    * **Worker:** Não há movimentação de `worker` para `worker`.
    * **Obra:** Não há movimentação de `worker` para `obra`.
    * **Container:** As ferramentas podem ser guardadas ou movidas para um container.
        * *Tipo de Movimentação:* Entrada (código 4).

* **Observação Crucial:** A anotação "não tem movim de origem" indica que, embora um trabalhador possa passar uma ferramenta para outro local ou pessoa, o sistema **não registra o trabalhador como o ponto de partida oficial** da movimentação. A movimentação é provavelmente registrada a partir da localização do trabalhador (ex: a Obra).

### **4. Movimentações a partir do CONTAINER**

O Container atua como uma unidade de armazenamento móvel ou localizada, com fluxos de saída para locais de trabalho.

* **Origem:** Container
* **Destinos Possíveis:**
    * **Obra:** Envio de ferramentas para a frente de trabalho.
        * *Tipo de Movimentação:* Saída (código 3), Transferência (código 5), Depósito (Remoção) (código 2) e Perda (código 8).
    * **Worker:** Alocação de ferramentas diretamente para um trabalhador.
        * *Tipo de Movimentação:* Saída (código 3).
    * **Container:** Movimentação entre containers (transferência).
        * *Tipo de Movimentação:* Não há movimentação direta entre containers.

### **Resumo dos Códigos de Movimentação Identificados:**

* **1:** Depósito
* **2:** Depósito (Remoção)
* **3:** Saída
* **4:** Entrada
* **5:** Transferência
* **6:** REparação (Envio)
* **7:** Reparação (Retorno)
* **8:** Perda
* **9:** Perda (Recuperação)
* **10:** Devolução

Este conjunto de regras governar a logística e o rastreamento das ferramentas do negócio, definindo claramente os fluxos permitidos e os tipos de transação associados a cada movimentação.

## 🎯 O que significa “mais utilizada globalmente”?

Queremos medir **uso real**, o foco deve ser nas movimentações que **colocam a ferramenta em mãos de quem vai trabalhar com ela** (obra, trabalhador, frente de trabalho via container).

📌 Isso é diferente de contabilizar devoluções, perdas ou reparações → esses não significam uso, apenas ciclo administrativo.

---

## 🔑 Regras para contar utilização

### Conta como **utilização**:

1. **Estaleiro → Obra / Container / Worker**

   * `statusid = 3 (Saída)`
   * `statusid = 5 (Transferência)` *(se for alocação real, não só logística)*

2. **Container → Obra / Worker**

   * `statusid = 3 (Saída)`
   * `statusid = 5 (Transferência)`

---

### Não contam como utilização:

* `statusid = 1 (Depósito)` → entrada em estoque.
* `statusid = 4 (Entrada)` → retornos/devoluções.
* `statusid = 7 (Reparação Retorno)`.
* `statusid = 8/9 (Perda/Recuperação)`.
* `statusid = 10 (Devolução)`.

---

## 📊 Query base para ranking global


```sql
SELECT
    ti.NAME,
    tmi.TOOLINGITEMID,
    ROUND(SUM(tmi.QUANTITY), 0) AS VolumeSolicitado
FROM OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT tm
JOIN OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT_TOOLINGITEM tmi 
    ON tm.ID = tmi.MOVEMENTID
JOIN OSUSR_CEQ_TOOLINGITEM ti 
    ON ti.ID = tmi.TOOLINGITEMID
WHERE ti.INTERNALCOMPANYID = 1
  AND ti.ISDELETED = 0
  AND tm.TYPEID IN (3, 5) -- 3 = Saída, 5 = Transferência
  AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL) -- só conta uso real
  AND tm.STATUSID = 2
GROUP BY tmi.TOOLINGITEMID, ti.NAME
ORDER BY VolumeSolicitado DESC;
```

---

