# Documentação Geral- MeivRecomendation
## Tipos de Movimentação:

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

# 📘 Documentação Complementar

## 🔎 Diferença entre as Queries

### 1. **Query por Obra/Gestor/Tipo de Ferramenta**

👉 Objetivo: entender **como e onde** cada ferramenta foi usada, trazendo granularidade.

* **Dimensões**: Obra (`DESTINATIONJOBID`), Gestor (`RESPONSIBLEID`), Ferramenta (`ti.NAME`), Tipo (`Seriada` ou `NaoSeriada`).
* **Métrica**: `VolumeSolicitado = SUM(QUANTITY)` → quantas unidades foram pedidas naquela obra, por aquele gestor.

```sql
SELECT
    tm.DESTINATIONJOBID AS Obra,
    j.RESPONSIBLEID AS Gestor,
    ti.NAME,
    ROUND(SUM(tmi.QUANTITY), 0) AS VolumeSolicitado,
    CASE 
        WHEN ti.SERIALNUMBER = '' THEN 'NaoSeriada'
        ELSE 'Seriada'
    END AS TipoFerramenta
FROM OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT tm
JOIN OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT_TOOLINGITEM tmi 
    ON tm.ID = tmi.MOVEMENTID
JOIN OSUSR_CEQ_TOOLINGITEM ti 
    ON ti.ID = tmi.TOOLINGITEMID
JOIN OSUSR_8DK_JOB j
    ON j.ID = tm.DESTINATIONJOBID AND j.ISDELETED = 0
WHERE ti.INTERNALCOMPANYID = 1
  AND ti.ISDELETED = 0
  AND tm.TYPEID IN (3, 5) -- 3 = Saída, 5 = Transferência
  AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL)
  AND tm.STATUSID = 2
  AND j.JOBSTATUSID IN (3, 4, 5)
GROUP BY tm.DESTINATIONJOBID, j.RESPONSIBLEID, ti.NAME, 
         CASE WHEN ti.SERIALNUMBER = '' THEN 'NaoSeriada' ELSE 'Seriada' END
ORDER BY tm.DESTINATIONJOBID, j.RESPONSIBLEID, VolumeSolicitado DESC;
```


📌 **Usos típicos**:

* Similaridade de Jaccard → montar a matriz obra × ferramenta (binária ou ponderada por volume).
* Apriori / Regras de Associação → descobrir combinações frequentes de ferramentas.
* Análises de uso segmentadas por **obra** ou **gestor**.

---

### 2. **Query de Popularidade Global**

👉 Objetivo: medir a **popularidade agregada** da ferramenta em todo o histórico.

* **Dimensões**: Ferramenta (`ti.NAME`).
* **Métricas**:

  * `ObrasDistintas` = quantas obras diferentes usaram a ferramenta.
  * `GestoresDistintos` = quantos gestores pediram a ferramenta.
  * `VolumeTotal` = soma de todas as quantidades pedidas.
  * `ScorePopularidade` = métrica combinada (ex: obras + log(volume)).

  ```sql
  SELECT
    ti.NAME AS Ferramenta,
    COUNT(DISTINCT tm.DESTINATIONJOBID) AS ObrasDistintas,
    COUNT(DISTINCT j.RESPONSIBLEID) AS GestoresDistintos,
    SUM(tmi.QUANTITY) AS VolumeTotal,
    -- Score combinado: nº de obras + log(volume_total + 1)
    COUNT(DISTINCT tm.DESTINATIONJOBID) 
        + 0.5 * LOG(1 + SUM(tmi.QUANTITY)) AS ScorePopularidade
    FROM OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT tm
    JOIN OSUSR_BBQ_TOOLINGLOGISTICSMOVEMENT_TOOLINGITEM tmi 
        ON tm.ID = tmi.MOVEMENTID
    JOIN OSUSR_CEQ_TOOLINGITEM ti 
        ON ti.ID = tmi.TOOLINGITEMID
    JOIN OSUSR_8DK_JOB j
        ON j.ID = tm.DESTINATIONJOBID AND j.ISDELETED = 0
    WHERE ti.INTERNALCOMPANYID = 1
        AND ti.ISDELETED = 0
        AND tm.TYPEID IN (3, 5) -- Saída ou Transferência
        AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL) -- só uso real
        AND tm.STATUSID = 2
        AND j.JOBSTATUSID IN (3, 4, 5)
    GROUP BY ti.NAME
    ORDER BY ScorePopularidade DESC;```


📌 **Usos típicos**:

