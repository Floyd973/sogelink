11,869 clients"""
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

    /* ── Tabs — sélecteurs larges pour compatibilité toutes versions ── */
    button[data-baseweb="tab"] {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        padding: 10px 24px !important;
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #4a5568 !important;
        margin-right: 4px !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #4a5568 !important;
        color: #ffffff !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2F5496 !important;
        color: #ffffff !important;
        border-color: #2F5496 !important;
    }
    div[data-baseweb="tab-list"] {
        background-color: #1a202c !important;
        border-bottom: 2px solid #2F5496 !important;
        padding: 6px 6px 0 6px !important;
        border-radius: 8px 8px 0 0 !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #2F5496 !important;
        height: 3px !important;
    }
    div[data-baseweb="tab-border"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & ORG CHART
# =============================================================================
CAPACITY = {'Enterprise':4,'Key Account':4,'MM':3,'SMB':3,'T1':6,'T2':4,'T3':4,'T4':3}
MAX_ACT = 1410
CHURN = 0.03
NRR = 1.20

@st.cache_data
def parse_org():
    """Load new org from org_cible.xlsx. Falls back to hardcoded if file not found."""
    try:
        org = pd.read_excel('./org_cible.xlsx')
        org.columns = ['AM_Name', 'Role', 'Segment']
        org['AM_Name'] = org['AM_Name'].str.strip()
        org['Role'] = org['Role'].str.strip()
        org['Segment'] = org['Segment'].str.strip()
    except Exception:
        # Fallback hardcoded
        import io as _io
        _raw = """Thomas CAUWE;Private - SMB D&E Manager;Private
