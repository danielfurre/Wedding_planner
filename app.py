import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import base64
from io import BytesIO

# Sett sidekonfigurasjon
st.set_page_config(
    page_title="Bryllupsplanlegger",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funksjon for å eksportere én DataFrame til Excel (brukes i andre funksjoner om ønskelig)
def download_excel(df, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    return f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'

# Funksjon for å eksportere alle dataene til én Excel-fil med flere ark
def save_all_to_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.gjester.to_excel(writer, sheet_name="Gjester", index=False)
        st.session_state.budsjett.to_excel(writer, sheet_name="Budsjett", index=False)
        st.session_state.oppgaver.to_excel(writer, sheet_name="Oppgaver", index=False)
        st.session_state.tidsplan.to_excel(writer, sheet_name="Tidsplan", index=False)
    return output.getvalue()

# Funksjon for å initiere session_state hvis de ikke eksisterer
def init_session_state():
    if 'gjester' not in st.session_state:
        st.session_state.gjester = pd.DataFrame({
            'Navn': [],
            'Relasjon': [],
            'Invitert': [],
            'RSVP Status': [],
            'Antall gjester': [],
            'Spesielle behov': []
        })
    
    if 'budsjett' not in st.session_state:
        st.session_state.budsjett = pd.DataFrame({
            'Kategori': ['Lokale', 'Catering', 'Fotograf', 'Blomster', 'Kake', 'Klær', 'Ringer', 'Dekorasjoner', 'Transport', 'Musikk', 'Invitasjoner', 'Annet'],
            'Budsjettert': [0] * 12,
            'Faktisk': [0] * 12,
            'Betalt': [0] * 12,
            'Beskrivelse': [''] * 12
        })
    
    if 'oppgaver' not in st.session_state:
        st.session_state.oppgaver = pd.DataFrame({
            'Oppgave': [],
            'Beskrivelse': [],
            'Frist': [],
            'Ansvarlig': [],
            'Status': [],
            'Prioritet': [],
            'Notater': []
        })
    
    if 'tidsplan' not in st.session_state:
        st.session_state.tidsplan = pd.DataFrame({
            'Tid': [],
            'Aktivitet': [],
            'Sted': [],
            'Ansvarlig': [],
            'Notater': []
        })

# Initier session_state
init_session_state()

# Sidebar for navigasjon
st.sidebar.title("Bryllupsplanlegger 💍")
side = st.sidebar.radio(
    "Naviger til:",
    ["Oversikt", "Gjestehåndtering", "Budsjett"]
)

# Fargeskjema
primary_color = "#FF4B4B"
secondary_color = "#0068C9"
neutral_color = "#F0F2F6"

# Sett tema med CSS
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# SIDER
# ==============================

# Oversikt side (forsiden)
if side == "Oversikt":
    st.title("Furres Bryllupsplanlegger")
    
    # --------------------------------------
    # Excel-import: Ekspanderbar seksjon
    with st.expander("Last opp Excel-fil for å fortsette der du var", expanded=False):
        uploaded_excel = st.file_uploader("Velg Excel-fil", type=["xlsx"], key="excel_uploader_dashboard")
        if uploaded_excel is not None:
            try:
                xls = pd.ExcelFile(uploaded_excel)
                st.session_state.gjester = pd.read_excel(xls, sheet_name="Gjester")
                st.session_state.budsjett = pd.read_excel(xls, sheet_name="Budsjett")
                st.session_state.oppgaver = pd.read_excel(xls, sheet_name="Oppgaver")
                st.session_state.tidsplan = pd.read_excel(xls, sheet_name="Tidsplan")
                st.success("Data lastet fra Excel!")
            except Exception as e:
                st.error(f"Kunne ikke laste Excel-fil: {e}")
    # --------------------------------------
    
    # Øvre rad: Bryllupsdato og budsjettoversikt
    col_date, col_budget = st.columns(2)
    
    with col_date:
        st.subheader("Nedtelling")
        # Hardkodet bryllupsdato: 31. mai
        today = datetime.date.today()
        current_year = today.year
        bryllupsdato = datetime.date(current_year, 5, 31)
        # Dersom dagens dato er etter 31. mai, bruk 31. mai neste år
        if today > bryllupsdato:
            bryllupsdato = datetime.date(current_year + 1, 5, 31)
        st.markdown("**Bryllupsdato: 31. mai**")
        dager_igjen = (bryllupsdato - today).days
        st.markdown(f"### 🗓️ {dager_igjen} dager igjen!")
    
    with col_budget:
        st.subheader("Budsjettoversikt")
        if 'budsjett_total' not in st.session_state:
            st.session_state.budsjett_total = 160000
        budsjett_total = st.number_input("Totalt budsjett", min_value=0, value=st.session_state.budsjett_total, key="dashboard_budsjett_total")
        st.session_state.budsjett_total = budsjett_total
        brukt = st.session_state.budsjett['Faktisk'].sum()
        prosent = int(brukt / budsjett_total * 100) if budsjett_total else 0
        st.markdown(f"### 💰 {brukt:,.0f} kr brukt av {budsjett_total:,.0f} kr ({prosent}%)")
    
    st.markdown("---")
    
    # Nøkkeltall
    st.markdown("## Nøkkeltall")
    col1, col2, col3, col4 = st.columns(4)

    # Håndter tomme dataframes ved å sjekke om den er tom
    inviterte = st.session_state.gjester['Antall gjester'].sum() if not st.session_state.gjester.empty else 0

    rsvp_ja = st.session_state.gjester.loc[
        st.session_state.gjester['RSVP Status'] == 'Kommer', 'Antall gjester'
    ].sum() if not st.session_state.gjester.empty else 0

    rsvp_nei = st.session_state.gjester.loc[
        st.session_state.gjester['RSVP Status'] == 'Kommer ikke', 'Antall gjester'
    ].sum() if not st.session_state.gjester.empty else 0

    rsvp_venter = st.session_state.gjester.loc[
        st.session_state.gjester['RSVP Status'] == 'Venter på svar', 'Antall gjester'
    ].sum() if not st.session_state.gjester.empty else 0

    with col1:
        st.metric(label="Inviterte gjester", value=inviterte)
    with col2:
        st.metric(label="Bekreftet kommer", value=rsvp_ja)
    with col3:
        st.metric(label="Bekreftet kommer ikke", value=rsvp_nei)
    with col4:
        st.metric(label="Venter på svar", value=rsvp_venter)


    
    st.markdown("---")
    
    # Grafisk oversikt
    st.markdown("## Statistikk")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### RSVP-status")
        if inviterte > 0:
            rsvp_data = pd.DataFrame({
                'Status': ['Kommer', 'Kommer ikke', 'Venter på svar'],
                'Antall': [rsvp_ja, rsvp_nei, rsvp_venter]
            })
            fig = px.pie(rsvp_data, names='Status', values='Antall', 
                         title='RSVP-status',
                         color_discrete_sequence=['#ffc107', '#28a745', '#dc3545'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ingen RSVP-data tilgjengelig.")
    
    with col_chart2:
        st.markdown("### Budsjettfordeling")
        budget_data = st.session_state.budsjett.copy()
        budget_data = budget_data[budget_data['Budsjettert'] > 0]
        if not budget_data.empty:
            fig = px.bar(budget_data, x='Kategori', y=['Budsjettert', 'Faktisk'], 
                         title='Budsjett vs. Faktiske utgifter',
                         barmode='group',
                         color_discrete_sequence=[primary_color, secondary_color])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Fyll inn budsjettet for å se fordelingen.")
    
    st.markdown("---")
    
    # Eksportering av data
    st.markdown("## Eksporter Data")
    if st.download_button("Lagre data til Excel", data=save_all_to_excel(), file_name="bryllupsdata.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
        st.success("Data eksportert!")


# Gjestehåndtering side
elif side == "Gjestehåndtering":
    st.title("Gjestehåndtering")
    
    tab1, tab2, tab3 = st.tabs(["Oversikt", "Legg til gjester", "Rediger gjester"])
    
    with tab1:
        # Filtrering og visning
        st.subheader("Gjesteoversikt")
        
        # Filtreringsalternativer
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.selectbox("Filtrer etter RSVP status", 
                                        ["Alle", "Kommer", "Kommer ikke", "Venter på svar"])
        with col2:
            filter_relasjon = st.selectbox("Filtrer etter relasjon", 
                                          ["Alle", "Familie brud", "Familie brudgom", "Venn brud", "Venn brudgom", "Kollega", "Annet"])
        with col3:
            filter_text = st.text_input("Søk etter navn")
        
        # Filtrer dataframe
        filtered_df = st.session_state.gjester.copy()
        
        if filter_status != "Alle":
            filtered_df = filtered_df[filtered_df['RSVP Status'] == filter_status]
        
        if filter_relasjon != "Alle":
            filtered_df = filtered_df[filtered_df['Relasjon'] == filter_relasjon]
        
        if filter_text:
            filtered_df = filtered_df[filtered_df['Navn'].str.contains(filter_text, case=False, na=False)]
        
        # Vis filtrert dataframe
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
            
            # Statistikk
            st.subheader("Statistikk")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Antall i utvalget", len(filtered_df))
                st.metric("Antall personer totalt", 
                         filtered_df['Antall gjester'].sum() if 'Antall gjester' in filtered_df.columns else 0)
            
            with col2:
                # Spesielle behov
                special_needs = filtered_df[filtered_df['Spesielle behov'].notna() & 
                                         (filtered_df['Spesielle behov'] != "")]
                st.metric("Spesielle behov", len(special_needs))
                
        else:
            st.info("Ingen gjester funnet som matcher kriteriene.")
    
    with tab2:
        st.subheader("Legg til gjester")
        
        # Enkeltgjest
        with st.expander("Legg til enkeltgjest", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                ny_navn = st.text_input("Navn")
                ny_relasjon = st.selectbox("Relasjon", 
                                         ["Familie brud", "Familie brudgom", "Venn brud", "Venn brudgom", "Kollega", "Annet"])
                ny_invitert = st.checkbox("Invitert", value=True)
            
            with col2:
                ny_rsvp = st.selectbox("RSVP Status", ["Venter på svar", "Kommer", "Kommer ikke"])
                ny_antall = st.number_input("Antall gjester (inkl. følge)", min_value=1, value=1, key="legg_til_antall_gjester")
                ny_behov = st.text_area("Spesielle behov", key="legg_til_spesielle_behov")
            
            if st.button("Legg til gjest"):
                if ny_navn:
                    ny_gjest = pd.DataFrame({
                        'Navn': [ny_navn],
                        'Relasjon': [ny_relasjon],
                        'Invitert': [ny_invitert],
                        'RSVP Status': [ny_rsvp],
                        'Antall gjester': [ny_antall],
                        'Spesielle behov': [ny_behov]
                    })
                    
                    st.session_state.gjester = pd.concat([st.session_state.gjester, ny_gjest], ignore_index=True)
                    st.success(f"Gjest {ny_navn} lagt til!")
                else:
                    st.error("Du må fylle inn navn.")
        
        # Bulk import
        with st.expander("Importer gjester fra CSV"):
            st.markdown("""
            Last opp CSV-fil med gjester. Filen bør ha følgende kolonner:
            - Navn (påkrevd)
            - Relasjon
            - Invitert
            - RSVP Status
            - Antall gjester
            - Spesielle behov
            """)
            
            uploaded_file = st.file_uploader("Velg CSV-fil", type="csv")
            
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    if 'Navn' in df_upload.columns:
                        st.dataframe(df_upload.head())
                        
                        if st.button("Importer gjester"):
                            required_columns = ['Navn']
                            for col in required_columns:
                                if col not in df_upload.columns:
                                    st.error(f"Kolonnen '{col}' mangler i CSV-filen!")
                                    break
                            else:
                                # Legg til manglende kolonner
                                all_columns = st.session_state.gjester.columns
                                for col in all_columns:
                                    if col not in df_upload.columns:
                                        df_upload[col] = ""
                                
                                # Importer bare kolonnene som finnes i gjester-dataframen
                                df_upload = df_upload[all_columns]
                                
                                st.session_state.gjester = pd.concat([st.session_state.gjester, df_upload], ignore_index=True)
                                st.success(f"{len(df_upload)} gjester importert!")
                    else:
                        st.error("CSV-filen mangler kolonnen 'Navn'.")
                except Exception as e:
                    st.error(f"Feil ved import: {e}")
    
    with tab3:
        st.subheader("Oppdater RSVP status")
        
        if not st.session_state.gjester.empty:
            gjest_å_oppdatere = st.selectbox("Velg gjest", st.session_state.gjester['Navn'].tolist())
            
            gjest_idx = st.session_state.gjester[st.session_state.gjester['Navn'] == gjest_å_oppdatere].index[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                ny_rsvp_status = st.selectbox(
                    "RSVP Status", 
                    ["Venter på svar", "Kommer", "Kommer ikke"],
                    index=["Venter på svar", "Kommer", "Kommer ikke"].index(
                        st.session_state.gjester.at[gjest_idx, 'RSVP Status']
                    ),
                    key=f"oppdater_rsvp_status_{gjest_idx}"  # Unik nøkkel for hver gjest
                )
    
                ny_antall_gjester = st.number_input(
                    "Antall gjester (inkl. følge)", 
                    min_value=1, 
                    value=int(st.session_state.gjester.at[gjest_idx, 'Antall gjester']),
                    key=f"oppdater_antall_gjester_{gjest_idx}"
                )
            
            with col2:
                ny_spesielle_behov = st.text_area("Spesielle behov", value=st.session_state.gjester.at[gjest_idx, 'Spesielle behov'], key=f"oppdater_spesielle_behov_{gjest_idx}")

        
            if st.button("Oppdater gjest"):
                st.session_state.gjester.at[gjest_idx, 'RSVP Status'] = ny_rsvp_status
                st.session_state.gjester.at[gjest_idx, 'Antall gjester'] = ny_antall_gjester
                st.session_state.gjester.at[gjest_idx, 'Spesielle behov'] = ny_spesielle_behov
                
                st.success(f"Gjest {gjest_å_oppdatere} oppdatert!")
            
            if st.button("Slett gjest"):
                st.session_state.gjester = st.session_state.gjester.drop(gjest_idx).reset_index(drop=True)
                st.success(f"Gjest {gjest_å_oppdatere} slettet!")
        else:
            st.info("Ingen gjester lagt til ennå.")

# Budsjett side
elif side == "Budsjett":
    st.title("Budsjett")
    
    tab1, tab2 = st.tabs(["Budsjett oversikt", "Rediger budsjett"])
    
    with tab1:
        # Total budsjett
        if 'budsjett_total' not in st.session_state:
            st.session_state.budsjett_total = 160000
        
        budsjett_total = st.number_input("Totalt budsjett", min_value=0, value=st.session_state.budsjett_total)
        st.session_state.budsjett_total = budsjett_total
        
        # Viser budsjett
        if not st.session_state.budsjett.empty:
            # Legg til summering
            sum_row = pd.DataFrame({
                'Kategori': ['Sum'],
                'Budsjettert': [st.session_state.budsjett['Budsjettert'].sum()],
                'Faktisk': [st.session_state.budsjett['Faktisk'].sum()],
                'Betalt': [st.session_state.budsjett['Betalt'].sum()],
                'Beskrivelse': ['']
            })
            
            display_df = pd.concat([st.session_state.budsjett, sum_row], ignore_index=True)
            
            # Formater tall
            display_df['Budsjettert'] = display_df['Budsjettert'].apply(lambda x: f"{x:,.0f} kr")
            display_df['Faktisk'] = display_df['Faktisk'].apply(lambda x: f"{x:,.0f} kr")
            display_df['Betalt'] = display_df['Betalt'].apply(lambda x: f"{x:,.0f} kr")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Budsjett statistikk
            st.subheader("Budsjett statistikk")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sum_budsjettert = st.session_state.budsjett['Budsjettert'].sum()
                st.metric("Totalt budsjettert", f"{sum_budsjettert:,.0f} kr")
                st.metric("Prosent av totalbudsjett", f"{sum_budsjettert/budsjett_total*100:.1f}%" if budsjett_total else "0%")
            
            with col2:
                sum_faktisk = st.session_state.budsjett['Faktisk'].sum()
                st.metric("Totalt faktisk", f"{sum_faktisk:,.0f} kr")
                st.metric("Differanse", f"{(sum_budsjettert-sum_faktisk):,.0f} kr")
            
            with col3:
                sum_betalt = st.session_state.budsjett['Betalt'].sum()
                st.metric("Totalt betalt", f"{sum_betalt:,.0f} kr")
                st.metric("Gjenstående å betale", f"{(sum_faktisk-sum_betalt):,.0f} kr")
            
            # Visuelle oversikter
            st.subheader("Grafisk oversikt")
            
            col1, col2 = st.columns(2)
            
            with col1:
                kategori_df = st.session_state.budsjett[st.session_state.budsjett['Budsjettert'] > 0].copy()
                
                if not kategori_df.empty:
                    fig = px.pie(
                        kategori_df, 
                        values='Budsjettert', 
                        names='Kategori',
                        title='Budsjett fordeling',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Sammenligning budsjett vs faktisk
                if not st.session_state.budsjett.empty:
                    # Fjern rader der alt er 0
                    compare_df = st.session_state.budsjett[
                        (st.session_state.budsjett['Budsjettert'] > 0) | 
                        (st.session_state.budsjett['Faktisk'] > 0)
                    ].copy()
                    
                    if not compare_df.empty:
                        fig = px.bar(
                            compare_df,
                            x='Kategori',
                            y=['Budsjettert', 'Faktisk', 'Betalt'],
                            title='Budsjett vs. Faktisk vs. Betalt',
                            barmode='group'
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Rediger budsjett")
        
        # Velg kategori å redigere
        kategori_å_redigere = st.selectbox("Velg kategori", st.session_state.budsjett['Kategori'].tolist())
        
        kategori_idx = st.session_state.budsjett[st.session_state.budsjett['Kategori'] == kategori_å_redigere].index[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            ny_budsjettert = st.number_input(
                "Budsjettert beløp", 
                min_value=0, 
                value=int(st.session_state.budsjett.at[kategori_idx, 'Budsjettert'])
            )
            
            ny_faktisk = st.number_input(
                "Faktisk beløp", 
                min_value=0, 
                value=int(st.session_state.budsjett.at[kategori_idx, 'Faktisk'])
            )
            
            ny_betalt = st.number_input(
                "Betalt beløp", 
                min_value=0, 
                max_value=int(ny_faktisk),
                value=min(int(st.session_state.budsjett.at[kategori_idx, 'Betalt']), int(ny_faktisk))
            )
        
        with col2:
            ny_beskrivelse = st.text_area(
                "Beskrivelse", 
                value=st.session_state.budsjett.at[kategori_idx, 'Beskrivelse']
            )
        
        if st.button("Oppdater budsjett"):
            st.session_state.budsjett.at[kategori_idx, 'Budsjettert'] = ny_budsjettert
            st.session_state.budsjett.at[kategori_idx, 'Faktisk'] = ny_faktisk
            st.session_state.budsjett.at[kategori_idx, 'Betalt'] = ny_betalt
            st.session_state.budsjett.at[kategori_idx, 'Beskrivelse'] = ny_beskrivelse
            
            st.success(f"Budsjett for {kategori_å_redigere} oppdatert!")
        
        # Legg til ny kategori
        st.subheader("Legg til ny kategori")
        
        ny_kategori_navn = st.text_input("Navn på ny kategori")
        
        if st.button("Legg til kategori"):
            if ny_kategori_navn and ny_kategori_navn not in st.session_state.budsjett['Kategori'].values:
                ny_kategori = pd.DataFrame({
                    'Kategori': [ny_kategori_navn],
                    'Budsjettert': [0],
                    'Faktisk': [0],
                    'Betalt': [0],
                    'Beskrivelse': [''],
                })
                
                st.session_state.budsjett = pd.concat([st.session_state.budsjett, ny_kategori], ignore_index=True)
                st.success(f"Kategori {ny_kategori_navn} lagt til!")
            else:
                st.error("Fyll inn et unikt kategorinavn.")