* Ranking global das ferramentas mais utilizadas.
* Critério para recomendação baseada em **popularidade** (Top-N).
* Análises de tendência (quais ferramentas são “campeãs” de uso).

---

## 🎯 Conexão com as Regras de Movimentação

Ambas as queries respeitam a mesma lógica:

* **Contam como uso real** apenas os movimentos `Saída (3)` e `Transferência (5)` com destino **Obra** ou **Worker**.
* **Ignoram** devoluções, reparações, perdas, depósitos etc., porque não representam uso efetivo.

Ou seja: **uso real = ferramenta entregue para frente de trabalho**.

---

## 🛠️ Como usar essas queries juntas

1. **Popularidade Global**

   * Dá o **Top 20 geral** das ferramentas mais requisitadas em toda a empresa.
   * Útil para “recomendações padrão” ou como baseline em análises de recomendação.

2. **Popularidade por Obra/Gestor**

   * Permite criar um **perfil de uso local** (por obra) e de gestão (por responsável).
   * Base para **personalização**: recomendar ferramentas que obras/gestores similares costumam pedir.

3. **Similaridade (Jaccard) + Apriori**

   * A query detalhada por obra/gestor serve como base para gerar **cestas de ferramentas** e aplicar técnicas de associação.
   * Exemplo: se em 80% das obras que pediram “Furadeira” também pediram “Broca 12mm”, o sistema sugere automaticamente.

---

Perfeito 🚀 Então vou te estruturar um **fluxo visual e descritivo** mostrando como as duas queries que você já tem se encaixam no pipeline de recomendação.

---

# 🔄 Fluxo de Dados para Recomendação de Ferramentas

```plaintext
                ┌─────────────────────┐
                │ Movimentações Brutas │
                │ (tabelas tm, tmi, ti │
                │ e job)               │
                └─────────┬───────────┘
                          │
          ┌───────────────┼─────────────────┐
          │                                   │
┌─────────────────────┐             ┌─────────────────────┐
│ Query 1: Detalhada  │             │ Query 2: Global     │
│ por Obra/Gestor     │             │ Popularidade        │
│ - Obra              │             │ - Ferramenta        │
│ - Gestor            │             │ - VolumeTotal       │
│ - Ferramenta        │             │ - ObrasDistintas    │
│ - Tipo (Ser/NSer)   │             │ - ScorePop          │
│ - VolumeSolicitado  │             └─────────┬───────────┘
└─────────┬───────────┘                       │
          │                                   │
          │                                   │
          ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│ Similaridade (Jacc.)│             │ Ranking Global       │
│ - Matriz obra×tool  │             │ - Top N Ferramentas │
│ - Perfil por gestor │             │ - Sugestões default │
└─────────┬───────────┘             └─────────┬───────────┘
          │                                   │
          ▼                                   │
┌─────────────────────┐                       │
│ Regras de Associação│                       │
│ (Apriori/FP-Growth) │                       │
│ - Ferramentas que   │                       │
│   aparecem juntas   │                       │
└─────────┬───────────┘                       │
          │                                   │
          └──────────────────┬────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Sistema de Sugestão │
                  │ - Popularidade      │
                  │ - Similaridade      │
                  │ - Associações       │
                  └─────────────────────┘
```

---

## 📌 Explicação do Fluxo

1. **Dados brutos de movimentação** → extraídos das tabelas (`tm`, `tmi`, `ti`, `job`)

   * Filtrados para **uso real** (`TYPEID IN (3,5)`, `STATUSID=2`, destino obra/worker).

2. **Query 1 (Detalhada por obra/gestor)** → gera a base transacional:

   * Permite ver quais ferramentas **foram pedidas juntas** em cada obra.
   * Serve para **similaridade (Jaccard)** e **regras de associação (Apriori)**.

3. **Query 2 (Popularidade Global)** → gera os rankings agregados:

   * Identifica as ferramentas **mais pedidas de forma geral**.
   * Útil para ranking **Top N** e como fallback (quando não há histórico da obra).

4. **Módulos de Recomendação**:

   * **Popularidade** = baseline (recomenda sempre os mais pedidos).
   * **Similaridade (Jaccard)** = recomenda ferramentas com histórico semelhante em outras obras.
   * **Associações (Apriori)** = recomenda combinações frequentes de ferramentas.

5. **Sistema final** pode mesclar as abordagens:

   * **Se não há histórico da obra** → usa Popularidade Global.
   * **Se há pouco histórico** → mistura Popularidade + Similaridade.
   * **Se há bastante histórico** → aplica Associações para recomendações mais finas.

---

