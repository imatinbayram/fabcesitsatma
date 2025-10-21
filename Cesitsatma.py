# streamlit_app.py
import streamlit as st
import pandas as pd
import warnings
from datetime import date
import requests
from io import BytesIO

warnings.simplefilter("ignore")

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(
    page_title='FAB HESABAT',
    page_icon='logo.png',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# FAB HESABAT \n Bu hesabat FAB şirkətlər qrupu üçün hazırlanmışdır."
    }
)

bazarlama_filial = [
'BAKI 1',
'BAKI 2',
'BAKI 3',
'BAKI 4',
'BAKI 5',
'BNAXCHIVAN',
'GENCE1',
'GENCE2',
'GOYCAY',
'QUBA',
'LENKERAN',
'SABIRABAD',
'SEKI'
]

today = date.today()
tarix_1 = today.replace(day=1)
tarix_2 = today

# Format: DD.MM.YYYY
tarix_1_str = tarix_1.strftime("%d.%m.%Y")
tarix_2_str = tarix_2.strftime("%d.%m.%Y")

st.text(f"Tarix: {tarix_2_str}")
select_filial = st.selectbox("Filial seçin:",bazarlama_filial,
                                    index=0,
                                    placeholder = 'Filial',
                                    #label_visibility='collapsed'
                                    )

musteri_qrup = pd.read_excel("Musteri.xlsx", sheet_name="Qrup")

temsilci_list = musteri_qrup[musteri_qrup["AD"] == select_filial]["Temsilci"].tolist()

row = musteri_qrup.loc[musteri_qrup["AD"] == select_filial, "Grup"]

if not row.empty:
    filial_grup_kodu = row.iloc[0]
else:
    filial_grup_kodu = None

