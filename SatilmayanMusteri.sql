IF OBJECT_ID('tempdb..##TmpResult') IS NOT NULL
    DROP TABLE ##TmpResult;

DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql +
    CASE WHEN @sql = N'' THEN N'' ELSE N' UNION ALL ' END +
    N'SELECT N''' + Name + ''' AS ProductName, ContragentCode 
      FROM BazarlamaHesabatDB.dbo.ContragentInfo 
      WHERE [' + SqlName + ']=1'
FROM BazarlamaHesabatDB.dbo.ProductGroup
WHERE MikroID NOT IN (0,999) AND SqlName <> '';

SET @sql = N'SELECT * INTO ##TmpResult FROM (' + @sql + N') AS T;';

EXEC sp_executesql @sql;

WITH SATIS_TABLE AS (
    SELECT * 
    FROM [MikroDB_V16_05].[dbo].[bazarlamaSatishCariStok_MB]('2025-07-01',@BugunTarix)
    WHERE [GRUP] = @filial
),
CEDVEL AS (
    SELECT
        [GRUP],
        [CARI AD],
        [KOD],
        [AD],
        sto_resim_url,
        CRG.crg_isim AS BOLGE
    FROM
        SATIS_TABLE
    LEFT JOIN [MikroDB_V16_05].[dbo].CARI_HESAP_GRUPLARI CRG
        ON [GRUP] = CRG.crg_kod
    LEFT JOIN [MikroDB_V16_05].[dbo].STOKLAR
        ON [KOD] = sto_kod
),
-- All product groups (including those with no sales)
PRODUCT_GROUPS AS (
    SELECT MikroID, Name AS QG_NAME
    FROM [BazarlamaHesabatDB].dbo.[ProductGroup]
    WHERE MikroID NOT IN ('0', '999')
),
-- Match sales to product groups (left join to include all product groups)
MATCHED_SALES AS (
    SELECT 
        PG.MikroID,
        PG.QG_NAME,
        CEDVEL.[KOD],
        CEDVEL.[AD],
        CEDVEL.BOLGE,
        CEDVEL.[CARI AD],
        CARI.cari_Ana_cari_kodu [ANA]
    FROM CEDVEL
    LEFT JOIN PRODUCT_GROUPS PG
        ON PG.MikroID = CEDVEL.sto_resim_url
    LEFT JOIN [MikroDB_V16_05].[dbo].CARI_HESAPLAR CARI
        ON CARI.cari_unvan1 = CEDVEL.[CARI AD]
),

SATILAN AS (
SELECT DISTINCT QG_NAME ProductName, [ANA] ContragentCode from MATCHED_SALES
)


SELECT 
    T.ProductName AS Kateqoriya,
    T.ContragentCode AS Musteri_kodu,
    CARI.cari_unvan1 AS Musteri_adi,
    CRG.crg_isim AS Bolge
FROM ##TmpResult T
LEFT JOIN SATILAN S 
    ON T.ContragentCode COLLATE SQL_Latin1_General_CP1_CI_AS = S.ContragentCode COLLATE SQL_Latin1_General_CP1_CI_AS
   AND T.ProductName    COLLATE SQL_Latin1_General_CP1_CI_AS = S.ProductName    COLLATE SQL_Latin1_General_CP1_CI_AS
LEFT JOIN [MikroDB_V16_05].[dbo].CARI_HESAPLAR CARI
    ON CARI.cari_kod COLLATE SQL_Latin1_General_CP1_CI_AS = T.ContragentCode COLLATE SQL_Latin1_General_CP1_CI_AS
LEFT JOIN [MikroDB_V16_05].[dbo].CARI_HESAP_GRUPLARI CRG
    ON CRG.crg_kod COLLATE SQL_Latin1_General_CP1_CI_AS = CARI.cari_grup_kodu COLLATE SQL_Latin1_General_CP1_CI_AS
WHERE
    S.ProductName is null
ORDER BY
    T.ProductName,CARI.cari_unvan1