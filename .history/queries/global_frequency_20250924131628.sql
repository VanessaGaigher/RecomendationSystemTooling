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
    LEFT JOIN OSUSR_8DK_JOB j 
        ON j.ID = tm.DESTINATIONJOBID AND j.ISDELETED = 0 AND j.JOBSTATUSID IN (3, 4, 5)
    WHERE ti.INTERNALCOMPANYID = 1
        AND ti.ISDELETED = 0
        AND tm.TYPEID IN (3, 5) -- Exit or Transfer
        AND (tm.DESTINATIONJOBID IS NOT NULL OR tm.DESTINATIONWORKERID IS NOT NULL) -- only real use
        AND tm.STATUSID = 2
		--AND j.JOBTYPEID != 12 -- Centro de Custos
    GROUP BY ti.NAME
    ORDER BY PopularityScore DESC;