def cesitstok():
    today = date.today()
    #tarix_1 = today.replace(day=1).isoformat()
    tarix_2 = today.isoformat()
    with open("SOK.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
    DECLARE @filial NVARCHAR(50) = N'{select_filial}';
    WITH Periods AS (
    SELECT '2025-07-01' AS StartDate, '2025-07-31' AS EndDate, '7ci_ay' AS PeriodNote
    UNION ALL SELECT '2025-08-01', '2025-08-31', '8ci_ay'
    UNION ALL SELECT '2025-09-01', '2025-09-30', '9cu_ay'
    UNION ALL SELECT '2025-10-01', '{tarix_2}', '10cu_ay'
    UNION ALL SELECT '2025-07-01', '2025-09-30', '7_8_9_ay'
    UNION ALL SELECT '2025-08-01', '{tarix_2}', '8_9_10_ay'
    UNION ALL SELECT '2025-07-01', '{tarix_2}', '7_8_9_10_ay'
    ),
    {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

def musteri_sayi():
    all_data = []  # list to store data from each seller

    for temsilci in temsilci_list:
        query = f"""
            DECLARE 
                @IL INT = 2025,
                @AY INT = 10,
                @Seller NVARCHAR(10) = N'{temsilci}';
            
            USE [BazarlamaHesabatDB];
            
            EXEC [dbo].[Report_201_PART_3]
                @IL = @IL,
                @AY = @AY,
                @Seller = @Seller;
        """

        url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {"Query": query}
        response = requests.get(url, json=payload, headers=headers, verify=False)

        if response.status_code == 200:
            api_data = response.json()
            if api_data.get("Code") == 0 and api_data.get("Data"):
                df = pd.DataFrame(api_data["Data"])
                all_data.append(df)
            else:
                print(f"API Error for {temsilci}: {api_data.get('Message')}")
        else:
            print(f"HTTP Error for {temsilci}: {response.status_code}")

    # Combine all results into one DataFrame
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    else:
        print("No data returned from API.")
        return pd.DataFrame()

def satilmayanmusteri():
    today = date.today()
    #tarix_1 = today.replace(day=1).isoformat()
    buguntarix = today.isoformat()
    with open("SatilmayanMusteri.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
    
    DECLARE @filial NVARCHAR(50) = N'{filial_grup_kodu}';
    DECLARE @BugunTarix DATE = '{buguntarix}';
    
    {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

st.markdown("""
<script>
const meta = document.createElement('meta');
meta.name = "description";
meta.content = "FAB HESABAT - Bu hesabat FAB şirkətlər qrupu üçün hazırlanmışdır.";
document.getElementsByTagName('head')[0].appendChild(meta);
</script>

<link rel="icon" href="logo.png" type="image/png">

<style>
/* Hide left index (row headers) in tables rendered by pandas Styler */
th.row_heading {display: none !important;}
th.blank {display: none !important;}      /* top-left blank corner */
tbody th {display: none !important;}      /* extra guard */
</style>

<style>
  table td {
    text-align: right;
  }
  table th {
    text-align: right; /* Optional: Align headers as well */
  }
  table p {
    text-align: right; /* Optional: Align headers as well */
  }
  
[data-testid="stMarkdownContainer"] table {
    width: 100%;
    border-collapse: collapse;
}

[data-testid="stMarkdownContainer"] th,
[data-testid="stMarkdownContainer"] td {
    text-align: right;
    border: 1px solid #ccc;
    padding: 5px;
}
</style>


<style>

    [data-testid="stHeader"] {
        display: none;
    }
    
    [data-testid="stElementToolbar"] {
        display: none;
    }
    
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />

<style>

    th {
       color: black;
       font-weight: bold;
    }
        
    

    [data-testid="stHeader"] {
        display: none;
    }
    
    [class="viewerBadge_link__qRIco"] {
        display: none;
    }
    
    [data-testid="stElementToolbar"] {
        display: none;
    }
    
    button[title="View fullscreen"] {
        visibility: hidden;
    }
    
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />

<style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 46px;
        background-color: #FF4B4B;
        color: white;
        text-align: left;
        padding: 1rem 1.25rem;
        font-size: 12px;
        z-index: 10;
    }
</style>

<div class="footer">
    FAB
</div>
""", unsafe_allow_html=True)

##################################################
#SOK KAMPANIYA SOHBETLERI
##################################################

with st.spinner("Satış məlumatları yüklənir..."):
    try:
        cesitstok_data = cesitstok()
    except Exception as e:
        st.error(f"Xəta: {e}")

if cesitstok_data is None or cesitstok_data.empty:
    st.info("Məlumat tapılmadı.")


cesitstok_data = cesitstok_data[cesitstok_data["Filial"]==select_filial]

pivot_cesitstok_data = cesitstok_data.pivot(
    index=["Filial", "Kateqoriya", "KOD", "AD"],
    columns="Period",
    values="Deyer"
).reset_index()

pivot_cesitstok_data = pivot_cesitstok_data.fillna(0)

with st.spinner("Müştəri sayları yüklənir..."):
    try:
        musteri_sayi_func = musteri_sayi()
    except Exception as e:
        st.error(f"Xəta: {e}")

if musteri_sayi_func is None or musteri_sayi_func.empty:
    st.info("Məlumat tapılmadı.")

musteri_sayi_cedvel = musteri_sayi_func[["GroupName","ProductGroup","TotalContragentCount","MinSaleContragentCount"]]
musteri_sayi_cedvel.rename(columns={
    "GroupName": "Filial",
    "ProductGroup": "Kateqoriya",
    "TotalContragentCount": "Musteri sayi",
    "MinSaleContragentCount": "Hedef"
}, inplace=True)

cesitstok_musterisay = pivot_cesitstok_data.merge(
    musteri_sayi_cedvel,
    how="left",
    on=["Filial", "Kateqoriya"]
)

period_columns = ["7ci_ay", "8ci_ay", "9cu_ay", "10cu_ay",
                  "7_8_9_ay", "8_9_10_ay", "7_8_9_10_ay"]
numeric_columns = ["Musteri sayi", "Hedef"] + period_columns

final_columns = ["Filial", "AD"] + numeric_columns
cesitstok_musterisay = cesitstok_musterisay[final_columns]

cesitstok_musterisay["Performans"] = cesitstok_musterisay.apply(
    lambda row: "Az artim var" if row["8_9_10_ay"] > row["7_8_9_ay"] else "Artim yox",
    axis=1
)

def highlight_performans(row):
    # If the 'Performans' column contains the phrase, color the whole row green
    if "Az artim var" in str(row["Performans"]):
        return ['background-color: green'] * len(row)
    else:
        return [''] * len(row)

styled_df = (
    cesitstok_musterisay.style
    .format({col: "{:.0f}" for col in numeric_columns})
    .apply(highlight_performans, axis=1)
)

st.subheader(f"{select_filial} - ŞOK Kampaniya məhsulları müştəri sayı", divider='rainbow')
st.table(styled_df)

# ---------------------------------------------
# Excel export with auto column width
# ---------------------------------------------
df_to_excel = styled_df.data if hasattr(styled_df, "data") else styled_df

output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_to_excel.to_excel(writer, index=False, sheet_name='Ümumi')
    worksheet = writer.sheets['Ümumi']

    # Set column widths based on max length of content
    for i, col in enumerate(df_to_excel.columns):
        max_len = max(
            df_to_excel[col].astype(str).map(len).max(),  # Max length of values
            len(str(col))  # Max length of column name
        )
        worksheet.set_column(i, i, max_len + 2)  # +2 for padding

excel_data = output.getvalue()

st.download_button(
    label=":green[Cədvəli Excel'ə yüklə] :floppy_disk:",
    data=excel_data,
    file_name=f"{select_filial} - SOK Kampaniya mehsullari musteri sayi.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

##################################################
#CESIT SATMA ICRA
##################################################

cesitsatma_icra = musteri_sayi_func[["GroupName","ProductGroup","TotalContragentCount","MinSaleContragentCount",
                                     "SaleContragentCount","CompletedPercentage"]]
cesitsatma_icra.rename(columns={
    "GroupName": "Filial",
    "ProductGroup": "Kateqoriya",
    "TotalContragentCount": "Musteri sayi",
    "MinSaleContragentCount": "Hedef",
    "SaleContragentCount": "Satılan",
    "CompletedPercentage": "İCRA"
}, inplace=True)

styled_cesitsatma_icra = (
    cesitsatma_icra.style
    .format(
        {col: "{:.0f}" for col in numeric_columns if col != "İCRA"} | 
        {"İCRA": lambda x: f"{x:.0f}%"}  # just add % without scaling
    )
)

st.subheader(f"{select_filial} - Çeşit satmaya görə icra", divider='rainbow')

st.table(styled_cesitsatma_icra)

##################################################
#KATEQORIYA SATMAYAN MUSTERILER
##################################################

with st.spinner("Satılmayan müştərilər yüklənir..."):
    try:
        satilmayan_musteri = satilmayanmusteri()
    except Exception as e:
        st.error(f"Xəta: {e}")

if satilmayan_musteri is None or satilmayan_musteri.empty:
    st.info("Məlumat tapılmadı.")
    
st.subheader(f"{select_filial} - Kateqoriya satılmayan müştərilər", divider='rainbow')

output2 = BytesIO()
with pd.ExcelWriter(output2, engine='xlsxwriter') as writer2:
    satilmayan_musteri.to_excel(writer2, index=False, sheet_name='Satılmayan')
    worksheet2 = writer2.sheets['Satılmayan']

    # Auto column width
    for i, col in enumerate(satilmayan_musteri.columns):
        max_len = max(
            satilmayan_musteri[col].astype(str).map(len).max(),
            len(str(col))
        )
        worksheet2.set_column(i, i, max_len + 2)

excel_data2 = output2.getvalue()

st.download_button(
    label=":red[Satılmayan müştəriləri yüklə] 📥",
    data=excel_data2,
    file_name=f"{select_filial} - Satılmayan müştərilər.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
