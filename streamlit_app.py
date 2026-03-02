"""
Sogelink — Commercial Intelligence Dashboard
=============================================
Two tabs: Metrics + Réassignation
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Sogelink — Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background: rgba(47,84,150,0.10); padding:10px; border-radius:8px; border-left:4px solid #2F5496; }
    div[data-testid="stMetricValue"] { font-size:1.5rem; color:#e2e8f0 !important; }
    div[data-testid="stMetricLabel"] { color:#94a3b8 !important; }
    div[data-testid="stMetricDelta"] { font-size:0.78rem; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & ORG CHART
# =============================================================================
CAPACITY = {'Enterprise':4,'Key Account':4,'MM':3,'SMB':3,'T1':6,'T2':4,'T3':4,'T4':3}
MAX_ACT = 1410
CHURN = 0.03
NRR = 1.20

ORG_RAW = """Thomas CAUWE;Private - SMB D&E Manager;Private
Beatrice DEMONT;Private - SMB D&E Contractors Account Manager;Private
Emmanuelle MORILLE TOUBLANC;Private - SMB D&E Contractors Account Manager;Private
Cecile RIAHI;Private - SMB D&E Contractors Account Manager;Private
Zohra SABER;Private - SMB D&E Contractors Account Manager;Private
Cecile CHERHAL;Private - SMB D&E Contractors Account Manager;Private
Marie MAHEO;Private - SMB D&E Contractors Account Manager;Private
Patricia BIZIEN;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Marie-France DURAND;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Karine ROUE;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Aurelie SAVIDAN;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Virginie VESCHI;Private - SMB CBYD Manager;Private
Zahia BENMANSOUR;Private - SMB CBYD Account Manager;Private
Cloe BIA;Private - SMB CBYD Account Manager;Private
Florence BARJON;Private - SMB CBYD Account Manager;Private
Arnaud CERESA;Private - SMB CBYD Account Manager;Private
Abderrahmen BENALI;Private - SMB CBYD Account Manager;Private
Fares Hamlat;Private - SMB CBYD Account Manager;Private
Albin HUGUES;Private - SMB CBYD Account Manager;Private
Amandine LANNIER;Private - SMB CBYD Account Manager;Private
Sebastien LOPEZ;Private - SMB CBYD Account Manager;Private
Lea PITINZANO;Private - SMB CBYD Account Manager;Private
Elodie SAINTE-MARIE;Private - SMB CBYD Account Manager;Private
Mathias ALFANO;Private - SMB CBYD Account Manager;Private
Quentin TROJANI;Private - SMB CBYD Account Manager;Private
Loukas VENTURA;Private - SMB CBYD Account Manager;Private
Julie MERLAT;Private - SMB CBYD Account Manager;Private
Alain BORNET;Private - MM & Enterprise Manager;Private
Robin BURRUS;Private - MM & Enterprise Account Manager;Private
Yoan LELEU;Private - MM & Enterprise Account Manager;Private
Thomas MELLET;Private - MM & Enterprise Account Manager;Private
Mickael Iochem;Private - MM & Enterprise Account Manager;Private
Jean-Francois ROBERT;Private - MM & Enterprise Account Manager;Private
TBH AE;Private - MM & Enterprise Account Manager;Private
Christine EVAIN;Private - Renewals Manager;Private
Malika TARZOUT;Private - Contractors Renewal Manager;Private
Mireille GUILLEMINEAU;Private - Contractors Renewal Manager;Private
Elise MARTINEAU;Private - Contractors Renewal Manager;Private
Charline QUEFFELEC;Private - Surveyors & Design Offices Renewal Manager;Private
Marie-Reine FLIPPOT;Private - Surveyors & Design Offices Renewal Manager;Private
Quentin DECK;Public - ex M&M - Manager;Public
Simon TONY;Public - ex M&M - Account Manager;Public
Guillaume CAGNA;Public - ex M&M - Account Manager;Public
Laetitia TRIGO;Public - ex M&M - Account Manager - Netysis;Public
Morgane CURIAL;Public - ex M&M - Account Manager;Public
Pierre-Antoine MARQUAND;Public - ex M&M - Account Manager;Public
Bryan TUGLER;Public - ex M&M - Account Manager;Public
Diego PINAUDEAU;Public - ex M&M - Account Manager;Public
Thibaut DUPONT;Public - ex M&M - Account Manager;Public
Anissa EL BAHRI;Public - ex M&M - Account Manager;Public
Margaux LORENTE;Public - ex M&M - Account Manager;Public
William ILUNGA;Public - ex M&M - Account Manager;Public
Valentin BRIDE;Public - ex M&M - Account Manager;Public
Alexandre PENTECOUTEAU;Public - ex M&M - Account Manager;Public
Marion ANCIAN;Public - ex-CBYD - Manager;Public
Amandine BORJON-BLIND;Public - ex-CBYD - Account Manager;Public
Clara SATGER;Public - ex-CBYD - Account Manager;Public
Amandine DA SILVA;Public - ex-CBYD - Account Manager;Public
Mounira EL HAFI;Public - ex-CBYD - Account Manager;Public
Justine TRANCHANT;Public - ex-CBYD - Account Manager;Public
Remy GOUTALAND;Public - ex-CBYD - Account Manager;Public
Alexandre JULIA;Public - ex-CBYD - Account Manager;Public
Zacharia RAMANI;Public - ex-CBYD - Account Manager;Public
Lea BENEDETTI;Public - ex-CBYD - Account Manager;Public
Florent TREHET;Public - ex-DIAG - Team Lead;Public
Arnaud BRIDAY;Public - ex-DIAG - Account Manager;Public
Pierre-Louis ASSO;Public - ex-DIAG - Account Manager;Public
Raphael CATHERIN;Public - ex-DIAG - Account Manager;Public
Mathieu LOUPIAS;Public - ex-DIAG - Account Manager;Public
Baptiste Pasquier guillard;Public - ex-DIAG - Account Manager;Public
Aymerick Dechamps-cottin;Public - ex-DIAG - Account Manager;Public
Julien CAEN;Public - ex-DIAG - Account Manager;Public
1 MANAGER TBH;Public - Key Account Manager;Public
Gildas KERNEIS;Public - Key Account - Account Manager;Public
Tiffany KAAS CHEVALIER;Public - Key Account - Account Manager;Public
1 KAM TBH;Public - Key Account - Account Manager;Public
Kelian HOULMIERE;Public - Key Account - Subsidiary Account Manager;Public
Aurelien Tabard;Public - Key Account - Subsidiary Account Manager;Public
Margot PRADINES;Public - Key Account - Subsidiary Account Manager;Public
Mirabelle RAMOND;Public - Renewals - Team Manager;Public
Beatrice Douine;Public - Renewals Manager;Public
Camille LEDAIN;Public - Renewals Manager;Public
Margot MERLET;Public - Renewals Manager;Public
Nadia Guery;Public - Renewals Manager;Public
Stephanie REILLER;Public - Renewals Manager;Public
Clarisse SCATTOLIN;Public - Renewals Manager;Public"""

def parse_org():
    rows = []
    for line in ORG_RAW.strip().split('\n'):
        p = line.split(';')
        if len(p)>=3:
            name,role,seg = p[0].strip(),p[1].strip(),p[2].strip()
            rows.append({'AM_Name':name,'Role':role,'Segment':seg,
                         'Is_Manager':'Manager' in role and 'Account Manager' not in role and 'Renewal Manager' not in role,
                         'Is_Renewal':'Renewal' in role})
    return pd.DataFrame(rows)

ARR_PRODUCTS = {'Infra':'ARR Infra','Topo':'ARR Topo','Elec & Gas':'ARR Elec & Gas',
    'DICT':'ARR DICT','Geo Expertise':'ARR Geo Expertise','Diag':'ARR Diag','Expo':'ARR Expo','Coordin':'ARR Coordin'}

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_base():
    df = pd.read_csv('./base_sogelink.csv', sep=';', low_memory=False)
    mask = (df['ARR Dec 2025']>0) & (df['Status']=='Client') & (df['bucket_CA']>0) & (df['Secteur_activite'].notna())
    bench = df[mask].groupby(['Secteur_activite','bucket_CA']).agg(
        n=('ARR Dec 2025','count'), p75=('ARR Dec 2025', lambda x: x.quantile(0.75))).reset_index()
    bench = bench[bench['n']>=10]
    bd = {(r['Secteur_activite'],int(r['bucket_CA'])):r['p75'] for _,r in bench.iterrows()}
    df['Potentiel'] = df.apply(lambda r: bd.get((r['Secteur_activite'],int(r['bucket_CA'])),np.nan)
        if pd.notna(r['Secteur_activite']) and pd.notna(r['bucket_CA']) and r['bucket_CA']>0 else np.nan, axis=1)
    df['Reste_a_depenser'] = (df['Potentiel']-df['ARR Dec 2025']).clip(lower=0)
    df['Taux_penetration'] = np.where(df['Potentiel']>0, df['ARR Dec 2025']/df['Potentiel']*100, np.nan)
    def pb(p):
        if pd.isna(p): return 'N/A'
        if p>=100: return '≥ P75'
        if p>=50: return '50-99%'
        if p>=25: return '25-49%'
        return '< 25%'
    df['Pen_Band'] = df['Taux_penetration'].apply(pb)
    df['Activities'] = df['Classification'].map(CAPACITY).fillna(3)
    # Dominant product
    arr_cols = {'DICT':'ARR DICT','Infra':'ARR Infra','Topo':'ARR Topo','Elec':'ARR Elec & Gas',
                'Geo':'ARR Geo Expertise','Diag':'ARR Diag','Expo':'ARR Expo','Coordin':'ARR Coordin'}
    def dom_prod(row):
        mx,mp = 0,'None'
        for p,c in arr_cols.items():
            v = row.get(c,0)
            if pd.notna(v) and v>mx: mx,mp = v,p
        return mp
    df['Dom_Product'] = df.apply(dom_prod, axis=1)
    return df, bench

df_full, bench_raw = load_base()
org_df = parse_org()

# =============================================================================
# SIDEBAR FILTERS
# =============================================================================
st.sidebar.title("📊 Sogelink Intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtres")
sel_classif = st.sidebar.multiselect("Classification", sorted(df_full['Classification'].dropna().unique()), default=sorted(df_full['Classification'].dropna().unique()))
sel_teams = st.sidebar.multiselect("Sogelink Team", sorted(df_full['FR_Sogelink_Team'].dropna().unique()), default=sorted(df_full['FR_Sogelink_Team'].dropna().unique()))
sel_secteurs = st.sidebar.multiselect("Secteur", sorted(df_full['Secteur_activite'].dropna().unique()), default=sorted(df_full['Secteur_activite'].dropna().unique()))
sel_status = st.sidebar.multiselect("Status", ['Client','Prospect'], default=['Client','Prospect'])

df = df_full[
    (df_full['Classification'].isin(sel_classif)) & (df_full['FR_Sogelink_Team'].isin(sel_teams)) &
    (df_full['Secteur_activite'].isin(sel_secteurs)) & (df_full['Status'].isin(sel_status))
].copy()
st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(df):,}** / {len(df_full):,} comptes")

# =============================================================================
# REASSIGNMENT ENGINE
# =============================================================================
def build_am_registry():
    ams = []
    for _,r in org_df.iterrows():
        if r['Is_Manager'] or r['Is_Renewal']: continue
        role = r['Role']
        ams.append({'name':r['AM_Name'],'role':role,'segment':r['Segment'],
            'ka':'Key Account' in role, 'mm_ent':'MM & Enterprise' in role,
            'cbyd':'CBYD' in role or 'ex-CBYD' in role, 'de':'D&E' in role,
            'diag':'DIAG' in role or 'ex-DIAG' in role, 'mm_pub':'ex M&M' in role,
            'contractors':'Contractor' in role, 'surveyors':'Surveyor' in role or 'Design Office' in role,
            'subsidiary':'Subsidiary' in role})
    return ams

def score_am(acct, am, am_load, avg_load):
    seg = 'Public' if acct['pp']=='PUBLIC' else 'Private'
    if am['segment']!=seg: return None,[]
    s,reasons = 0,[]
    cls = acct['cls']
    if cls in ('Enterprise','Key Account'):
        if am['ka']: s+=30; reasons.append('KA')
        elif am['mm_ent']: s+=25; reasons.append('MM/Ent')
        elif am['mm_pub']: s+=15; reasons.append('M&M Pub')
        else: s-=10
    elif cls=='MM':
        if am['mm_ent']: s+=25; reasons.append('MM')
        elif am['mm_pub']: s+=20; reasons.append('M&M Pub')
    else:
        if not am['ka'] and not am['subsidiary']: s+=10; reasons.append('SMB/Tx ok')
    dom = acct['dom']
    if dom=='DICT':
        if am['cbyd']: s+=20; reasons.append('CBYD')
        elif am['mm_pub']: s+=10
    elif dom in ('Infra','Topo','Elec','Geo'):
        if am['de'] or am['surveyors']: s+=20; reasons.append('D&E')
    elif dom=='Diag':
        if am['diag']: s+=20; reasons.append('DIAG')
    elif dom=='Coordin':
        if am['mm_pub'] or am['cbyd']: s+=15; reasons.append('Coordin')
    sect = str(acct.get('sect',''))
    if 'Contractor' in sect and am['contractors']: s+=15; reasons.append('Ind:Contr')
    elif ('Surveyor' in sect or 'Design' in sect) and (am['surveyors'] or am['de']): s+=15; reasons.append('Ind:Surv/DE')
    elif 'Local auth' in sect and (am['mm_pub'] or am['cbyd'] or am['diag']): s+=10; reasons.append('Ind:Public')
    if avg_load>0:
        if am_load<avg_load: s+=5; reasons.append('↓charge')
        elif am_load>avg_load*1.3: s-=5; reasons.append('↑charge')
    if acct['arr']>50000 and (am['mm_ent'] or am['ka']): s+=10; reasons.append('High ARR')
    return s,reasons

@st.cache_data
def run_auto_reassign(_df_json):
    dfa = pd.read_json(io.StringIO(_df_json))
    am_reg = build_am_registry()
    am_load = {a['name']:0 for a in am_reg}
    for c in ['B&S','D&E','M&M']:
        if c in dfa.columns:
            for n in dfa[c].dropna(): am_load[n] = am_load.get(n,0)+1
    avg = np.mean(list(am_load.values())) if am_load else 100
    cli = dfa[dfa['Status']=='Client']
    unasgn = cli[cli[['B&S','D&E','M&M']].isna().all(axis=1)]
    results = []
    for _,row in unasgn.iterrows():
        acct = {'pp':row.get('Public_Prive',''),'cls':row.get('Classification','SMB'),
                'dom':row.get('Dom_Product','None'),'sect':row.get('Secteur_activite',''),'arr':row.get('ARR Dec 2025',0)}
        scored = []
        for am in am_reg:
            sc,rea = score_am(acct, am, am_load.get(am['name'],0), avg)
            if sc is not None: scored.append({'am':am['name'],'role':am['role'],'score':sc,'reasons':' | '.join(rea[:4])})
        scored.sort(key=lambda x:x['score'], reverse=True)
        best = scored[0] if scored else None
        results.append({
            'Account ID':row['Account ID'],'Account Name':row['Account Name'],
            'Classification':row['Classification'],'Public_Prive':row['Public_Prive'],
            'Team':row.get('FR_Sogelink_Team',''),'Secteur':row.get('Secteur_activite',''),
            'ARR':row['ARR Dec 2025'],'Dom_Product':acct['dom'],
            'Reco_AM':best['am'] if best else '','Reco_Role':best['role'] if best else '',
            'Score':best['score'] if best else 0,'Raisons':best['reasons'] if best else '',
        })
        if best: am_load[best['am']] = am_load.get(best['am'],0)+1
    return pd.DataFrame(results), am_load

# =============================================================================
# TABS
# =============================================================================
tab1, tab2 = st.tabs(["📊 Metrics", "🔄 Réassignation"])

# =============================================================================
# TAB 1: METRICS
# =============================================================================
with tab1:
    st.title("📊 Vue commerciale Sogelink")

    # ── KPIs ──
    nb_cli = len(df[df['Status']=='Client'])
    nb_pro = len(df[df['Status']=='Prospect'])
    arr_t = df['ARR Dec 2025'].sum()
    ps_t = df['PS 2025'].sum()
    ops_t = df['ops_closed_won'].sum()
    pot_t = df['Potentiel'].sum()
    reste_t = df['Reste_a_depenser'].sum()
    couv = (arr_t/pot_t*100) if pot_t>0 else 0

    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("Comptes",f"{len(df):,}",f"{nb_cli:,} cli · {nb_pro:,} prosp")
    c2.metric("ARR",f"{arr_t/1e6:.1f} M€",help="Annual Recurring Revenue — Déc 2025")
    c3.metric("PS 2025",f"{ps_t/1e6:.1f} M€")
    c4.metric("Ops Won",f"{ops_t:,.0f}")
    c5.metric("Potentiel P75",f"{pot_t/1e6:.1f} M€",help="P75 ARR par Secteur × bucket CA")
    c6.metric("Reste à dépenser",f"{reste_t/1e6:.1f} M€",
              delta=f"{reste_t/arr_t*100:.0f}% de l'ARR" if arr_t else "")
    c7.metric("Couverture",f"{couv:.1f}%",delta=f"{100-couv:.0f}% restant",delta_color="inverse")
    st.markdown("---")

    # ── Secteur & Pénétration ──
    cL,cR = st.columns([3,2])
    with cL:
        st.subheader("ARR vs Potentiel par secteur")
        bs = df.groupby('Secteur_activite').agg(arr=('ARR Dec 2025','sum'),pot=('Potentiel','sum')).reset_index().sort_values('pot',ascending=False)
        fig=go.Figure()
        fig.add_trace(go.Bar(name='ARR',x=bs['Secteur_activite'],y=bs['arr'],marker_color='#2F5496',
                             text=bs['arr'].apply(lambda x:f"{x/1e6:.1f}M"),textposition='inside'))
        fig.add_trace(go.Bar(name='Potentiel P75',x=bs['Secteur_activite'],y=bs['pot'],marker_color='#10b981',opacity=0.5,
                             text=bs['pot'].apply(lambda x:f"{x/1e6:.1f}M"),textposition='inside'))
        fig.update_layout(barmode='overlay',height=400,xaxis_tickangle=30,legend=dict(orientation='h',y=1.12))
        st.plotly_chart(fig,use_container_width=True)
    with cR:
        st.subheader("Pénétration (clients)")
        bo=['≥ P75','50-99%','25-49%','< 25%','N/A']
        bc_map={'≥ P75':'#10b981','50-99%':'#3b82f6','25-49%':'#f59e0b','< 25%':'#ef4444','N/A':'#94a3b8'}
        bdf=df[df['Status']=='Client']['Pen_Band'].value_counts().reindex(bo).fillna(0).reset_index()
        bdf.columns=['Band','Count']
        fp=px.pie(bdf,values='Count',names='Band',color='Band',color_discrete_map=bc_map,hole=0.45)
        fp.update_layout(height=400,legend=dict(orientation='h',y=-0.1))
        fp.update_traces(textinfo='value+percent',textfont_size=12)
        st.plotly_chart(fp,use_container_width=True)
    st.markdown("---")

    # ── Produits & Classification ──
    cL2,cR2 = st.columns(2)
    with cL2:
        st.subheader("ARR par produit")
        prd=pd.DataFrame([{'Produit':l,'ARR':df[c].sum()} for l,c in ARR_PRODUCTS.items()]).sort_values('ARR',ascending=True)
        fp2=px.bar(prd,x='ARR',y='Produit',orientation='h',color='ARR',color_continuous_scale='Blues',
                   text=prd['ARR'].apply(lambda x:f"{x/1e6:.2f}M€"))
        fp2.update_layout(height=380,showlegend=False,coloraxis_showscale=False)
        fp2.update_traces(textposition='outside')
        st.plotly_chart(fp2,use_container_width=True)
    with cR2:
        st.subheader("Par Classification")
        bcl=df.groupby('Classification').agg(arr=('ARR Dec 2025','sum'),pot=('Potentiel','sum'),
            reste=('Reste_a_depenser','sum'),ncli=('Status',lambda x:(x=='Client').sum()),
            n=('Account ID','count'),ops=('ops_closed_won','sum')).reset_index()
        bcl['couv']=np.where(bcl['pot']>0,(bcl['arr']/bcl['pot']*100).round(1),0)
        st.dataframe(bcl.sort_values('arr',ascending=False),use_container_width=True,hide_index=True,
                     column_config={'Classification':'Class.','n':st.column_config.NumberColumn('Total',format="%d"),
                         'ncli':st.column_config.NumberColumn('Clients',format="%d"),
                         'arr':st.column_config.NumberColumn('ARR',format="%.0f €"),
                         'pot':st.column_config.NumberColumn('Potentiel',format="%.0f €"),
                         'reste':st.column_config.NumberColumn('Reste',format="%.0f €"),
                         'ops':st.column_config.NumberColumn('Ops',format="%d"),
                         'couv':st.column_config.NumberColumn('Couv %',format="%.1f%%")})
    st.markdown("---")

    # ── Équipe & Capacité ──
    st.subheader("👥 Équipe & Capacité")
    cT1,cT2 = st.columns([3,2])
    with cT1:
        btm=df.groupby('FR_Sogelink_Team').agg(n=('Account ID','count'),ncli=('Status',lambda x:(x=='Client').sum()),
            arr=('ARR Dec 2025','sum'),pot=('Potentiel','sum'),reste=('Reste_a_depenser','sum'),
            ops=('ops_closed_won','sum'),acts=('Activities','sum')).reset_index()
        amc=org_df[~org_df['Is_Manager']&~org_df['Is_Renewal']].groupby('Segment').size()
        tam={'KA':amc.get('Public',0),'PUBLIC':amc.get('Public',0),'PRIVE':amc.get('Private',0)}
        btm['ams']=btm['FR_Sogelink_Team'].map(tam).fillna(0).astype(int)
        btm['arr_am']=np.where(btm['ams']>0,btm['arr']/btm['ams'],0)
        btm['charge']=np.where(btm['ams']>0,(btm['acts']/btm['ams']/MAX_ACT*100).round(0),0)
        st.dataframe(btm.sort_values('arr',ascending=False),use_container_width=True,hide_index=True,
                     column_config={'FR_Sogelink_Team':'Team','n':st.column_config.NumberColumn('Comptes',format="%d"),
                         'ncli':st.column_config.NumberColumn('Clients',format="%d"),
                         'arr':st.column_config.NumberColumn('ARR',format="%.0f €"),
                         'pot':st.column_config.NumberColumn('Potentiel',format="%.0f €"),
                         'reste':st.column_config.NumberColumn('Reste',format="%.0f €"),
                         'ops':st.column_config.NumberColumn('Ops',format="%d"),
                         'ams':st.column_config.NumberColumn('AMs',format="%d"),
                         'arr_am':st.column_config.NumberColumn('ARR/AM',format="%.0f €"),
                         'charge':st.column_config.NumberColumn('Charge %',format="%.0f%%"),
                         'acts':None})
    with cT2:
        bt2=btm.sort_values('arr',ascending=False)
        ft=go.Figure()
        ft.add_trace(go.Bar(name='ARR',x=bt2['FR_Sogelink_Team'],y=bt2['arr'],marker_color='#2F5496'))
        ft.add_trace(go.Bar(name='Reste',x=bt2['FR_Sogelink_Team'],y=bt2['reste'],marker_color='#f59e0b'))
        ft.update_layout(barmode='stack',height=300,legend=dict(orientation='h',y=1.12))
        st.plotly_chart(ft,use_container_width=True)
    with st.expander("📋 Organigramme cible (Avril 2026)"):
        st.dataframe(org_df.sort_values(['Segment','Is_Manager','Role'],ascending=[True,False,True]),
                     use_container_width=True,hide_index=True)
    st.markdown("---")

    # ── Projections ──
    st.subheader("📈 Projections (3% churn, 120% NRR)")
    pr=[]
    for cls in df['Classification'].dropna().unique():
        cd=df[(df['Classification']==cls)&(df['Status']=='Client')]
        a=cd['ARR Dec 2025'].sum(); ch=a*CHURN; bk=a*(NRR-1); r=cd['Reste_a_depenser'].sum()
        pr.append({'Classification':cls,'ARR':a,'Churn 3%':ch,'Post-churn':a-ch,
                   'Bookings':bk,'Ending ARR':a*NRR,'Reste dispo':r,
                   'Couv %':min(r/bk*100,999) if bk>0 else 0})
    pdff=pd.DataFrame(pr).sort_values('ARR',ascending=False)
    tp=pdff[['ARR','Churn 3%','Post-churn','Bookings','Ending ARR','Reste dispo']].sum()
    cp1,cp2,cp3,cp4,cp5=st.columns(5)
    cp1.metric("ARR clients",f"{tp['ARR']/1e6:.1f} M€")
    cp2.metric("Churn",f"-{tp['Churn 3%']/1e6:.2f} M€",delta="-3%",delta_color="inverse")
    cp3.metric("Post-churn",f"{tp['Post-churn']/1e6:.1f} M€")
    cp4.metric("Bookings cible",f"{tp['Bookings']/1e6:.1f} M€",help="Pour 120% NRR")
    cp5.metric("Ending ARR",f"{tp['Ending ARR']/1e6:.1f} M€",delta="+20% NRR")
    st.dataframe(pdff,use_container_width=True,hide_index=True,
                 column_config={c:st.column_config.NumberColumn(format="%.0f €") for c in
                                ['ARR','Churn 3%','Post-churn','Bookings','Ending ARR','Reste dispo']}|
                 {'Couv %':st.column_config.NumberColumn(format="%.0f%%")})
    fw=go.Figure(go.Waterfall(x=['ARR','Churn','Post-churn','Bookings','Ending'],
        y=[tp['ARR'],-tp['Churn 3%'],0,tp['Bookings'],0],
        measure=['absolute','relative','total','relative','total'],
        text=[f"{tp['ARR']/1e6:.1f}M",f"-{tp['Churn 3%']/1e6:.1f}M",'',f"+{tp['Bookings']/1e6:.1f}M",f"{tp['Ending ARR']/1e6:.1f}M"],
        textposition='outside',connector=dict(line=dict(color='#475569',width=1)),
        increasing=dict(marker=dict(color='#10b981')),decreasing=dict(marker=dict(color='#ef4444')),
        totals=dict(marker=dict(color='#2F5496'))))
    fw.update_layout(height=320,showlegend=False)
    st.plotly_chart(fw,use_container_width=True)
    st.markdown("---")

    # ── Key Accounts ──
    st.subheader("🏢 Key Accounts")
    cli=df[df['Status']=='Client']
    ka=cli.groupby('Ultimate_Parent').agg(n=('Account ID','count'),arr=('ARR Dec 2025','sum'),
        pot=('Potentiel','sum'),reste=('Reste_a_depenser','sum'),
        cls=('Classification',lambda x:', '.join(sorted(x.dropna().unique())))).reset_index()
    ka['couv']=np.where(ka['pot']>0,(ka['arr']/ka['pot']*100).round(1),0)
    ka=ka[ka['arr']>0].sort_values('arr',ascending=False)
    topn=st.slider("Groupes",10,100,30,5)
    kat=ka.head(topn)
    ck1,ck2=st.columns([3,2])
    with ck1:
        st.dataframe(kat,use_container_width=True,hide_index=True,
                     column_config={'Ultimate_Parent':'Groupe','n':st.column_config.NumberColumn('Comptes',format="%d"),
                         'arr':st.column_config.NumberColumn('ARR',format="%.0f €"),
                         'pot':st.column_config.NumberColumn('Potentiel',format="%.0f €"),
                         'reste':st.column_config.NumberColumn('Reste',format="%.0f €"),
                         'couv':st.column_config.NumberColumn('Couv %',format="%.0f%%"),'cls':'Class.'})
    with ck2:
        t15=kat.head(15)
        fk=go.Figure()
        fk.add_trace(go.Bar(name='ARR',y=t15['Ultimate_Parent'],x=t15['arr'],orientation='h',marker_color='#2F5496'))
        fk.add_trace(go.Bar(name='Reste',y=t15['Ultimate_Parent'],x=t15['reste'],orientation='h',marker_color='#f59e0b',opacity=0.7))
        fk.update_layout(barmode='stack',height=480,yaxis=dict(autorange='reversed'),legend=dict(orientation='h',y=1.08))
        st.plotly_chart(fk,use_container_width=True)
    st.markdown("---")

    # ── Top comptes ──
    st.subheader("🎯 Top comptes — Reste à dépenser")
    tv=st.radio("Vue",['Clients','Clients + Prospects'],horizontal=True,key='tv')
    tb=df[(df['Status']=='Client')&(df['ARR Dec 2025']>0)] if tv=='Clients' else df[df['Potentiel'].notna()]
    t30=tb.nlargest(30,'Reste_a_depenser')[['Account Name','Classification','FR_Sogelink_Team','Secteur_activite',
        'Status','ARR Dec 2025','Potentiel','Reste_a_depenser','Taux_penetration','Ultimate_Parent']]
    st.dataframe(t30,use_container_width=True,hide_index=True,
                 column_config={'Account Name':'Compte','Classification':'Class.','FR_Sogelink_Team':'Team',
                     'Secteur_activite':'Secteur','ARR Dec 2025':st.column_config.NumberColumn('ARR',format="%.0f €"),
                     'Potentiel':st.column_config.NumberColumn('Potentiel',format="%.0f €"),
                     'Reste_a_depenser':st.column_config.NumberColumn('Reste',format="%.0f €"),
                     'Taux_penetration':st.column_config.NumberColumn('Pénét.',format="%.1f%%"),
                     'Ultimate_Parent':'Groupe'})
    st.markdown("---")

    # ── Heatmap ──
    st.subheader("🗺️ Heatmap — Mix produit × secteur")
    hb=df[df['Status']=='Client']
    hd=[{'Secteur':s,**{l:hb[hb['Secteur_activite']==s][c].sum() for l,c in ARR_PRODUCTS.items()}}
        for s in hb['Secteur_activite'].dropna().unique()]
    hdf=pd.DataFrame(hd).set_index('Secteur')
    hdf=hdf.loc[hdf.sum(axis=1).sort_values(ascending=False).index]
    hn=hdf.div(hdf.sum(axis=1),axis=0).fillna(0)*100
    fh=px.imshow(hn.values,x=hn.columns.tolist(),y=hn.index.tolist(),
                 color_continuous_scale='Blues',labels=dict(color='% mix'),text_auto='.0f',aspect='auto')
    fh.update_layout(height=420)
    st.plotly_chart(fh,use_container_width=True)
    st.markdown("---")

    # ── Export ──
    st.subheader("📥 Export")
    exp_cols=['Account ID','Account Name','Status','Classification','FR_Sogelink_Team','Secteur_activite','bucket_CA',
        'Public_Prive','ARR Dec 2025','ARR Infra','ARR Topo','ARR Elec & Gas','ARR DICT','ARR Geo Expertise',
        'ARR Diag','ARR Expo','ARR Coordin','PS 2025','ops_closed_won','Potentiel','Reste_a_depenser',
        'Taux_penetration','Pen_Band','Chiffre_affaires_annuel','Employes','Ultimate_Parent']
    exp=df[[c for c in exp_cols if c in df.columns]]
    cd1,cd2=st.columns(2)
    with cd1:
        st.download_button("📄 CSV",data=exp.to_csv(index=False,sep=';'),
                           file_name="sogelink_potentiel.csv",mime="text/csv",type="primary")
    with cd2:
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine='openpyxl') as w:
            exp.to_excel(w,sheet_name='Potentiel',index=False)
            be=bench_raw[bench_raw['n']>=10].copy(); be.columns=['Secteur','Bucket_CA','N','P75_ARR']
            be.to_excel(w,sheet_name='Benchmarks',index=False)
            pdff.to_excel(w,sheet_name='Projections',index=False)
        st.download_button("📊 Excel",data=buf.getvalue(),file_name="sogelink_complet.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with st.expander("ℹ️ Méthodologie"):
        st.markdown("""**Potentiel** = P75 ARR par Secteur × bucket_CA (clients, n≥10).