Beatrice DEMONT;Private - SMB D&E Contractors Account Manager;Private
Cecile RIAHI;Private - SMB D&E Contractors Account Manager;Private
Patricia BIZIEN;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Karine ROUE;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Aurelie SAVIDAN;Private - SMB D&E Surveyors & Design Offices Account Manager;Private
Virginie VESCHI;Private - SMB CBYD Manager;Private
Arnaud CERESA;Private - SMB CBYD Account Manager;Private
Albin HUGUES;Private - SMB CBYD Account Manager;Private
Amandine LANNIER;Private - SMB CBYD Account Manager;Private
Alain BORNET;Private - MM & Enterprise Manager;Private
Robin BURRUS;Private - MM & Enterprise Account Manager;Private
Mickael Iochem;Private - MM & Enterprise Account Manager;Private
Christine EVAIN;Private - Renewals Manager;Private
Quentin DECK;Public - ex M&M - Manager;Public
Simon TONY;Public - ex M&M - Account Manager;Public
Morgane CURIAL;Public - ex M&M - Account Manager;Public
Pierre-Antoine MARQUAND;Public - ex M&M - Account Manager;Public
Bryan TUGLER;Public - ex M&M - Account Manager;Public
Anissa EL BAHRI;Public - ex M&M - Account Manager;Public
Alexandre PENTECOUTEAU;Public - ex M&M - Account Manager;Public
Marion ANCIAN;Public - ex-CBYD - Manager;Public
Amandine BORJON-BLIND;Public - ex-CBYD - Account Manager;Public
Amandine DA SILVA;Public - ex-CBYD - Account Manager;Public
Mounira EL HAFI;Public - ex-CBYD - Account Manager;Public
Alexandre JULIA;Public - ex-CBYD - Account Manager;Public
Florent TREHET;Public - ex-DIAG - Team Lead;Public
Arnaud BRIDAY;Public - ex-DIAG - Account Manager;Public
Raphael CATHERIN;Public - ex-DIAG - Account Manager;Public
Baptiste Pasquier guillard;Public - ex-DIAG - Account Manager;Public
Aymerick Dechamps-cottin;Public - ex-DIAG - Account Manager;Public
Gildas KERNEIS;Public - Key Account - Account Manager;Public
Tiffany KAAS CHEVALIER;Public - Key Account - Account Manager;Public
Kelian HOULMIERE;Public - Key Account - Subsidiary Account Manager;Public
Aurelien Tabard;Public - Key Account - Subsidiary Account Manager;Public
Mirabelle RAMOND;Public - Renewals - Team Manager;Public
Nadia Guery;Public - Renewals Manager;Public"""
        rows = []
        for line in _raw.strip().split('\n'):
            p = line.split(';')
            if len(p) >= 3:
                rows.append({'AM_Name': p[0].strip(), 'Role': p[1].strip(), 'Segment': p[2].strip()})
        org = pd.DataFrame(rows)

    org['Is_Manager'] = (org['Role'].str.contains('Manager') &
                         ~org['Role'].str.contains('Account Manager') &
                         ~org['Role'].str.contains('Renewal Manager') &
                         ~org['Role'].str.contains('Team Lead'))
    org['Is_Renewal'] = org['Role'].str.contains('Renewal')
    return org


import unicodedata, re as _re

def _norm_name(s):
    """Normalize accents + lowercase for fuzzy matching (ops owner lookup)."""
    s = str(s).strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = _re.sub(r'\s+', ' ', s)
    return s

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

@st.cache_data
def load_ops():
    """Load ops ouvertes - returns (grp per account+owner, total per account)."""
    try:
        ops = pd.read_html('./ops_ouvertes.xls', encoding='latin1')[0]
        ops.columns = ['Owner','Opp_ID','Account_Name','Account_ID','Opp_Name',
                       'Stage','FY','Currency','Amount','Probability','Age','Close_Date','Create_Date']
        grp = ops.groupby(['Account_ID','Owner']).size().reset_index(name='n_ops')
        total = ops.groupby('Account_ID').size().reset_index(name='total_ops')
        return grp, total
    except Exception:
        return pd.DataFrame(columns=['Account_ID','Owner','n_ops']), pd.DataFrame(columns=['Account_ID','total_ops'])

ops_by_acct, ops_total = load_ops()

# =============================================================================
# SIDEBAR FILTERS
# =============================================================================
st.sidebar.title("📊 Sogelink Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Metrics", "🔄 Réassignation"], label_visibility="collapsed")
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
# REASSIGNMENT ENGINE  (v3 — règles métier complètes)
# =============================================================================

# ---------------------------------------------------------------------------
# Old-AM → New-AM mapping  (Règle 1 : conservation si possible)
# ---------------------------------------------------------------------------
# Manual mapping: old name (as it appears in base_sogelink) → new canonical name
# Only AMs who are Account Managers in the new org are mapped.
# AMs who became Renewal / Manager / left are mapped to None.
_OLD_NAME_MAP = {
    # old name (lowercase-ish, as in base)    : new canonical name in org_cible (or None if no longer AM)
    'Alain Bornet':                None,            # Manager in new org
    'Albin Hugues':                'Albin HUGUES',
    'Alexandre Julia':             'Alexandre JULIA',
    'Alexandre Pentecouteau':      'Alexandre PENTECOUTEAU',
    'Amandine Borjon-blind':       'Amandine BORJON-BLIND',
    'Amandine Da Silva':           'Amandine DA SILVA',
    'Amandine Lannier':            'Amandine LANNIER',
    'Anissa El bahri':             'Anissa EL BAHRI',
    'Arnaud Briday':               'Arnaud BRIDAY',
    'Arnaud Ceresa':               'Arnaud CERESA',
    'Aurelie Savidan':             'Aurelie SAVIDAN',
    'Aurélien Tabard':             'Aurélien Tabard',
    'Aymerick Dechamps-cottin':    'Aymerick Dechamps-cottin',
    'Baptiste Pasquier guillard':  'Baptiste Pasquier guillard',
    'Beatrice Demont':             'Beatrice DEMONT',
    'Bryan Tugler':                'Bryan TUGLER',
    'Cecile Cherhal':              'Cecile CHERHAL',
    'Cecile Riahi':                'Cecile RIAHI',
    'Farès Hamlat':                'Farès Hamlat',
    'Florence Barjon':             'Florence BARJON',
    'Karine Roue':                 'Karine ROUE',
    'Mickaël Iochem':              'Mickaël Iochem',
    'Morgane Curial':              'Morgane CURIAL',
    'Mounira El hafi':             'Mounira EL HAFI',
    'Nadia Guery':                 None,            # Renewal in new org → not an AM anymore
    'Olivier Kennibol':            None,            # not in new org
    'Patricia Bizien':             'Patricia BIZIEN',
    'Pierre-Antoine Marquand':     'Pierre-Antoine MARQUAND',
    'Pierre-Louis Asso':           'Pierre-Louis ASSO',
    'Quentin Deck':                'Quentin DECK',
    'Quentin Trojani':             'Quentin TROJANI',
    'Raphael Catherin':            'Raphael CATHERIN',
}


def build_am_registry():
    """Build AM list from new org (org_cible), excluding Managers and Renewal."""
    ams = []
    for _, r in org_df.iterrows():
        if r['Is_Manager'] or r['Is_Renewal']:
            continue
        role = r['Role']
        ams.append({
            'name':        r['AM_Name'],
            'role':        role,
            'segment':     r['Segment'],       # 'Public' or 'Private'
            'ka':          'Key Account' in role and 'Subsidiary' not in role,
            'subsidiary':  'Subsidiary' in role,
            'mm_ent':      'MM & Enterprise' in role,
            'cbyd':        'CBYD' in role,
            'de':          'D&E' in role,
            'contractors': 'Contractor' in role,
            'surveyors':   'Surveyor' in role or 'Design Office' in role,
            'diag':        'DIAG' in role,
            'mm_pub':      'ex M&M' in role,
        })
    return ams

# Pre-build registry as a name→dict lookup used during continuity check
@st.cache_data
def _am_lookup_by_name():
    return {a['name']: a for a in build_am_registry()}


def _expertise_tag(am):
    """Canonical expertise bucket for a new-org AM."""
    if am['ka'] or am['subsidiary']: return 'KA'
    if am['mm_ent']:                 return 'MM_ENT'
    if am['diag']:                   return 'DIAG'
    if am['de'] or am['surveyors'] or am['contractors']: return 'DE'
    if am['cbyd']:                   return 'CBYD'
    if am['mm_pub']:                 return 'MM_PUB'
    return 'OTHER'


def _slot_expertise(col):
    """
    Expertise required by a slot, inferred from the old-org column.
    B&S = CBYD  |  D&E = DE  |  M&M = MM_PUB
    (KA accounts get a KA/MM_ENT preference via classification scoring)
    """
    if col == 'D&E': return 'DE'
    if col == 'M&M': return 'MM_PUB'
    return 'CBYD'


def score_am_auto(acct, am, am_load, avg_load, ops_boost=0):
    """
    AUTO-reassignment scoring.
    Rules applied strictly (Règles 2-6 + ops bonus R7 aussi en auto).
    Returns (score, reasons) or (None, []) if hard-filtered out.
    """
    # R2 — Strict segment filter
    seg = 'Public' if acct['pp'] == 'PUBLIC' else 'Private'
    if am['segment'] != seg:
        return None, []

    s, reasons = 0, []
    cls = acct['cls']

    # R3/R5 — Expertise match (primary lever — must stay on speciality)
    req_exp = acct.get('required_expertise', '')
    if req_exp:
        am_exp = _expertise_tag(am)
        if am_exp == req_exp:
            s += 50; reasons.append(f'✓Exp:{req_exp}')
        else:
            s -= 40; reasons.append(f'✗Exp({am_exp}≠{req_exp})')

    # Classification fit
    if cls in ('Enterprise', 'Key Account'):
        if am['ka']:       s += 40; reasons.append('KA')
        elif am['mm_ent']: s += 30; reasons.append('MM/Ent')
        elif am['mm_pub']: s += 15; reasons.append('M&M Pub')
        else:              s -= 15
    elif cls == 'MM':
        if am['mm_ent']:   s += 30; reasons.append('MM/Ent')
        elif am['mm_pub']: s += 20; reasons.append('M&M Pub')
        elif am['ka']:     s -= 10
    else:
        if not am['ka'] and not am['subsidiary']:
            s += 10; reasons.append('SMB/Tx ok')
        elif am['ka']:
            s -= 15

    # Domain bonus (when no strict expertise constraint, e.g. accounts without AM)
    if not req_exp:
        dom = acct.get('dom', 'None')
        if dom == 'DICT'   and am['cbyd']:                  s += 25; reasons.append('CBYD')
        elif dom in ('Infra','Topo','Elec','Geo') and (am['de'] or am['surveyors']): s += 25; reasons.append('D&E')
        elif dom == 'Diag' and am['diag']:                  s += 25; reasons.append('DIAG')
        elif dom == 'Coordin' and (am['mm_pub'] or am['cbyd']): s += 15; reasons.append('Coordin')

    # Sector fit
    sect = str(acct.get('sect', ''))
    if 'Contractor' in sect and am['contractors']:                         s += 15; reasons.append('Ind:Contr')
    elif ('Surveyor' in sect or 'Design' in sect) and (am['surveyors'] or am['de']): s += 15; reasons.append('Ind:Surv/DE')
    elif 'Local auth' in sect and (am['mm_pub'] or am['cbyd'] or am['diag']): s += 10; reasons.append('Ind:Public')

    # R6 — Load balancing (soft, flag only — never blocks)
    if avg_load > 0:
        if am_load < avg_load:           s += 5;  reasons.append('↓charge')
        elif am_load > avg_load * 1.3:   s -= 5;  reasons.append('⚠surcharge')

    # ARR large accounts
    if acct.get('arr', 0) > 50000 and (am['mm_ent'] or am['ka']):
        s += 10; reasons.append('High ARR')

    # R7 — Ops ouvertes sur le compte
    if ops_boost > 0:
        bonus = min(ops_boost * 3, 20)
        s += bonus; reasons.append(f'Ops:{ops_boost}')

    return s, reasons


def score_am_manual(acct, am, am_load, avg_load, ops_boost=0,
                    am_arr=0, am_pot=0, am_reste=0, am_ca=0, n_accounts=0):
    """
    MANUAL workbench scoring.
    Adds ops bonus (R7) and portfolio balance indicators (R9).
    Returns (score, reasons, balance_info).
    """
    sc, rea = score_am_auto(acct, am, am_load, avg_load)
    if sc is None:
        return None, [], {}

    # R7 — Ops ouvertes sur le compte (manual only)
    if ops_boost > 0:
        bonus = min(ops_boost * 5, 25)
        sc += bonus; rea.append(f'Ops:{ops_boost}')

    # R9 — Portfolio balance info (displayed, not used in score to avoid gaming)
    balance = {
        'Comptes': n_accounts,
        'ARR':     am_arr,
        'Potentiel': am_pot,
        'Reste':   am_reste,
        'CA':      am_ca,
    }

    return sc, rea, balance


@st.cache_data
def build_portfolio_stats(_df_json, _auto_results_json):
    """
    Compute per-AM portfolio stats from the auto-reassignment results.
    Used in the manual workbench to display balance indicators (R9).
    """
    dfa = pd.read_json(io.StringIO(_df_json))
    res = pd.read_json(io.StringIO(_auto_results_json))

    stats = {}  # am_name → {n, arr, pot, reste, ca}
    for col in ['New_BS', 'New_DE', 'New_MM']:
        for _, row in res.iterrows():
            am = row.get(col, '')
            if not am:
                continue
            acct_row = dfa[dfa['Account ID'] == row['Account ID']]
            if acct_row.empty:
                continue
            r = acct_row.iloc[0]
            if am not in stats:
                stats[am] = {'n': 0, 'arr': 0, 'pot': 0, 'reste': 0, 'ca': 0}
            stats[am]['n']     += 1
            stats[am]['arr']   += float(r.get('ARR Dec 2025', 0) or 0)
            stats[am]['pot']   += float(r.get('Potentiel', 0) or 0)
            stats[am]['reste'] += float(r.get('Reste_a_depenser', 0) or 0)
            stats[am]['ca']    += float(r.get('Chiffre_affaires_annuel', 0) or 0)
    return stats


@st.cache_data
def run_auto_reassign(_df_json, _ops_json):
    """
    Auto-reassignment — Règles 1 à 6 + 8 (strictement, sans ops bonus).

    Pour chaque compte client :
    R1 — On cherche d'abord à conserver les AM existants s'ils sont dans la
         nouvelle org AVEC le bon segment.
    R2 — Filtre dur Public/Privé — aucune exception.
    R3/R5 — Expertise du slot (B&S→CBYD, D&E→DE, M&M→MM_PUB) conservée.
    R4/R6 — Surcharge acceptée et flaggée, jamais bloquante.
    R8 — Pas de bonus ops ici (réservé au manuel).
    """
    dfa    = pd.read_json(io.StringIO(_df_json))
    ops_df = pd.read_json(io.StringIO(_ops_json)) if _ops_json else pd.DataFrame()

    am_reg  = build_am_registry()
    am_lkup = {a['name']: a for a in am_reg}
    am_load = {a['name']: 0 for a in am_reg}

    cli = dfa[dfa['Status'] == 'Client'].copy()
    cli = cli.sort_values('ARR Dec 2025', ascending=False)

    # Build ops lookup: {account_id: {owner_norm: n_ops}}
    ops_lookup = {}
    if not ops_df.empty:
        for _, orow in ops_df.iterrows():
            aid   = orow['Account_ID']
            owner = _norm_name(str(orow['Owner']))
            ops_lookup.setdefault(aid, {})[owner] = ops_lookup.get(aid, {}).get(owner, 0) + int(orow['n_ops'])

    results = []

    for _, row in cli.iterrows():
        acct_id = row['Account ID']
        pp      = str(row.get('Public_Prive', ''))
        cls     = str(row.get('Classification', 'SMB'))
        dom     = str(row.get('Dom_Product', 'None'))
        sect    = str(row.get('Secteur_activite', ''))
        arr_val = float(row.get('ARR Dec 2025', 0) or 0)
        acct_seg = 'Public' if pp == 'PUBLIC' else 'Private'

        # ── Determine slots ──────────────────────────────────────────────
        old_slot_map = {}  # col → old AM name (may be None if empty)
        for col in ['B&S', 'D&E', 'M&M']:
            val = row.get(col)
            if pd.notna(val) and str(val).strip():
                old_slot_map[col] = str(val).strip()

        slots = list(old_slot_map.keys()) if old_slot_map else ['B&S']

        # Dynamic avg load
        loads_vals = list(am_load.values())
        avg_load = np.mean(loads_vals) if any(v > 0 for v in loads_vals) else 100

        acct_ops = ops_lookup.get(acct_id, {})
        new_slots  = {}
        slot_notes = {}
        continuity_flags = {}

        for col in slots:
            exp_needed = _slot_expertise(col)
            already    = set(new_slots.values())
            old_am     = old_slot_map.get(col)

            # ── R1 : try to keep the old AM ──────────────────────────────
            kept = False
            if old_am:
                new_name = _OLD_NAME_MAP.get(old_am)  # None if not in new org or left
                if new_name and new_name in am_lkup:
                    am_info = am_lkup[new_name]
                    # R2 check: same segment?
                    if am_info['segment'] == acct_seg and new_name not in already:
                        new_slots[col]          = new_name
                        slot_notes[col]         = f'✓Conservé: {new_name}'
                        continuity_flags[col]   = 'kept'
                        am_load[new_name]        = am_load.get(new_name, 0) + 1
                        kept = True
                    # else: AM changed segment → must replace (falls through to scoring)

            # ── Score for replacement / new assignment ───────────────────
            if not kept:
                acct_ctx = {
                    'pp': pp, 'cls': cls, 'dom': dom, 'sect': sect, 'arr': arr_val,
                    'required_expertise': exp_needed,
                }
                scored = []
                for am in am_reg:
                    if am['name'] in already:
                        continue
                    ops_boost = acct_ops.get(_norm_name(am['name']), 0)
                    sc, rea = score_am_auto(acct_ctx, am, am_load.get(am['name'], 0), avg_load, ops_boost)
                    if sc is not None:
                        scored.append({'am': am['name'], 'role': am['role'],
                                       'score': sc, 'reasons': ' | '.join(rea[:5])})
                scored.sort(key=lambda x: x['score'], reverse=True)

                if scored:
                    best = scored[0]
                    new_slots[col]         = best['am']
                    reason_prefix = '↺Remplacé' if old_am else '★Nouveau'
                    slot_notes[col]        = f'{reason_prefix}: {best["am"]} (exp:{exp_needed}, sc:{best["score"]:.0f})'
                    continuity_flags[col]  = 'replaced' if old_am else 'new'
                    am_load[best['am']]    = am_load.get(best['am'], 0) + 1
                else:
                    new_slots[col]         = ''
                    slot_notes[col]        = f'⚠️ Aucun AM {exp_needed} {acct_seg}'
                    continuity_flags[col]  = 'missing'

        # ── Overload flag ────────────────────────────────────────────────
        avg_now    = np.mean(list(am_load.values())) or 1
        overloaded = [n for n in new_slots.values()
                      if n and am_load.get(n, 0) > avg_now * 1.5]

        n_kept     = sum(1 for v in continuity_flags.values() if v == 'kept')
        n_replaced = sum(1 for v in continuity_flags.values() if v == 'replaced')

        results.append({
            'Account ID':     acct_id,
            'Account Name':   row['Account Name'],
            'Classification': cls,
            'Public_Prive':   pp,
            'Team':           str(row.get('FR_Sogelink_Team', '')),
            'Secteur':        sect,
            'ARR':            arr_val,
            'Dom_Product':    dom,
            'Old_BS':         str(old_slot_map.get('B&S', '')),
            'Old_DE':         str(old_slot_map.get('D&E', '')),
            'Old_MM':         str(old_slot_map.get('M&M', '')),
            'New_BS':         new_slots.get('B&S', ''),
            'New_DE':         new_slots.get('D&E', ''),
            'New_MM':         new_slots.get('M&M', ''),
            'AM_Conservés':   n_kept,
            'AM_Remplacés':   n_replaced,
            'Notes':          ' | '.join(v for v in slot_notes.values() if v),
            'Overload_Flag':  ', '.join(overloaded) if overloaded else '',
        })

    return pd.DataFrame(results), am_load

# =============================================================================
# TABS
# =============================================================================


# =============================================================================
# TAB 1: METRICS
# =============================================================================
if page == "📊 Metrics":
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
if page == "🔄 Réassignation":
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
        L'algorithme applique les règles métier dans l'ordre de priorité suivant :
        1. **R1 — Continuité** : si l'ancien AM existe dans la nouvelle org avec le bon segment → conservé
        2. **R2 — Segment strict** : Public → AM Public, Privé → AM Privé (aucune exception)
        3. **R3/R5 — Expertise produit** : remplacement par même expertise (B&S→CBYD, D&E→D&E, M&M→M&M Pub)
        4. **R4/R6 — Surcharge acceptée** : flaggée ⚠️ si > 150% moyenne, jamais bloquante
        5. **R7 — Bonus ops** : AM avec opportunités ouvertes sur le compte favorisé (+3 pts/op, max +20)
        """)

        col_run, col_info = st.columns([1, 2])
        with col_run:
            run_auto = st.button("🚀 Lancer", type="primary", key="run_auto")
        with col_info:
            cli_total = df_full[df_full['Status'] == 'Client']
            st.info(f"Traitement de **{len(cli_total):,}** clients")

        if run_auto:
            with st.spinner("Calcul en cours..."):
                ops_json = ops_by_acct.to_json() if not ops_by_acct.empty else ''
                result_df, new_loads = run_auto_reassign(df_full.to_json(), ops_json)
            st.session_state.auto_results = result_df
            st.session_state.auto_loads = new_loads
            st.success(f"✅ {len(result_df):,} comptes traités !")

        # Display results
        if 'auto_results' in st.session_state and st.session_state.auto_results is not None:
            res = st.session_state.auto_results

            st.markdown("---")
            st.subheader("Résultats de la réassignation automatique")

            # KPIs
            rc1, rc2, rc3, rc4, rc5 = st.columns(5)
            rc1.metric("Comptes traités", f"{len(res):,}")
            rc2.metric("ARR couvert", f"{res['ARR'].sum()/1e6:.1f} M€")
            n_kept_total = res['AM_Conservés'].sum()
            n_replaced_total = res['AM_Remplacés'].sum()
            rc3.metric("✓ AM conservés", f"{n_kept_total:,}")
            rc4.metric("↺ AM remplacés", f"{n_replaced_total:,}")
            n_overload = res[res['Overload_Flag'] != '']['Account ID'].nunique()
            rc5.metric("⚠️ Comptes surchargés", f"{n_overload:,}")

            # Load distribution
            st.markdown("**Charge nouvelle par AM :**")
            load_rows = []
            for am_name, cnt in sorted(st.session_state.auto_loads.items(), key=lambda x: -x[1]):
                if cnt > 0:
                    am_info = next((a for a in build_am_registry() if a['name'] == am_name), {})
                    avg_ = np.mean(list(st.session_state.auto_loads.values()))
                    flag = '⚠️ SURCHARGÉ' if cnt > avg_ * 1.5 else ('↑ élevé' if cnt > avg_ * 1.3 else '')
                    load_rows.append({'AM': am_name, 'Role': am_info.get('role',''), 
                                      'Segment': am_info.get('segment',''),
                                      'Comptes': cnt, 'Flag': flag})
            load_df = pd.DataFrame(load_rows)
            avg_load_val = load_df['Comptes'].mean() if not load_df.empty else 0

            cL_ld, cR_ld = st.columns([2, 3])
            with cL_ld:
                st.dataframe(load_df, use_container_width=True, hide_index=True,
                             column_config={
                                 'Comptes': st.column_config.NumberColumn(format="%d"),
                             })
            with cR_ld:
                if not load_df.empty:
                    colors = ['#ef4444' if '⚠️' in str(r['Flag']) else '#f59e0b' if '↑' in str(r['Flag']) else '#2F5496'
                              for _, r in load_df.iterrows()]
                    fig_ld = go.Figure(go.Bar(
                        x=load_df['AM'], y=load_df['Comptes'], marker_color=colors,
                        text=load_df['Flag'], textposition='outside',
                    ))
                    fig_ld.add_hline(y=avg_load_val, line_dash='dash', line_color='#94a3b8',
                                     annotation_text=f'Moy: {avg_load_val:.0f}')
                    fig_ld.update_layout(height=420, xaxis_tickangle=45)
                    st.plotly_chart(fig_ld, use_container_width=True)

            # Results table with filters
            st.markdown("---")
            st.markdown("**Détail par compte :**")

            fcl1, fcl2, fcl3, fcl4 = st.columns(4)
            with fcl1:
                f_team = st.multiselect("Team", res['Team'].dropna().unique().tolist(),
                                        default=res['Team'].dropna().unique().tolist(), key='auto_f_team')
            with fcl2:
                f_cls = st.multiselect("Classification", res['Classification'].dropna().unique().tolist(),
                                       default=res['Classification'].dropna().unique().tolist(), key='auto_f_cls')
            with fcl3:
                f_overload = st.checkbox("⚠️ Surchargés seulement", key='auto_overload')
            with fcl4:
                f_sort = st.selectbox("Trier par", ['ARR ↓', 'Account Name'], key='auto_sort')

            res_filt = res[(res['Team'].isin(f_team)) & (res['Classification'].isin(f_cls))]
            if f_overload:
                res_filt = res_filt[res_filt['Overload_Flag'] != '']
            if f_sort == 'ARR ↓':
                res_filt = res_filt.sort_values('ARR', ascending=False)
            else:
                res_filt = res_filt.sort_values('Account Name')

            display_cols = ['Account Name', 'Classification', 'Public_Prive', 'Dom_Product',
                            'New_BS', 'New_DE', 'New_MM', 'ARR', 'Notes', 'Overload_Flag']
            st.dataframe(res_filt[display_cols].head(200), use_container_width=True, hide_index=True,
                         column_config={
                             'Account Name':  'Compte',
                             'Classification':'Class.',
                             'Public_Prive':  'Pub/Priv',
                             'Dom_Product':   'Produit dom.',
                             'New_BS':        'B&S (cible)',
                             'New_DE':        'D&E (cible)',
                             'New_MM':        'M&M (cible)',
                             'ARR':           st.column_config.NumberColumn('ARR', format="%.0f €"),
                             'Notes':         'Notes',
                             'Overload_Flag': '⚠️ Surcharge',
                         })

            # Export
            st.markdown("---")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("✅ Accepter toutes les réassignations auto", type="primary", key="accept_all"):
                    for _, row in res.iterrows():
                        for slot, col_key in [('New_BS','B&S'), ('New_DE','D&E'), ('New_MM','M&M')]:
                            new_am = row.get(slot, '')
                            if new_am:
                                aid = f"{row['Account ID']}_{col_key}"
                                st.session_state.decisions[aid] = {
                                    'new_owner': new_am, 'method': 'auto',
                                    'old_owner': str(row.get(col_key.replace('New_',''), '')),
                                    'arr': row['ARR'], 'account_name': row['Account Name'],
                                    'slot': col_key,
                                }
                    st.success(f"✅ Décisions enregistrées")
                    st.rerun()
            with ca2:
                buf_auto = io.BytesIO()
                with pd.ExcelWriter(buf_auto, engine='openpyxl') as w:
                    res.to_excel(w, sheet_name='Reassignation_Auto', index=False)
                    load_df.to_excel(w, sheet_name='Charge_AM', index=False)
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
            'Tous les clients',
            'Clients sans AM seulement',
        ], horizontal=True, key='wb_scope')

        if scope == 'Clients sans AM seulement':
            wb_base = no_am.copy()
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

        am_reg = build_am_registry()

        # Load is computed on the NEW org after auto-reassign if available,
        # otherwise initialise to zero (workbench is for manual decisions).
        if 'auto_loads' in st.session_state:
            cur_loads = dict(st.session_state.auto_loads)
        else:
            cur_loads = {a['name']: 0 for a in am_reg}
        avg_ld = np.mean(list(cur_loads.values())) if any(v > 0 for v in cur_loads.values()) else 100

        # Display account cards
        for _, row in pg_df.iterrows():
            acct_id = row['Account ID']
            decided = any(k.startswith(acct_id) for k in st.session_state.decisions)
            icon = "✅" if decided else "⚠️"

            # Current AM slots
            existing_slots = {}
            for c in ['B&S', 'D&E', 'M&M']:
                if pd.notna(row.get(c)):
                    existing_slots[c] = row[c]

            slot_summary = ' | '.join(f"{c}: {v}" for c, v in existing_slots.items()) if existing_slots else 'Aucun'

            with st.expander(
                f"{icon} **{row['Account Name']}** — {row['ARR Dec 2025']:,.0f}€ | "
                f"{row.get('Classification', '')} | {row.get('Public_Prive','')} | {row.get('Secteur_activite', '')}",
                expanded=not decided
            ):
                ci1, ci2, ci3, ci4 = st.columns(4)
                ci1.markdown(f"**AM actuels:** {slot_summary}")
                ci2.markdown(f"**Produit dom.:** {row.get('Dom_Product', '?')}")
                ci3.markdown(f"**Ops ouvertes:** {ops_total[ops_total['Account_ID']==acct_id]['total_ops'].sum():.0f}")
                ci4.markdown(f"**Groupe:** {row.get('Ultimate_Parent', '—')}")

                pp   = row.get('Public_Prive', '')
                cls  = row.get('Classification', 'SMB')
                dom  = row.get('Dom_Product', 'None')
                sect = row.get('Secteur_activite', '')
                arr_v = row.get('ARR Dec 2025', 0)

                # Ops for this account (R7)
                acct_ops = ops_by_acct[ops_by_acct['Account_ID'] == acct_id] if not ops_by_acct.empty else pd.DataFrame()
                ops_dict = {_norm_name(r['Owner']): int(r['n_ops']) for _, r in acct_ops.iterrows()} if not acct_ops.empty else {}

                # Portfolio stats for balance display (R9)
                port_stats = {}
                if 'auto_results' in st.session_state and st.session_state.auto_results is not None:
                    port_stats = build_portfolio_stats(
                        df_full.to_json(),
                        st.session_state.auto_results.to_json()
                    )

                # Per slot
                slots_to_show = list(existing_slots.keys()) if existing_slots else ['B&S']
                for col in slots_to_show:
                    old_am = existing_slots.get(col, None)
                    # Show auto-reassign result for this slot if available
                    auto_reco = ''
                    if 'auto_results' in st.session_state and st.session_state.auto_results is not None:
                        auto_row = st.session_state.auto_results[
                            st.session_state.auto_results['Account ID'] == acct_id
                        ]
                        if not auto_row.empty:
                            col_map = {'B&S': 'New_BS', 'D&E': 'New_DE', 'M&M': 'New_MM'}
                            auto_reco = auto_row.iloc[0].get(col_map.get(col, ''), '')

                    st.markdown(
                        f"**Slot {col}** — ancienne org: `{old_am or 'non assigné'}` "
                        f"| auto-reco: `{auto_reco or '—'}`"
                    )

                    exp_needed = _slot_expertise(col)
                    acct_ctx = {
                        'pp': pp, 'cls': cls, 'dom': dom, 'sect': sect, 'arr': arr_v,
                        'required_expertise': exp_needed,
                    }

                    # Score all AMs with ops bonus + portfolio balance (R7, R9)
                    scored = []
                    for am in am_reg:
                        ops_boost  = ops_dict.get(_norm_name(am['name']), 0)
                        ps         = port_stats.get(am['name'], {})
                        sc, rea, bal = score_am_manual(
                            acct_ctx, am,
                            cur_loads.get(am['name'], 0), avg_ld,
                            ops_boost=ops_boost,
                            am_arr=ps.get('arr', 0),
                            am_pot=ps.get('pot', 0),
                            am_reste=ps.get('reste', 0),
                            am_ca=ps.get('ca', 0),
                            n_accounts=ps.get('n', 0),
                        )
                        if sc is not None:
                            scored.append({
                                'AM':           am['name'],
                                'Rôle':         am['role'],
                                'Score':        sc,
                                'Raisons':      ' | '.join(rea[:5]),
                                'Charge':       cur_loads.get(am['name'], 0),
                                'Ops/compte':   ops_boost,
                                # R9 portfolio balance indicators
                                'Port. Comptes': bal.get('Comptes', 0),
                                'Port. ARR':    bal.get('ARR', 0),
                                'Port. Potentiel': bal.get('Potentiel', 0),
                                'Port. Reste':  bal.get('Reste', 0),
                                'Port. CA':     bal.get('CA', 0),
                            })
                    scored.sort(key=lambda x: x['Score'], reverse=True)
                    top5 = scored[:5]

                    if top5:
                        st.dataframe(pd.DataFrame(top5), use_container_width=True, hide_index=True,
                                     column_config={
                                         'Score':    st.column_config.NumberColumn(format="%.0f"),
                                         'Charge':   st.column_config.NumberColumn(format="%d"),
                                         'Ops/compte': st.column_config.NumberColumn(format="%d"),
                                         'Port. Comptes': st.column_config.NumberColumn('📋 Comptes', format="%d"),
                                         'Port. ARR': st.column_config.NumberColumn('💰 ARR', format="%.0f €"),
                                         'Port. Potentiel': st.column_config.NumberColumn('📈 Potentiel', format="%.0f €"),
                                         'Port. Reste': st.column_config.NumberColumn('🎯 Reste', format="%.0f €"),
                                         'Port. CA': st.column_config.NumberColumn('🏢 CA clients', format="%.0f €"),
                                     })

                        slot_key = f"{acct_id}_{col}"
                        cd1, cd2, cd3 = st.columns([2, 2, 1])
                        with cd1:
                            choice = st.selectbox(
                                f"Assigner slot {col}",
                                [f"#{i+1} — {c['AM']} (sc {c['Score']:.0f})" for i, c in enumerate(top5)]
                                + ["Autre (manuel)"],
                                key=f"ch_{slot_key}",
                            )
                        with cd2:
                            manual_am = None
                            if choice == "Autre (manuel)":
                                seg = 'Public' if pp == 'PUBLIC' else 'Private'
                                seg_ams = [a['name'] for a in am_reg if a['segment'] == seg]
                                manual_am = st.selectbox("AM", seg_ams, key=f"man_{slot_key}")
                        with cd3:
                            if st.button("✅ Valider", key=f"val_{slot_key}"):
                                if choice == "Autre (manuel)" and manual_am:
                                    new_owner = manual_am
                                    method = 'manual'
                                else:
                                    idx = int(choice.split('#')[1].split(' ')[0]) - 1
                                    new_owner = top5[idx]['AM']
                                    method = 'workbench'
                                st.session_state.decisions[slot_key] = {
                                    'new_owner': new_owner, 'method': method,
                                    'old_owner': old_am or 'Aucun',
                                    'arr': arr_v, 'account_name': row['Account Name'],
                                    'slot': col,
                                }
                                st.rerun()
                    else:
                        st.warning(f"Aucun AM compatible pour le slot {col} (segment {pp})")

        # Bulk actions
        st.markdown("---")
        bk1, bk2 = st.columns(2)
        with bk1:
            if st.button("🚀 Accepter tous les #1 de cette page", type="primary", key="bulk_page"):
                for _, row in pg_df.iterrows():
                    acct_id = row['Account ID']
                    pp   = row.get('Public_Prive', '')
                    cls  = row.get('Classification', 'SMB')
                    dom  = row.get('Dom_Product', 'None')
                    sect = row.get('Secteur_activite', '')
                    arr_v = row.get('ARR Dec 2025', 0)
                    existing = {c: row[c] for c in ['B&S','D&E','M&M'] if pd.notna(row.get(c))}
                    slots = list(existing.keys()) if existing else ['B&S']
                    for col in slots:
                        slot_key = f"{acct_id}_{col}"
                        if slot_key in st.session_state.decisions:
                            continue
                        exp = _slot_expertise(col)
                        acct_ctx = {'pp': pp, 'cls': cls, 'dom': dom, 'sect': sect, 'arr': arr_v, 'required_expertise': exp}
                        scored2 = []
                        for am in am_reg:
                            sc, _ = score_am_auto(acct_ctx, am, cur_loads.get(am['name'], 0), avg_ld)
                            if sc is not None:
                                scored2.append({'am': am['name'], 'score': sc})
                        scored2.sort(key=lambda x: x['score'], reverse=True)
                        if scored2:
                            best = scored2[0]
                            st.session_state.decisions[slot_key] = {
                                'new_owner': best['am'], 'method': 'auto_bulk',
                                'old_owner': existing.get(col, 'Aucun'),
                                'arr': arr_v, 'account_name': row['Account Name'], 'slot': col,
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