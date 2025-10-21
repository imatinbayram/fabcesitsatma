
Satishlar AS (
    SELECT
        crg_isim AS Filial,
        P.Name AS Kateqoriya,
        S.KOD,
        S.AD,
        CH.cari_Ana_cari_kodu AS ContragentCode,
        S.MEBLEG,
        Per.PeriodNote
    FROM Periods Per
    CROSS APPLY [MikroDB_V16_05].[dbo].[bazarlamaSatishCariStok_MB](Per.StartDate, Per.EndDate) S
    LEFT JOIN [MikroDB_V16_05].[dbo].[CARI_HESAPLAR] CH ON S.CARI = CH.cari_kod
    LEFT JOIN [MikroDB_V16_05].[dbo].[STOKLAR] ST ON S.KOD = ST.sto_kod
    LEFT JOIN [BazarlamaHesabatDB].[dbo].[ProductGroup] P ON P.MikroID = ST.sto_resim_url
    LEFT JOIN [MikroDB_V16_05].[dbo].[CARI_HESAP_GRUPLARI] CG ON S.GRUP = CG.crg_kod
    WHERE 
        [crg_isim] = @filial AND
        P.MikroID NOT IN (0, 999)
        AND S.KOD IN (
        '431.1000.95','431.1000.96','432.1000.95','432.1000.96',
        '601.1000.108','500.2012.96',
        'HPB.4000.016.20.200','HPBS.4000.016.20.200',
        'TM.220206070195',
        'HYST.8028.18','HYST.8028.185',
        'PST.8000.185',
        'PPRC.1000.4.025',
        'TM.200708010852','TM.200708010853',
        'TM.200708012784','TM.200708011484','TM.200708010897',
        '500.2012.96'
      )
),
MusteriKateqoriya AS (
    SELECT DISTINCT
        Filial, Kateqoriya, KOD, AD, ContragentCode, PeriodNote
    FROM Satishlar
)
SELECT
    MK.Filial,
    MK.Kateqoriya,
    MK.KOD,
    MK.AD,
    COUNT(MK.ContragentCode) AS Deyer,
    MK.PeriodNote AS Period
FROM MusteriKateqoriya MK
GROUP BY
    MK.Filial, MK.Kateqoriya, MK.KOD, MK.AD, MK.PeriodNote
ORDER BY
    MK.Filial, MK.Kateqoriya, MK.KOD, MK.AD,
    CASE MK.PeriodNote
        WHEN '7ci_ay' THEN 1
        WHEN '8ci_ay' THEN 2
        WHEN '9cu_ay' THEN 3
        WHEN '10cu_ay' THEN 4
        WHEN '7_8_9_ay' THEN 5
        WHEN '8_9_10_ay' THEN 6
        WHEN '7_8_9_10_ay' THEN 7
        ELSE 99
    END;