**Reste** = max(0, Potentiel − ARR). **Capacité** : activités/an par classification, max 1410/AM.
**Projections** : churn 3%, NRR 120%.""")

# =============================================================================
# TAB 2: RÉASSIGNATION
# =============================================================================
with tab2:
    st.title("🔄 Réassignation des comptes")

    # Session state
    if 'decisions' not in st.session_state:
        st.session_state.decisions = {}

    # ── Current ownership overview ──
    cli_all = df_full[df_full['Status'] == 'Client'].copy()
    has_am = cli_all[cli_all[['B&S', 'D&E', 'M&M']].notna().any(axis=1)]
    no_am = cli_all[cli_all[['B&S', 'D&E', 'M&M']].isna().all(axis=1)]

    # Sub-tabs for auto vs manual
    sub_auto, sub_manual, sub_simulation = st.tabs([
        "⚡ Auto-réassignation",
        "🔧 Workbench manuel",
        "📈 Simulation"
    ])

    # ─────────────────────────────────────────────────────────────────────
    # SUB-TAB: AUTO
    # ─────────────────────────────────────────────────────────────────────
    with sub_auto:
        st.subheader("⚡ Réassignation automatique")

        st.markdown(f"""
        **État actuel :**
        - **{len(has_am):,}** clients avec AM assigné ({has_am['ARR Dec 2025'].sum()/1e6:.1f}M€ ARR)
        - **{len(no_am):,}** clients **sans AM** ({no_am['ARR Dec 2025'].sum()/1e6:.1f}M€ ARR)
        """)

        # Current AM load
        st.markdown("**Charge actuelle par AM :**")
        am_load_data = []
        for c in ['B&S', 'D&E', 'M&M']:
            for am_name, cnt in cli_all[c].value_counts().items():
                arr_am = cli_all[cli_all[c] == am_name]['ARR Dec 2025'].sum()
                am_load_data.append({'AM': am_name, 'Canal': c, 'Comptes': cnt, 'ARR': arr_am})
        am_load_df = pd.DataFrame(am_load_data)
        if not am_load_df.empty:
            am_agg = am_load_df.groupby('AM').agg(
                comptes=('Comptes', 'sum'), arr=('ARR', 'sum'),
                canaux=('Canal', lambda x: ', '.join(sorted(x.unique())))
            ).reset_index().sort_values('arr', ascending=False)

            cL, cR = st.columns([2, 3])
            with cL:
                st.dataframe(am_agg.head(20), use_container_width=True, hide_index=True,
                             column_config={
                                 'AM': 'AM', 'comptes': st.column_config.NumberColumn('Comptes', format="%d"),
                                 'arr': st.column_config.NumberColumn('ARR', format="%.0f €"),
                                 'canaux': 'Canaux'
                             })
            with cR:
                fam = px.bar(am_agg.head(20).sort_values('comptes', ascending=True),
                             x='comptes', y='AM', orientation='h', color='arr',
                             color_continuous_scale='Blues',
                             labels={'comptes': '# Comptes', 'arr': 'ARR'})
                fam.update_layout(height=450, coloraxis_showscale=False)
                st.plotly_chart(fam, use_container_width=True)

        st.markdown("---")

        # Run auto reassignment
        st.subheader("🚀 Lancer la réassignation automatique")
        st.markdown("""
        L'algorithme affecte chaque compte **non assigné** au meilleur AM disponible selon :
        - **Segment** : Public → AM Public, Privé → AM Privé (filtre dur)
        - **Classification** : Enterprise/KA → AM KA ou MM/Ent, SMB → AM CBYD/D&E
        - **Produit dominant** : DICT → CBYD, Infra/Topo → D&E, Diag → DIAG
        - **Secteur** : Contractors → AM Contractors, Surveyors → AM Surveyors
        - **Équilibrage** : préférence aux AM moins chargés
        """)

        col_run, col_info = st.columns([1, 2])
        with col_run:
            run_auto = st.button("🚀 Lancer", type="primary", key="run_auto")
        with col_info:
            st.info(f"Va réassigner **{len(no_am):,}** clients sans AM")

        if run_auto:
            with st.spinner("Calcul en cours..."):
                result_df, new_loads = run_auto_reassign(df_full.to_json())

            st.session_state.auto_results = result_df
            st.session_state.auto_loads = new_loads
            st.success(f"✅ {len(result_df)} comptes réassignés !")

        # Display results
        if 'auto_results' in st.session_state and st.session_state.auto_results is not None:
            res = st.session_state.auto_results

            st.markdown("---")
            st.subheader("Résultats de la réassignation automatique")

            # KPIs
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Comptes réassignés", f"{len(res):,}")
            rc2.metric("ARR réassigné", f"{res['ARR'].sum()/1e6:.1f} M€")
            rc3.metric("Score moyen", f"{res['Score'].mean():.1f}")
            rc4.metric("AMs utilisés", f"{res['Reco_AM'].nunique()}")

            # New load distribution
            st.markdown("**Nouvelle charge par AM recommandé :**")
            new_load_df = res.groupby('Reco_AM').agg(
                n_new=('Account ID', 'count'),
                arr_new=('ARR', 'sum'),
                score_avg=('Score', 'mean'),
            ).reset_index().sort_values('arr_new', ascending=False)

            st.dataframe(new_load_df, use_container_width=True, hide_index=True,
                         column_config={
                             'Reco_AM': 'AM recommandé',
                             'n_new': st.column_config.NumberColumn('Nouveaux comptes', format="%d"),
                             'arr_new': st.column_config.NumberColumn('ARR ajouté', format="%.0f €"),
                             'score_avg': st.column_config.NumberColumn('Score moyen', format="%.1f"),
                         })

            # Results table with filters
            st.markdown("---")
            st.markdown("**Détail des affectations :**")

            # Filters
            fcl1, fcl2, fcl3 = st.columns(3)
            with fcl1:
                f_team = st.multiselect("Team", res['Team'].dropna().unique().tolist(),
                                        default=res['Team'].dropna().unique().tolist(), key='auto_f_team')
            with fcl2:
                f_cls = st.multiselect("Classification", res['Classification'].dropna().unique().tolist(),
                                       default=res['Classification'].dropna().unique().tolist(), key='auto_f_cls')
            with fcl3:
                f_sort = st.selectbox("Trier par", ['ARR ↓', 'Score ↓', 'AM recommandé'], key='auto_sort')

            res_filt = res[(res['Team'].isin(f_team)) & (res['Classification'].isin(f_cls))]
            if f_sort == 'ARR ↓':
                res_filt = res_filt.sort_values('ARR', ascending=False)
            elif f_sort == 'Score ↓':
                res_filt = res_filt.sort_values('Score', ascending=False)
            else:
                res_filt = res_filt.sort_values('Reco_AM')

            st.dataframe(res_filt.head(100), use_container_width=True, hide_index=True,
                         column_config={
                             'Account ID': None,
                             'Account Name': 'Compte',
                             'Classification': 'Class.',
                             'Public_Prive': 'Pub/Priv',
                             'Team': 'Team',
                             'Secteur': 'Secteur',
                             'ARR': st.column_config.NumberColumn('ARR', format="%.0f €"),
                             'Dom_Product': 'Produit dom.',
                             'Reco_AM': 'AM recommandé',
                             'Reco_Role': 'Rôle AM',
                             'Score': st.column_config.NumberColumn('Score', format="%.0f"),
                             'Raisons': 'Raisons',
                         })

            # Accept all auto → push to decisions
            st.markdown("---")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("✅ Accepter toutes les réassignations auto", type="primary", key="accept_all"):
                    for _, row in res.iterrows():
                        st.session_state.decisions[row['Account ID']] = {
                            'new_owner': row['Reco_AM'],
                            'method': 'auto',
                            'old_owner': 'Non assigné',
                            'arr': row['ARR'],
                            'account_name': row['Account Name'],
                        }
                    st.success(f"✅ {len(res)} décisions enregistrées")
                    st.rerun()
            with ca2:
                # Export auto results
                buf_auto = io.BytesIO()
                with pd.ExcelWriter(buf_auto, engine='openpyxl') as w:
                    res.to_excel(w, sheet_name='Reassignation_Auto', index=False)
                    new_load_df.to_excel(w, sheet_name='Charge_AM', index=False)
                st.download_button("📊 Exporter résultats", data=buf_auto.getvalue(),
                                   file_name="reassignation_auto.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ─────────────────────────────────────────────────────────────────────
    # SUB-TAB: WORKBENCH MANUEL
    # ─────────────────────────────────────────────────────────────────────
    with sub_manual:
        st.subheader("🔧 Workbench — Réassignation manuelle")
        st.markdown(f"**{len(st.session_state.decisions):,}** décisions déjà prises")

        # Select scope
        scope = st.radio("Scope", [
            'Clients sans AM (non encore décidés)',
            'Tous les clients (révision possible)',
        ], horizontal=True, key='wb_scope')

        if scope == 'Clients sans AM (non encore décidés)':
            wb_base = no_am[~no_am['Account ID'].isin(st.session_state.decisions)]
        else:
            wb_base = cli_all.copy()

        # Filters
        wf1, wf2, wf3, wf4 = st.columns(4)
        with wf1:
            wb_team = st.multiselect("Team", wb_base['FR_Sogelink_Team'].dropna().unique().tolist(),
                                     default=wb_base['FR_Sogelink_Team'].dropna().unique().tolist(), key='wb_team')
        with wf2:
            wb_cls = st.multiselect("Classification", wb_base['Classification'].dropna().unique().tolist(),
                                    default=wb_base['Classification'].dropna().unique().tolist(), key='wb_cls')
        with wf3:
            wb_sect = st.multiselect("Secteur", wb_base['Secteur_activite'].dropna().unique().tolist(),
                                     default=wb_base['Secteur_activite'].dropna().unique().tolist(), key='wb_sect')
        with wf4:
            wb_sort = st.selectbox("Trier par", ['ARR ↓', 'Account Name'], key='wb_sort')

        wb_filt = wb_base[
            (wb_base['FR_Sogelink_Team'].isin(wb_team)) &
            (wb_base['Classification'].isin(wb_cls)) &
            (wb_base['Secteur_activite'].isin(wb_sect))
        ]
        if wb_sort == 'ARR ↓':
            wb_filt = wb_filt.sort_values('ARR Dec 2025', ascending=False)
        else:
            wb_filt = wb_filt.sort_values('Account Name')

        st.markdown(f"**{len(wb_filt):,}** comptes affichés")

        # Paginate
        pg_size = 15
        total_pg = max(1, (len(wb_filt) - 1) // pg_size + 1)
        cur_pg = st.number_input("Page", min_value=1, max_value=total_pg, value=1, key='wb_pg')
        pg_df = wb_filt.iloc[(cur_pg-1)*pg_size : cur_pg*pg_size]

        # AM list for manual selection
        am_reg = build_am_registry()
        am_names = [a['name'] for a in am_reg]

        # Display account cards
        for _, row in pg_df.iterrows():
            acct_id = row['Account ID']
            decided = acct_id in st.session_state.decisions
            icon = "✅" if decided else "⚠️"

            current_ams = []
            for c in ['B&S', 'D&E', 'M&M']:
                if pd.notna(row.get(c)):
                    current_ams.append(f"{c}: {row[c]}")
            current_str = ' | '.join(current_ams) if current_ams else 'Aucun'

            with st.expander(
                f"{icon} **{row['Account Name']}** — {row['ARR Dec 2025']:,.0f}€ | "
                f"{row.get('Classification', '')} | {row.get('Secteur_activite', '')}",
                expanded=not decided
            ):
                # Account info
                ci1, ci2, ci3, ci4 = st.columns(4)
                ci1.markdown(f"**AM actuels:** {current_str}")
                ci2.markdown(f"**Segment:** {row.get('Public_Prive', '?')}")
                ci3.markdown(f"**Produit dom.:** {row.get('Dom_Product', '?')}")
                ci4.markdown(f"**Parent:** {row.get('Ultimate_Parent', '—')}")

                # Score candidates
                acct = {
                    'pp': row.get('Public_Prive', ''),
                    'cls': row.get('Classification', 'SMB'),
                    'dom': row.get('Dom_Product', 'None'),
                    'sect': row.get('Secteur_activite', ''),
                    'arr': row.get('ARR Dec 2025', 0),
                }

                # Compute current loads
                cur_loads = {a['name']: 0 for a in am_reg}
                for c in ['B&S', 'D&E', 'M&M']:
                    for n in cli_all[c].dropna():
                        cur_loads[n] = cur_loads.get(n, 0) + 1
                avg_ld = np.mean(list(cur_loads.values())) if cur_loads else 100

                scored = []
                for am in am_reg:
                    sc, rea = score_am(acct, am, cur_loads.get(am['name'], 0), avg_ld)
                    if sc is not None:
                        scored.append({'AM': am['name'], 'Role': am['role'], 'Score': sc,
                                       'Raisons': ' | '.join(rea[:4]), 'Charge': cur_loads.get(am['name'], 0)})
                scored.sort(key=lambda x: x['Score'], reverse=True)
                top5 = scored[:5]

                if top5:
                    st.dataframe(pd.DataFrame(top5), use_container_width=True, hide_index=True,
                                 column_config={
                                     'Score': st.column_config.NumberColumn(format="%.0f"),
                                     'Charge': st.column_config.NumberColumn(format="%d"),
                                 })

                    cd1, cd2, cd3 = st.columns([2, 2, 1])
                    with cd1:
                        choice = st.selectbox(
                            "Assigner à",
                            [f"#{i+1} — {c['AM']} (score {c['Score']:.0f})" for i, c in enumerate(top5)]
                            + ["Autre (manuel)"],
                            key=f"ch_{acct_id}",
                        )
                    with cd2:
                        manual_am = None
                        if choice == "Autre (manuel)":
                            # Filter AM names by matching segment
                            seg = 'Public' if row.get('Public_Prive') == 'PUBLIC' else 'Private'
                            seg_ams = [a['name'] for a in am_reg if a['segment'] == seg]
                            manual_am = st.selectbox("AM", seg_ams, key=f"man_{acct_id}")
                    with cd3:
                        if st.button("✅ Valider", key=f"val_{acct_id}"):
                            if choice == "Autre (manuel)" and manual_am:
                                new_owner = manual_am
                                method = 'manual'
                            else:
                                idx = int(choice.split('#')[1].split(' ')[0]) - 1
                                new_owner = top5[idx]['AM']
                                method = 'auto'
                            st.session_state.decisions[acct_id] = {
                                'new_owner': new_owner, 'method': method,
                                'old_owner': current_str,
                                'arr': row['ARR Dec 2025'],
                                'account_name': row['Account Name'],
                            }
                            st.rerun()
                else:
                    st.warning("Aucun AM compatible (segment mismatch)")

        # Bulk actions
        st.markdown("---")
        bk1, bk2 = st.columns(2)
        with bk1:
            if st.button("🚀 Accepter tous les #1 de cette page", type="primary", key="bulk_page"):
                for _, row in pg_df.iterrows():
                    aid = row['Account ID']
                    if aid in st.session_state.decisions:
                        continue
                    acct = {'pp': row.get('Public_Prive', ''), 'cls': row.get('Classification', 'SMB'),
                            'dom': row.get('Dom_Product', 'None'), 'sect': row.get('Secteur_activite', ''),
                            'arr': row.get('ARR Dec 2025', 0)}
                    cur_loads2 = {a['name']: 0 for a in am_reg}
                    for c in ['B&S', 'D&E', 'M&M']:
                        for n in cli_all[c].dropna():
                            cur_loads2[n] = cur_loads2.get(n, 0) + 1
                    avg2 = np.mean(list(cur_loads2.values())) if cur_loads2 else 100
                    best, best_sc = None, -999
                    for am in am_reg:
                        sc, _ = score_am(acct, am, cur_loads2.get(am['name'], 0), avg2)
                        if sc is not None and sc > best_sc:
                            best_sc = sc; best = am['name']
                    if best:
                        current_ams2 = []
                        for c in ['B&S', 'D&E', 'M&M']:
                            if pd.notna(row.get(c)): current_ams2.append(f"{c}: {row[c]}")
                        st.session_state.decisions[aid] = {
                            'new_owner': best, 'method': 'auto_bulk',
                            'old_owner': ' | '.join(current_ams2) if current_ams2 else 'Aucun',
                            'arr': row['ARR Dec 2025'], 'account_name': row['Account Name'],
                        }
                st.rerun()
        with bk2:
            if st.button("🗑️ Réinitialiser les décisions", key="reset_all"):
                st.session_state.decisions = {}
                st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    # SUB-TAB: SIMULATION
    # ─────────────────────────────────────────────────────────────────────
    with sub_simulation:
        st.subheader("📈 Simulation — Impact des réassignations")

        if not st.session_state.decisions:
            st.info("Aucune décision prise. Utilisez l'onglet Auto ou Workbench pour commencer.")
            st.stop()

        dec = st.session_state.decisions
        st.markdown(f"**{len(dec):,}** décisions prises")

        # KPIs
        sk1, sk2, sk3 = st.columns(3)
        sk1.metric("Comptes réassignés", f"{len(dec):,}")
        arr_moved = sum(d['arr'] for d in dec.values())
        sk2.metric("ARR déplacé", f"{arr_moved/1e6:.2f} M€")
        methods = pd.Series([d['method'] for d in dec.values()])
        auto_pct = methods.isin(['auto', 'auto_bulk']).sum() / len(methods) * 100
        sk3.metric("% Auto", f"{auto_pct:.0f}%")

        st.markdown("---")

        # Build before/after per AM
        am_reg_sim = build_am_registry()
        before = {}
        for am in am_reg_sim:
            before[am['name']] = {'accounts': 0, 'arr': 0}
        for c in ['B&S', 'D&E', 'M&M']:
            for _, row in cli_all.iterrows():
                if pd.notna(row.get(c)) and row[c] in before:
                    before[row[c]]['accounts'] += 1
                    before[row[c]]['arr'] += row['ARR Dec 2025']

        after = {n: {**d} for n, d in before.items()}
        for aid, d in dec.items():
            new = d['new_owner']
            if new in after:
                after[new]['accounts'] += 1
                after[new]['arr'] += d['arr']

        sim_rows = []
        for am in am_reg_sim:
            n = am['name']
            b, a = before.get(n, {'accounts': 0, 'arr': 0}), after.get(n, {'accounts': 0, 'arr': 0})
            sim_rows.append({
                'AM': n, 'Role': am['role'], 'Segment': am['segment'],
                'Avant': b['accounts'], 'Après': a['accounts'], 'Δ': a['accounts'] - b['accounts'],
                'ARR Avant': b['arr'], 'ARR Après': a['arr'], 'Δ ARR': a['arr'] - b['arr'],
            })
        sim_df = pd.DataFrame(sim_rows)

        # Chart: before vs after
        st.subheader("Charge par AM — Avant vs Après")
        seg_f = st.radio("Segment", ['Tous', 'Public', 'Private'], horizontal=True, key='sim_seg')
        if seg_f != 'Tous':
            sim_df = sim_df[sim_df['Segment'] == seg_f]

        ss = sim_df.sort_values('Après', ascending=False)
        fg = go.Figure()
        fg.add_trace(go.Bar(name='Avant', x=ss['AM'], y=ss['Avant'], marker_color='#B0BEC5', opacity=0.6))
        fg.add_trace(go.Bar(name='Après', x=ss['AM'], y=ss['Après'], marker_color='#2F5496'))
        fg.update_layout(barmode='overlay', height=450, xaxis_tickangle=45, legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fg, use_container_width=True)

        # Delta chart
        st.subheader("Variation (Δ Comptes)")
        dd = sim_df[sim_df['Δ'] != 0].sort_values('Δ')
        cols = ['#ef4444' if v < 0 else '#10b981' for v in dd['Δ']]
        fg2 = go.Figure(go.Bar(x=dd['AM'], y=dd['Δ'], marker_color=cols, text=dd['Δ'], textposition='outside'))
        fg2.update_layout(height=400, xaxis_tickangle=45)
        st.plotly_chart(fg2, use_container_width=True)

        # Table
        st.subheader("Détail par AM")
        st.dataframe(sim_df.sort_values('Δ', ascending=False), use_container_width=True, hide_index=True,
                     column_config={
                         'ARR Avant': st.column_config.NumberColumn(format="%.0f €"),
                         'ARR Après': st.column_config.NumberColumn(format="%.0f €"),
                         'Δ ARR': st.column_config.NumberColumn(format="%.0f €"),
                     })

        # Export decisions
        st.markdown("---")
        st.subheader("📥 Export des décisions")
        dec_rows = []
        for aid, d in dec.items():
            dec_rows.append({
                'Account ID': aid,
                'Account Name': d.get('account_name', ''),
                'Old Owner': d['old_owner'],
                'New Owner': d['new_owner'],
                'Method': d['method'],
                'ARR': d['arr'],
            })
        dec_df = pd.DataFrame(dec_rows).sort_values('ARR', ascending=False) if dec_rows else pd.DataFrame()

        if not dec_df.empty:
            st.dataframe(dec_df.head(50), use_container_width=True, hide_index=True,
                         column_config={'ARR': st.column_config.NumberColumn(format="%.0f €")})
            buf_dec = io.BytesIO()
            with pd.ExcelWriter(buf_dec, engine='openpyxl') as w:
                dec_df.to_excel(w, sheet_name='Decisions', index=False)
                sim_df.to_excel(w, sheet_name='Simulation', index=False)
            st.download_button("📊 Exporter décisions + simulation", data=buf_dec.getvalue(),
                               file_name="reassignation_decisions.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               type="primary")