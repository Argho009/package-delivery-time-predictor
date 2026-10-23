import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_advanced_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Premium Modern Dark Dashboard Theme
    BG_OBSIDIAN = RGBColor(11, 15, 25)       # Ultra-deep obsidian (#0B0F19)
    BG_CARD     = RGBColor(21, 29, 46)       # Dark tech container (#151D2E)
    BG_CARD_ALT = RGBColor(28, 38, 59)       # Slightly lighter card (#1C263B)
    BORDER_DARK = RGBColor(39, 51, 77)       # Subtle border (#27334D)
    
    # Modern Accents
    ACC_CYAN    = RGBColor(0, 240, 255)      # Electric Cyan (#00F0FF)
    ACC_BLUE    = RGBColor(56, 189, 248)     # Sky Blue (#38BDF8)
    ACC_PURPLE  = RGBColor(168, 85, 247)     # Violet/Purple (#A855F7)
    ACC_GREEN   = RGBColor(16, 185, 129)     # Emerald Green (#10B981)
    ACC_ORANGE  = RGBColor(251, 146, 60)     # Neon Coral/Orange (#FB923C)
    ACC_AMBER   = RGBColor(251, 191, 36)     # Amber Gold (#FBBF24)
    ACC_ROSE    = RGBColor(244, 63, 94)      # Rose Red (#F43F5E)
    
    # Text Contrasts
    TEXT_HERO   = RGBColor(255, 255, 255)    # 100% White
    TEXT_BODY   = RGBColor(203, 213, 225)    # Slate-200
    TEXT_MUTED  = RGBColor(148, 163, 184)    # Slate-400
    TEXT_DARK   = RGBColor(15, 23, 42)

    FONT_DISPLAY = "Bahnschrift"
    FONT_SEMIBOLD = "Segoe UI Semibold"
    FONT_BODY    = "Segoe UI"
    FONT_CODE    = "Consolas"

    def fill_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_OBSIDIAN
        bg.line.fill.background()
        return bg

    def add_top_nav(slide, title, category="ANALYSIS PHASE", slide_num=1, subtitle=None):
        # Dual-tone top accent line
        line1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.35), Inches(5.0), Inches(0.04))
        line1.fill.solid()
        line1.fill.fore_color.rgb = ACC_CYAN
        line1.line.fill.background()

        line2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.8), Inches(0.35), Inches(6.733), Inches(0.04))
        line2.fill.solid()
        line2.fill.fore_color.rgb = ACC_PURPLE
        line2.line.fill.background()

        # Institute Breadcrumb
        tb_brand = slide.shapes.add_textbox(Inches(0.8), Inches(0.44), Inches(8.5), Inches(0.32))
        p_b = tb_brand.text_frame.paragraphs[0]
        p_b.text = "SSIPMT RAIPUR  •  DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING  •  5TH SEMESTER"
        p_b.font.name = FONT_DISPLAY
        p_b.font.size = Pt(8.5)
        p_b.font.bold = True
        p_b.font.color.rgb = ACC_BLUE

        # Category Badge Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.0), Inches(0.42), Inches(2.533), Inches(0.35))
        pill.fill.solid()
        pill.fill.fore_color.rgb = BG_CARD
        pill.line.color.rgb = ACC_CYAN
        pill.line.width = Pt(1)
        p_pill = pill.text_frame.paragraphs[0]
        p_pill.text = f"{category}  |  {slide_num}/16"
        p_pill.alignment = PP_ALIGN.CENTER
        p_pill.font.name = FONT_DISPLAY
        p_pill.font.size = Pt(8.5)
        p_pill.font.bold = True
        p_pill.font.color.rgb = ACC_CYAN

        # Main Slide Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.733), Inches(0.55))
        pt = tb_title.text_frame.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_DISPLAY
        pt.font.size = Pt(21)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_HERO

        # Subtitle if present
        if subtitle:
            tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.35))
            ps = tb_sub.text_frame.paragraphs[0]
            ps.text = subtitle
            ps.font.name = FONT_BODY
            ps.font.size = Pt(10)
            ps.font.color.rgb = TEXT_MUTED

    def add_modern_card(slide, left, top, width, height, title="", title_color=ACC_CYAN, stripe_color=None, bg_color=BG_CARD):
        # Card Background
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = BORDER_DARK
        card.line.width = Pt(1)

        # Left vertical accent stripe
        if stripe_color:
            stripe = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(0.08), height)
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = stripe_color
            stripe.line.fill.background()

        # Title
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.4), Inches(0.4))
            p = tb.text_frame.paragraphs[0]
            p.text = title
            p.font.name = FONT_DISPLAY
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = title_color

        return card

    def add_stat_chip(slide, left, top, width, height, stat_value, stat_label, accent_color=ACC_CYAN):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = BG_CARD
        box.line.color.rgb = accent_color
        box.line.width = Pt(1)

        tb = slide.shapes.add_textbox(left, top + Inches(0.08), width, height - Inches(0.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = stat_value
        p1.alignment = PP_ALIGN.CENTER
        p1.font.name = FONT_DISPLAY
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = accent_color

        p2 = tf.add_paragraph()
        p2.text = stat_label
        p2.alignment = PP_ALIGN.CENTER
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1: HERO TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    fill_bg(s1)

    # Glowing tech framing card
    hero_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3))
    hero_card.fill.solid()
    hero_card.fill.fore_color.rgb = BG_CARD
    hero_card.line.color.rgb = BORDER_DARK
    hero_card.line.width = Pt(1.5)

    # Top gradient strip
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACC_CYAN
    top_bar.line.fill.background()

    # Institute Pill Tag
    inst_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.466), Inches(0.95), Inches(6.4), Inches(0.42))
    inst_pill.fill.solid()
    inst_pill.fill.fore_color.rgb = BG_OBSIDIAN
    inst_pill.line.color.rgb = ACC_BLUE
    ip_p = inst_pill.text_frame.paragraphs[0]
    ip_p.text = "SHRI SHANKARACHARYA INSTITUTE OF PROFESSIONAL MGMT & TECH, RAIPUR"
    ip_p.alignment = PP_ALIGN.CENTER
    ip_p.font.name = FONT_DISPLAY
    ip_p.font.size = Pt(9.5)
    ip_p.font.bold = True
    ip_p.font.color.rgb = ACC_BLUE

    # Review Badge
    rev_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.766), Inches(1.5), Inches(3.8), Inches(0.35))
    rev_pill.fill.solid()
    rev_pill.fill.fore_color.rgb = BG_CARD_ALT
    rev_pill.line.color.rgb = ACC_PURPLE
    rp_p = rev_pill.text_frame.paragraphs[0]
    rp_p.text = "3RD PROJECT REVIEW  •  B.TECH 5TH SEMESTER (AIML)"
    rp_p.alignment = PP_ALIGN.CENTER
    rp_p.font.name = FONT_DISPLAY
    rp_p.font.size = Pt(8.5)
    rp_p.font.bold = True
    rp_p.font.color.rgb = ACC_PURPLE

    # Main Big Title
    tb_main = s1.shapes.add_textbox(Inches(1.2), Inches(2.05), Inches(10.933), Inches(1.3))
    tf_m = tb_main.text_frame
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "DeliverAI : Package Delivery Time Predictor"
    p_m1.alignment = PP_ALIGN.CENTER
    p_m1.font.name = FONT_DISPLAY
    p_m1.font.size = Pt(32)
    p_m1.font.bold = True
    p_m1.font.color.rgb = TEXT_HERO

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "Intelligent Multi-Model ETA Regression & OSRM Highway Corridor Telemetry for Indian Logistics"
    p_m2.alignment = PP_ALIGN.CENTER
    p_m2.font.name = FONT_BODY
    p_m2.font.size = Pt(13)
    p_m2.font.color.rgb = ACC_CYAN

    # Team & Mentorship Dual Cards
    add_modern_card(s1, Inches(1.4), Inches(3.6), Inches(5.1), Inches(1.85), "PROJECT TEAM CREDENTIALS", ACC_CYAN, ACC_CYAN, BG_OBSIDIAN)
    tb_t = s1.shapes.add_textbox(Inches(1.65), Inches(4.05), Inches(4.6), Inches(1.3))
    tf_t = tb_t.text_frame
    t_lines = [
        ("• Leader : ", "Satyam Verma (Team Coordination & Strategy)"),
        ("• Research Person : ", "Tanu Sahu (Literature & Benchmark Analysis)"),
        ("• Frontend : ", "Yash Sahu (UI/UX, Glassmorphic Dashboard & Maps)"),
        ("• Dataset & Model : ", "Arghodeep Chowdhury (184k Telemetry, 19 Models & SLM)"),
    ]
    for i, (k, v) in enumerate(t_lines):
        p = tf_t.paragraphs[0] if i == 0 else tf_t.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(8.5); r1.font.color.rgb = ACC_CYAN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(8.5); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(2)

    add_modern_card(s1, Inches(6.833), Inches(3.6), Inches(5.1), Inches(1.85), "DEPARTMENTAL SUPERVISION", ACC_GREEN, ACC_GREEN, BG_OBSIDIAN)
    tb_g = s1.shapes.add_textbox(Inches(7.083), Inches(4.05), Inches(4.6), Inches(1.3))
    tf_g = tb_g.text_frame
    g_lines = [
        ("• Project In-Charge : ", "Ms. Rashmi Banchhor (Assistant Professor, AIML)"),
        ("• Head of Department : ", "Dr. Anjali Chandra (HOD, AIML)"),
        ("• Review Dates : ", "23rd & 24th October 2026"),
    ]
    for i, (k, v) in enumerate(g_lines):
        p = tf_g.paragraphs[0] if i == 0 else tf_g.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(10); r1.font.color.rgb = TEXT_HERO
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(10); r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # 5 Bottom Metric Chips
    stat_items = [
        ("184,000+", "Unified Indian Records", ACC_CYAN),
        ("19 Models", "Benchmarked ML/DL", ACC_BLUE),
        ("0.9624 R²", "Peak Ensemble Score", ACC_GREEN),
        ("99.35%", "Laya SLM Routing Acc", ACC_PURPLE),
        ("< 45 ms", "CUDA GPU Latency", ACC_AMBER),
    ]
    for i, (val, lbl, col) in enumerate(stat_items):
        left_pos = Inches(1.1 + i * 2.25)
        add_stat_chip(s1, left_pos, Inches(5.65), Inches(2.1), Inches(0.95), val, lbl, col)

    # =========================================================================
    # SLIDE 2: MOTIVATION & COMPARATIVE ANALYSIS
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    fill_bg(s2)
    add_top_nav(s2, "Project Motivation: The Indian Logistics Dilemma", "ANALYSIS PHASE", 2, "Why traditional dispatch heuristics fail on Indian transport networks")

    # Left Card: Traditional Systems (Red/Muted)
    add_modern_card(s2, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1), "CONVENTIONAL HEURISTIC DISPATCH (LIMITATIONS)", ACC_ROSE, ACC_ROSE)
    tb_left = s2.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.3))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True
    flaws = [
        ("❌ Static Speed Assumptions: ", "Assumes constant 40-50 km/h across all state highways, ignoring regional road quality."),
        ("❌ Zero Weather Sensitivity: ", "Monsoon rainfall causes 15% to 35% systemic delays that static systems completely overlook."),
        ("❌ Urban Bottlenecks: ", "Fails to distinguish peak-hour metro gridlocks from express highway free-flow conditions."),
        ("❌ Commercial API Dependency: ", "Heavy recurring pay-per-call charges from Google Maps API without domain model control."),
        ("❌ High Return-to-Origin (RTO): ", "Inaccurate ETA windows cause customer unavailability, leading to multi-crore courier losses.")
    ]
    for i, (k, v) in enumerate(flaws):
        p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = ACC_ROSE
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(10); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(8)

    # Right Card: DeliverAI (Green/Cyan)
    add_modern_card(s2, Inches(6.933), Inches(1.75), Inches(5.6), Inches(5.1), "DELIVERAI INTELLIGENT ETA ENGINE (OUR SOLUTION)", ACC_GREEN, ACC_GREEN)
    tb_right = s2.shapes.add_textbox(Inches(7.183), Inches(2.3), Inches(5.1), Inches(4.3))
    tf_r = tb_right.text_frame
    tf_r.word_wrap = True
    benefits = [
        ("✔ 184k Real Indian Telemetry: ", "Trained on real courier journeys (Delhivery, Amazon India, Bangalore traffic)."),
        ("✔ Dynamic OSRM Routing: ", "Leverages open-source routing machine for true road distance and turn-by-turn vectors."),
        ("✔ 19 Multi-Model Intelligence: ", "Deploys gradient boosting & ensemble regression tailored to specific shipment types."),
        ("✔ Corridor-Stratified Routing: ", "Auto-selects optimal model based on trip distance (Hyperlocal, Regional, Interstate)."),
        ("✔ Zero Commercial API Costs: ", "100% open-source architecture with offline-capable caching and sub-50ms inference.")
    ]
    for i, (k, v) in enumerate(benefits):
        p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(10); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & MEASURABLE OBJECTIVES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    fill_bg(s3)
    add_top_nav(s3, "Problem Statement & Project Objectives", "ANALYSIS PHASE", 3)

    # Top Problem Statement Box
    add_modern_card(s3, Inches(0.8), Inches(1.7), Inches(11.733), Inches(1.85), "FORMAL PROBLEM STATEMENT", ACC_AMBER, ACC_AMBER)
    tb_ps = s3.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(11.233), Inches(1.2))
    tf_ps = tb_ps.text_frame
    tf_ps.word_wrap = True
    p_ps = tf_ps.paragraphs[0]
    p_ps.text = (
        "\"To architect, train, and deploy an end-to-end Machine Learning delivery duration prediction system "
        "that models real-world non-linear delays across Indian logistics corridors—combining route topology, "
        "traffic congestion, and shipment attributes into an accurate, low-latency, and zero-cost web application.\""
    )
    p_ps.font.name = FONT_BODY
    p_ps.font.size = Pt(12.5)
    p_ps.font.italic = True
    p_ps.font.color.rgb = TEXT_HERO

    # 4 Numbered Objectives Cards Below
    objs_data = [
        ("01", "DATASET UNIFICATION", "Ingest, clean, normalize and merge 184,000+ logistics rows from 6 distinct real-world Indian freight sources.", ACC_CYAN),
        ("02", "19-MODEL BENCHMARK", "Train and rigorously compare 19 algorithms (Ensembles, Boosters, Deep Learning, Baselines) on standard metrics.", ACC_BLUE),
        ("03", "CORRIDOR STRATIFICATION", "Evaluate performance across 48 discrete 50km intervals (0 to 2,400 km) to establish an operational routing rulebook.", ACC_PURPLE),
        ("04", "FULL-STACK DEPLOYMENT", "Build a production-ready Flask REST API and interactive Leaflet map dashboard with sub-50ms prediction latency.", ACC_GREEN),
    ]

    for i, (num, heading, desc, col) in enumerate(objs_data):
        left_pos = Inches(0.8 + i * 2.98)
        add_modern_card(s3, left_pos, Inches(3.8), Inches(2.78), Inches(3.1), "", col, col)
        
        # Big number
        tb_num = s3.shapes.add_textbox(left_pos + Inches(0.15), Inches(3.9), Inches(1.0), Inches(0.5))
        pn = tb_num.text_frame.paragraphs[0]
        pn.text = num
        pn.font.name = FONT_DISPLAY
        pn.font.size = Pt(20)
        pn.font.bold = True
        pn.font.color.rgb = col

        # Heading
        tb_h = s3.shapes.add_textbox(left_pos + Inches(0.15), Inches(4.5), Inches(2.48), Inches(0.45))
        ph = tb_h.text_frame.paragraphs[0]
        ph.text = heading
        ph.font.name = FONT_DISPLAY
        ph.font.size = Pt(10.5)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_HERO

        # Desc
        tb_d = s3.shapes.add_textbox(left_pos + Inches(0.15), Inches(5.0), Inches(2.48), Inches(1.7))
        pd = tb_d.text_frame
        pd.word_wrap = True
        pp = pd.paragraphs[0]
        pp.text = desc
        pp.font.name = FONT_BODY
        pp.font.size = Pt(9.5)
        pp.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: FEASIBILITY & TECHNICAL STACK
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    fill_bg(s4)
    add_top_nav(s4, "Technical Architecture & Technology Stack", "ANALYSIS PHASE", 4, "Complete breakdown of toolchains and framework choices")

    stack_cols = [
        ("1. AI & Machine Learning", ACC_CYAN, [
            ("Core Framework: ", "Scikit-Learn 1.4+"),
            ("On-Device SLM: ", "ModernBERT-421M (Laya Fine-Tuned)"),
            ("Meta-Router: ", "Dual-Tier Meta-Classifier (<0.4ms)"),
            ("Gradient Boosters: ", "CatBoost, LightGBM, XGBoost"),
            ("Deep Learning: ", "PyTorch 2.5.1 + CUDA 12.1"),
            ("Validation: ", "80/20 Stratified + 99.35% SLM Acc")
        ]),
        ("2. Backend API Services", ACC_BLUE, [
            ("Web Framework: ", "Python 3.10+ & Flask 3.x"),
            ("Architecture: ", "Modular Application Factory"),
            ("ORM Layer: ", "SQLAlchemy 2.x"),
            ("Routing Engine: ", "OSRM Local/Public Server"),
            ("Geocoding API: ", "Nominatim OpenStreetMap"),
            ("Weather API: ", "OpenWeatherMap REST API")
        ]),
        ("3. Frontend Dashboard", ACC_GREEN, [
            ("Structure: ", "Semantic HTML5 UI"),
            ("Styling: ", "Vanilla CSS3 Glassmorphism"),
            ("Scripting: ", "Asynchronous ES6+ JavaScript"),
            ("Map Engine: ", "Leaflet.js + OSM Tiles"),
            ("Route Polylines: ", "GeoJSON Vector Decoding"),
            ("Responsiveness: ", "Desktop, Tablet & Mobile Ready")
        ]),
        ("4. Data & Persistence", ACC_AMBER, [
            ("Primary DB: ", "MySQL 8.x (Production)"),
            ("Fallback DB: ", "SQLite 3 (Local Dev)"),
            ("Data Warehousing: ", "Pandas DataFrames / CSV"),
            ("Data Scale: ", "184,000+ Logistics Rows"),
            ("Security: ", "Environment Configuration (.env)"),
            ("Containerization: ", "Docker & Docker Compose")
        ])
    ]

    for i, (title, col, items) in enumerate(stack_cols):
        left_pos = Inches(0.8 + i * 2.98)
        add_modern_card(s4, left_pos, Inches(1.75), Inches(2.78), Inches(5.1), title, col, col)
        tb = s4.shapes.add_textbox(left_pos + Inches(0.18), Inches(2.35), Inches(2.42), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (k, v) in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            r1 = p.add_run(); r1.text = f"{k}\n"; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = TEXT_HERO
            r2 = p.add_run(); r2.text = f"{v}\n"; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 5: DATA ANALYSIS & FEATURE ENGINEERING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    fill_bg(s5)
    add_top_nav(s5, "Data Analysis: 184k Records & Feature Engineering", "ANALYSIS PHASE", 5)

    # Left: Table of Datasets
    add_modern_card(s5, Inches(0.8), Inches(1.75), Inches(6.0), Inches(5.1), "Unified Indian Logistics Data Sources", ACC_CYAN, ACC_CYAN)
    
    t_shape = s5.shapes.add_table(7, 3, Inches(1.0), Inches(2.35), Inches(5.6), Inches(4.2))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(2.5)
    tbl.columns[1].width = Inches(1.1)
    tbl.columns[2].width = Inches(2.0)

    heads = ["Dataset Source", "Volume", "Logistics Domain"]
    for c_idx, h in enumerate(heads):
        c = tbl.cell(0, c_idx)
        c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = BG_CARD_ALT
        p = c.text_frame.paragraphs[0]
        p.font.name = FONT_DISPLAY; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = ACC_CYAN

    data_src = [
        ("Delhivery Logistics", "55,000", "Courier Corridors & OSRM"),
        ("Amazon India Sales", "25,000", "E-Commerce Fulfillment"),
        ("Hyperlocal Parcel Trips", "45,593", "Urban Two-Wheeler Routes"),
        ("Bangalore Traffic Corridors", "8,936", "Metro Congestion Peaks"),
        ("Indian Road & Hazard Factors", "20,000", "Highway Condition Factors"),
        ("Indian Railways Freight", "10,000", "Heavy Rail Container Buffer")
    ]
    for r_idx, (src, vol, dom) in enumerate(data_src):
        for c_idx, val in enumerate([src, vol, dom]):
            c = tbl.cell(r_idx + 1, c_idx)
            c.text = val
            c.fill.solid(); c.fill.fore_color.rgb = BG_OBSIDIAN
            p = c.text_frame.paragraphs[0]
            p.font.name = FONT_BODY; p.font.size = Pt(9)
            if c_idx == 0:
                p.font.bold = True; p.font.color.rgb = TEXT_HERO
            elif c_idx == 1:
                p.font.color.rgb = ACC_BLUE; p.font.bold = True
            else:
                p.font.color.rgb = TEXT_MUTED

    # Right: 7 Features
    add_modern_card(s5, Inches(7.1), Inches(1.75), Inches(5.433), Inches(5.1), "7 Core Engineered Input Features", ACC_GREEN, ACC_GREEN)
    tb_feat = s5.shapes.add_textbox(Inches(7.35), Inches(2.35), Inches(4.95), Inches(4.3))
    tf_f = tb_feat.text_frame
    tf_f.word_wrap = True
    features = [
        ("distance_km [Float] : ", "True highway route distance computed via OSRM turn-by-turn routing engine."),
        ("traffic_duration_min [Float] : ", "Traffic-adjusted baseline duration accounting for corridor congestion."),
        ("traffic_level_enc [Categorical] : ", "Encoded congestion factor: LOW (0), MODERATE (1), HIGH (2), SEVERE (3)."),
        ("package_weight_kg [Float] : ", "Net shipment mass directly scaling transit vehicle speed and handling."),
        ("package_type_enc [Categorical] : ", "SMALL (0), MEDIUM (1), LARGE (2), FRAGILE (3), PERISHABLE (4)."),
        ("priority_enc [Categorical] : ", "Service tier: STANDARD (0), EXPRESS (1), OVERNIGHT (2)."),
        ("shipping_mode_enc [Categorical] : ", "Modal choice: ROAD (0), AIR (1), RAIL (2), SEA (3).")
    ]
    for i, (k, v) in enumerate(features):
        p = tf_f.paragraphs[0] if i == 0 else tf_f.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(5)

    # =========================================================================
    # SLIDE 6: SYSTEM ARCHITECTURE DESIGN
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    fill_bg(s6)
    add_top_nav(s6, "System Architecture: 3-Tier Layered Framework", "DESIGN PHASE", 6, "High-level separation of presentation, business logic, and persistence")

    arch_layers = [
        ("TIER 1 : CLIENT PRESENTATION LAYER", ACC_CYAN, [
            "• Single Page Web Application with custom glassmorphic CSS styling",
            "• Asynchronous Dispatch Input Form with live validation & debounce geocoding",
            "• Interactive Leaflet.js Route Map rendering polyline highway coordinates",
            "• Dynamic ETA Result Dashboard showing ETA in hours/days + ±30m confidence interval"
        ]),
        ("TIER 2 : APPLICATION & INFERENCE LAYER (FLASK)", ACC_BLUE, [
            "• Modular REST API Services exposing /api/predict, /api/history, and /api/analytics",
            "• Geocoding Integration: Translates city names to GPS coordinates via Nominatim",
            "• OSRM Client: Computes exact road distances and baseline travel vectors",
            "• Preprocessor Pipeline: Feature encoding and StandardScaler tensor transformation",
            "• In-Memory Singleton Model Loader: Sub-50ms execution eliminating model cold starts"
        ]),
        ("TIER 3 : DATA PERSISTENCE & REGISTRY LAYER", ACC_GREEN, [
            "• Serialized Model Registry: 19 .pkl and PyTorch TabNet binary weight models",
            "• Scaler & Encoders: Pickled preprocessor transformers maintaining feature alignment",
            "• Relational Storage: MySQL 8.x / SQLite storing deliveries, predictions, and actuals",
            "• Performance Log Warehouse: Historical error analysis for continuous evaluation"
        ])
    ]

    for i, (title, col, items) in enumerate(arch_layers):
        top_pos = Inches(1.75 + i * 1.75)
        add_modern_card(s6, Inches(0.8), top_pos, Inches(11.733), Inches(1.55), title, col, col)
        tb = s6.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.48), Inches(11.233), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, it in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = it
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_BODY
            p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 7: DATA FLOW DIAGRAM (DFD) & PIPELINE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    fill_bg(s7)
    add_top_nav(s7, "Data Flow Diagram & Pipeline Workflow", "DESIGN PHASE", 7, "Step-by-step path from customer dispatch input to final ETA delivery")

    flow_nodes = [
        ("01", "Dispatch Input", "Origin, Destination, Weight, Priority, Shipping Mode entered on Web UI.", ACC_CYAN),
        ("02", "Geocoding", "Nominatim Engine converts city strings into GPS Latitude and Longitude.", ACC_BLUE),
        ("03", "OSRM Routing", "Queries highway graph to extract exact distance (km) & transit time.", ACC_PURPLE),
        ("04", "Feature Pipeline", "Encodes categorical features and applies StandardScaler normalization.", ACC_ORANGE),
        ("05", "Model Inference", "Selected ML Model outputs estimated delivery duration in hours.", ACC_GREEN),
        ("06", "Render & Log", "Renders map polyline + ETA card on UI; persists record in MySQL database.", ACC_CYAN),
    ]

    for i, (num, h, desc, col) in enumerate(flow_nodes):
        col_idx = i % 3
        row_idx = i // 3
        left_pos = Inches(0.8 + col_idx * 3.98)
        top_pos = Inches(1.8 + row_idx * 2.55)

        add_modern_card(s7, left_pos, top_pos, Inches(3.78), Inches(2.3), "", col, col)
        
        # Step Number Badge
        step_badge = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.18), Inches(0.8), Inches(0.35))
        step_badge.fill.solid(); step_badge.fill.fore_color.rgb = BG_OBSIDIAN
        step_badge.line.color.rgb = col
        p_sb = step_badge.text_frame.paragraphs[0]
        p_sb.text = f"STEP {num}"
        p_sb.alignment = PP_ALIGN.CENTER
        p_sb.font.name = FONT_DISPLAY; p_sb.font.size = Pt(8.5); p_sb.font.bold = True; p_sb.font.color.rgb = col

        # Title
        tb_h = s7.shapes.add_textbox(left_pos + Inches(1.15), top_pos + Inches(0.15), Inches(2.4), Inches(0.4))
        ph = tb_h.text_frame.paragraphs[0]
        ph.text = h
        ph.font.name = FONT_DISPLAY; ph.font.size = Pt(12); ph.font.bold = True; ph.font.color.rgb = TEXT_HERO

        # Desc
        tb_d = s7.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.7), Inches(3.38), Inches(1.4))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True
        pd = tf_d.paragraphs[0]
        pd.text = desc
        pd.font.name = FONT_BODY; pd.font.size = Pt(10); pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 8: DATABASE & SCHEMA DESIGN
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    fill_bg(s8)
    add_top_nav(s8, "Database Design & Relational Schema", "DESIGN PHASE", 8, "Normalized relational schema for persistent shipment tracking and audit")

    tables_data = [
        ("1. deliveries (Shipment Orders)", ACC_CYAN, [
            ("id", "INTEGER", "PRIMARY KEY, AUTO_INC"),
            ("origin_city", "VARCHAR(100)", "Origin Dispatch Hub"),
            ("destination_city", "VARCHAR(100)", "Destination Hub"),
            ("distance_km", "FLOAT", "OSRM Highway Route Length"),
            ("package_weight_kg", "FLOAT", "Parcel Payload Mass"),
            ("shipping_mode", "VARCHAR(20)", "ROAD, AIR, RAIL, SEA"),
            ("priority", "VARCHAR(20)", "STANDARD, EXPRESS, OVERNIGHT"),
            ("created_at", "TIMESTAMP", "Creation Time")
        ]),
        ("2. predictions (ML Inference Logs)", ACC_GREEN, [
            ("id", "INTEGER", "PRIMARY KEY, AUTO_INC"),
            ("delivery_id", "INTEGER", "FOREIGN KEY -> deliveries.id"),
            ("predicted_eta_hours", "FLOAT", "Estimated Transit Duration"),
            ("model_used", "VARCHAR(50)", "e.g., 'voting', 'knn'"),
            ("confidence_lower", "FLOAT", "-30m Tolerance Bound"),
            ("confidence_upper", "FLOAT", "+30m Tolerance Bound"),
            ("actual_hours", "FLOAT", "Real Recorded Transit Time"),
            ("absolute_error", "FLOAT", "Computed Evaluation Error")
        ]),
        ("3. corridor_analytics (Corridors)", ACC_AMBER, [
            ("corridor_id", "INTEGER", "PRIMARY KEY, AUTO_INC"),
            ("route_code", "VARCHAR(50)", "INDEX (e.g., 'MUM-PUN')"),
            ("avg_transit_hours", "FLOAT", "Moving Historical Average"),
            ("congestion_index", "FLOAT", "Peak-Hour Delay Factor"),
            ("weather_impact", "FLOAT", "Rain/Monsoon Risk Factor"),
            ("total_shipments", "INTEGER", "Corridor Volume Counter"),
            ("last_updated", "DATETIME", "Telemetry Sync Timestamp")
        ])
    ]

    for i, (tbl_title, col, fields) in enumerate(tables_data):
        left_pos = Inches(0.8 + i * 3.98)
        add_modern_card(s8, left_pos, Inches(1.75), Inches(3.78), Inches(5.1), tbl_title, col, col)
        
        # Schema field list
        tb = s8.shapes.add_textbox(left_pos + Inches(0.18), Inches(2.35), Inches(3.42), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (fname, ftype, fdesc) in enumerate(fields):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            r1 = p.add_run(); r1.text = f"{fname} "; r1.font.bold = True; r1.font.size = Pt(9); r1.font.color.rgb = col
            r2 = p.add_run(); r2.text = f"({ftype})\n"; r2.font.size = Pt(8); r2.font.color.rgb = TEXT_MUTED
            r3 = p.add_run(); r3.text = f"  └ {fdesc}\n"; r3.font.size = Pt(8.5); r3.font.color.rgb = TEXT_BODY
            p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 9: ML METHODOLOGY (19 ALGORITHMS)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    fill_bg(s9)
    add_top_nav(s9, "Machine Learning Methodology: 19 Evaluated Algorithms", "IMPLEMENTATION PHASE", 9, "Broad architectural evaluation across 5 algorithmic families")

    families = [
        ("1. Meta-Ensemble Models (3)", ACC_CYAN, [
            ("Voting Regressor : ", "Soft weighted combination of top gradient boosting & forest models."),
            ("Stacking Regressor : ", "Two-tier meta-learner training a Ridge meta-model on base predictions."),
            ("Bagging Regressor : ", "Bootstrap aggregation reducing prediction variance across noisy corridors.")
        ]),
        ("2. Gradient Boosting Machines (5)", ACC_BLUE, [
            ("CatBoost Regressor : ", "Symmetric trees with native categorical handling and minimal overfitting."),
            ("LightGBM Regressor : ", "Fast leaf-wise tree growth with histogram-based feature binning."),
            ("XGBoost Regressor : ", "Extreme gradient boosting with L1/L2 regularization."),
            ("HistGradientBoosting : ", "Scikit-learn native fast binned boosting."),
            ("Gradient Boosting : ", "Standard sequential residual gradient boosting.")
        ]),
        ("3. Tree-Based Models (3)", ACC_GREEN, [
            ("Random Forest Regressor : ", "100 decorrelated parallel decision trees with sub-feature sampling."),
            ("Extra Trees Regressor : ", "Extremely randomized trees with random split thresholds."),
            ("Decision Tree Regressor : ", "Single interpretable CART decision tree baseline.")
        ]),
        ("4. Deep Learning & Baselines (8)", ACC_AMBER, [
            ("PyTorch TabNet : ", "Attentive transformer architecture designed specifically for tabular data."),
            ("Multi-Layer Perceptron (MLP) : ", "Deep neural network with ReLU activations and Adam optimizer."),
            ("KNN & SVR : ", "Distance-based nearest neighbors and support vector regression."),
            ("Linear Baselines : ", "Ordinary Least Squares, Ridge, Lasso, and ElasticNet.")
        ])
    ]

    for i, (title, col, items) in enumerate(families):
        col_idx = i % 2
        row_idx = i // 2
        left_pos = Inches(0.8 + col_idx * 5.98)
        top_pos = Inches(1.75 + row_idx * 2.65)
        add_modern_card(s9, left_pos, top_pos, Inches(5.78), Inches(2.45), title, col, col)
        tb = s9.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.38), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (k, v) in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = col
            r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
            p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 10: MODEL EVALUATION & LEADERBOARD
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    fill_bg(s10)
    add_top_nav(s10, "Model Benchmark Leaderboard (36,806 Test Shipments)", "IMPLEMENTATION PHASE", 10, "Rigorous empirical evaluation on unseen Indian validation shipments")

    # Table on Left
    t_shape = s10.shapes.add_table(9, 6, Inches(0.8), Inches(1.75), Inches(8.3), Inches(5.1))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(0.7)
    tbl.columns[1].width = Inches(2.4)
    tbl.columns[2].width = Inches(1.3)
    tbl.columns[3].width = Inches(1.3)
    tbl.columns[4].width = Inches(1.3)
    tbl.columns[5].width = Inches(1.3)

    heads = ["Rank", "Model Architecture", "R² Score", "RMSE (h)", "MAE (h)", "±30m Tol"]
    for c_idx, h in enumerate(heads):
        c = tbl.cell(0, c_idx)
        c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = BG_CARD_ALT
        p = c.text_frame.paragraphs[0]
        p.font.name = FONT_DISPLAY; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = ACC_CYAN

    leaderboard = [
        ("🥇 1", "Voting Regressor", "0.9624", "2.873 h", "1.290 h", "56.5%"),
        ("🥈 2", "Random Forest", "0.9623", "2.877 h", "1.281 h", "56.8%"),
        ("🥉 3", "Stacking Regressor", "0.9622", "2.879 h", "1.300 h", "56.2%"),
        ("4", "Extra Trees Regressor", "0.9622", "2.880 h", "1.285 h", "56.7%"),
        ("5", "CatBoost Regressor", "0.9619", "2.891 h", "1.309 h", "55.7%"),
        ("6", "LightGBM Regressor", "0.9619", "2.892 h", "1.304 h", "56.3%"),
        ("11", "MLP Neural Network", "0.9607", "2.934 h", "1.333 h", "55.3%"),
        ("18", "Linear Regression (OLS)", "0.8495", "5.745 h", "3.383 h", "20.3%"),
    ]
    for r_idx, (rk, mname, r2, rmse, mae, tol) in enumerate(leaderboard):
        for c_idx, val in enumerate([rk, mname, r2, rmse, mae, tol]):
            c = tbl.cell(r_idx + 1, c_idx)
            c.text = val
            c.fill.solid()
            c.fill.fore_color.rgb = BG_OBSIDIAN if r_idx % 2 == 0 else BG_CARD
            p = c.text_frame.paragraphs[0]
            p.font.name = FONT_BODY; p.font.size = Pt(9)
            if c_idx == 0:
                p.font.bold = True; p.font.color.rgb = ACC_AMBER if "1" in val else TEXT_HERO
            elif c_idx == 1:
                p.font.bold = True; p.font.color.rgb = TEXT_HERO
            elif c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = ACC_GREEN if float(val) > 0.95 else ACC_ROSE
            else:
                p.font.color.rgb = TEXT_MUTED

    # Right Card: Insights
    add_modern_card(s10, Inches(9.3), Inches(1.75), Inches(3.233), Inches(5.1), "Key Benchmark Takeaways", ACC_GREEN, ACC_GREEN)
    tb_in = s10.shapes.add_textbox(Inches(9.45), Inches(2.35), Inches(2.933), Inches(4.3))
    tf_in = tb_in.text_frame
    tf_in.word_wrap = True
    ins = [
        ("• Ensemble Superiority: ", "Meta-voting achieves peak R² of 0.9624 by compensating individual model biases."),
        ("• Low Deviation: ", "Average Mean Absolute Error is just 1.28 hours across thousands of multi-day routes."),
        ("• Linear Failure: ", "OLS regression performs poorly (0.849 R², 3.38h MAE), proving strong non-linearity."),
        ("• Real-Time Inference: ", "LightGBM executes in <2ms, making it ideal for live web requests.")
    ]
    for i, (k, v) in enumerate(ins):
        p = tf_in.paragraphs[0] if i == 0 else tf_in.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 11: 50KM CORRIDOR BENCHMARK (NOVELTY)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    fill_bg(s11)
    add_top_nav(s11, "Novelty: 50km Distance Interval Routing Benchmark", "IMPLEMENTATION PHASE", 11, "Empirical evaluation across 48 brackets with 912,000 total model inferences")

    top_banner = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.68), Inches(11.733), Inches(0.6))
    top_banner.fill.solid(); top_banner.fill.fore_color.rgb = BG_CARD
    top_banner.line.color.rgb = ACC_CYAN
    p_tb = top_banner.text_frame.paragraphs[0]
    p_tb.text = "CORRIDOR RULEBOOK  •  48 Brackets of 50 km (0 to 2,400 km)  •  1,000 Inferences/Bracket  •  Real Data Driven"
    p_tb.alignment = PP_ALIGN.CENTER
    p_tb.font.name = FONT_DISPLAY; p_tb.font.size = Pt(10.5); p_tb.font.bold = True; p_tb.font.color.rgb = ACC_CYAN

    corridors = [
        ("Hyperlocal & Intra-City (0 - 50 km)", "Urban Two-Wheelers / Zomato / Swiggy", "KNN / Bagging", "0.022 h (~1.3 mins)", "97.1%", "99.1%", ACC_CYAN),
        ("Metro Suburbs (50 - 150 km)", "Intra-City Delivery Vans & Couriers", "KNN / Decision Tree", "0.165 h (~9.9 mins)", "96.5%", "91.3%", ACC_BLUE),
        ("Regional Corridors (150 - 400 km)", "State Highway Feeder Logistics", "KNN / Decision Tree", "0.300 h (~18 mins)", "97.6%", "85.6%", ACC_PURPLE),
        ("Interstate Freight (400 - 800 km)", "Multi-Axle Heavy Highway Trucks", "KNN / Decision Tree", "0.564 h (~33 mins)", "97.7%", "82.8%", ACC_GREEN),
        ("Long-Haul Express (800 - 1500 km)", "Dedicated Freight Corridor / Rail", "KNN / Extra Trees", "0.798 h (~47 mins)", "97.8%", "82.9%", ACC_AMBER),
        ("Trans-National (> 1500 km)", "Cross-Country Intermodal Freight", "KNN / Meta-Voting", "1.295 h (~77 mins)", "97.8%", "80.9%", ACC_ROSE),
    ]

    for i, (tier_title, domain, model, mae, acc, tol, col) in enumerate(corridors):
        col_idx = i % 3
        row_idx = i // 3
        left_pos = Inches(0.8 + col_idx * 3.98)
        top_pos = Inches(2.45 + row_idx * 2.35)

        add_modern_card(s11, left_pos, top_pos, Inches(3.78), Inches(2.2), tier_title, col, col)
        tb = s11.shapes.add_textbox(left_pos + Inches(0.18), top_pos + Inches(0.55), Inches(3.42), Inches(1.55))
        tf = tb.text_frame
        tf.word_wrap = True
        c_lines = [
            ("Domain : ", domain),
            ("Top Model : ", model),
            ("Best MAE : ", mae),
            ("Accuracy / Tol : ", f"{acc}  (±30m: {tol})")
        ]
        for j, (k, v) in enumerate(c_lines):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9); r1.font.color.rgb = col
            r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
            p.space_after = Pt(1)

    # =========================================================================
    # SLIDE 12: ON-DEVICE LAYA SLM & DUAL-TIER META-ROUTER (NOVELTY)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    fill_bg(s12)
    add_top_nav(s12, "Novelty: Fine-Tuned Laya SLM & Dual-Tier Meta-Router", "INNOVATION PHASE", 12, "ModernBERT-421M parameter on-device neural dispatcher running on RTX 3050 CUDA GPU")

    # Top Banner
    slm_banner = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.68), Inches(11.733), Inches(0.6))
    slm_banner.fill.solid(); slm_banner.fill.fore_color.rgb = BG_CARD
    slm_banner.line.color.rgb = ACC_PURPLE
    p_sb = slm_banner.text_frame.paragraphs[0]
    p_sb.text = "BREAKTHROUGH  •  Zero-Shot Bias 19.48% ➔ 99.35% Fine-Tuned Accuracy (+79.87% Gain)  •  ~45ms CUDA  •  Loss 0.0176"
    p_sb.alignment = PP_ALIGN.CENTER
    p_sb.font.name = FONT_DISPLAY; p_sb.font.size = Pt(10.5); p_sb.font.bold = True; p_sb.font.color.rgb = ACC_PURPLE

    # Left Card: Fine-Tuning Pipeline & Zero-Shot Resolution
    add_modern_card(s12, Inches(0.8), Inches(2.4), Inches(5.7), Inches(4.5), "On-Device SLM Fine-Tuning Pipeline", ACC_CYAN, ACC_CYAN)
    tb_slm_l = s12.shapes.add_textbox(Inches(1.05), Inches(2.95), Inches(5.2), Inches(3.8))
    tf_sl = tb_slm_l.text_frame
    tf_sl.word_wrap = True
    slm_left_items = [
        ("• Backbone Architecture: ", "convaiinnovations/laya-typed-decisions based on ModernBERT-421M (8,192 token context window, unpadded flash attention)."),
        ("• Zero-Shot Bias Discovery: ", "Pre-trained base model collapsed to LightGBM (~80% bias, only 19.48% accuracy), unable to parse multi-token Indian freight metrics like '18.5 km'."),
        ("• Data Distillation Corpus: ", "Synthesized 1,540 balanced, stratified decision contracts directly from 184,000+ real delivery journeys into JSONL schema."),
        ("• Empirical Convergence: ", "Trained over 5 epochs with AdamW (lr=5e-5). Cross-entropy loss plunged to 0.0176, achieving 99.35% accuracy and an ultra-calibrated ECE of 0.0077.")
    ]
    for i, (k, v) in enumerate(slm_left_items):
        p = tf_sl.paragraphs[0] if i == 0 else tf_sl.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_CYAN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(5)

    # Right Card: Dual-Tier Meta-Router & 4-Tier Resilience
    add_modern_card(s12, Inches(6.833), Inches(2.4), Inches(5.7), Inches(4.5), "Dual-Tier Router & 4-Tier Fallback Hierarchy", ACC_GREEN, ACC_GREEN)
    tb_slm_r = s12.shapes.add_textbox(Inches(7.083), Inches(2.95), Inches(5.2), Inches(3.8))
    tf_sr = tb_slm_r.text_frame
    tf_sr.word_wrap = True
    slm_right_items = [
        ("• Tier 1 (Neural SLM): ", "Fine-Tuned Laya ModernBERT on RTX 3050 Laptop GPU (1.4GB VRAM, ~45ms latency) performing semantic route reasoning."),
        ("• Tier 1.5 (Empirical Meta-Router): ", "Fast decision tree meta-classifier (meta_router.pkl) achieving 100% in-sample fidelity in <0.4ms on CPU."),
        ("• Tier 2 (Local LLM Server): ", "LM Studio OpenAI-compatible endpoint (/v1/chat/completions) for complex corridor explanations."),
        ("• Tier 3 (Deterministic Heuristics): ", "Guaranteed zero-failure corridor matrix fallback if hardware experiences extreme load."),
        ("• Live Verified Corridors: ", "Monsoon Rain ➔ CatBoost (100% conf)  |  Dense Fog ➔ HistGradientBoosting (100%)  |  Interstate ➔ Voting (100%)  |  Hyperlocal ➔ Bagging (99.8%)")
    ]
    for i, (k, v) in enumerate(slm_right_items):
        p = tf_sr.paragraphs[0] if i == 0 else tf_sr.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 13: FULL-STACK WEB APPLICATION IMPLEMENTATION
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    fill_bg(s13)
    add_top_nav(s13, "Full-Stack Web Application Implementation", "IMPLEMENTATION PHASE", 13, "Production-grade Flask microservices integrated with Leaflet & OSRM")

    add_modern_card(s13, Inches(0.8), Inches(1.75), Inches(5.7), Inches(5.1), "REST API Microservices Layer", ACC_CYAN, ACC_CYAN)
    tb_api = s13.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.2), Inches(4.3))
    tf_a = tb_api.text_frame
    tf_a.word_wrap = True
    api_items = [
        ("POST /api/predict", "Core ML inference route. Ingests origin, destination, weight, package type, priority, and shipping mode. Evaluated by Laya SLM & returns optimal model ETA."),
        ("GET /api/history", "Queries past deliveries with pagination, returning actual vs predicted accuracy metrics for monitoring."),
        ("GET /api/analytics/corridors", "Aggregates latency and congestion metrics across high-frequency Indian highway corridors."),
        ("GET /api/health", "System health probe checking database connections, model registry status, and GPU SLM availability.")
    ]
    for i, (ep, desc) in enumerate(api_items):
        p = tf_a.paragraphs[0] if i == 0 else tf_a.add_paragraph()
        r1 = p.add_run(); r1.text = f"{ep}\n"; r1.font.bold = True; r1.font.size = Pt(10); r1.font.color.rgb = ACC_CYAN
        r2 = p.add_run(); r2.text = f"{desc}\n"; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(6)

    add_modern_card(s13, Inches(6.833), Inches(1.75), Inches(5.7), Inches(5.1), "Frontend UI & Engine Integration", ACC_GREEN, ACC_GREEN)
    tb_fe = s13.shapes.add_textbox(Inches(7.083), Inches(2.35), Inches(5.2), Inches(4.3))
    tf_f = tb_fe.text_frame
    tf_f.word_wrap = True
    fe_items = [
        ("• SLM Route Decision Badge: ", "Renders purple badge with model confidence % and physical corridor reasoning."),
        ("• Interactive Leaflet Routing: ", "Renders true highway geometry between Indian cities using GeoJSON vector decoding."),
        ("• Real-Time Weather Integration: ", "OpenWeatherMap API triggers visual rain/storm delay alerts for delivery dispatchers."),
        ("• Multi-Model Studio Comparison: ", "Runs all 12 algorithms side-by-side in real-time to analyze algorithm divergence."),
        ("• Responsive Design: ", "Modern glassmorphic interface accessible across mobile, tablet, and desktop dispatch screens.")
    ]
    for i, (k, v) in enumerate(fe_items):
        p = tf_f.paragraphs[0] if i == 0 else tf_f.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 14: SYSTEM DEMONSTRATION & USER WORKFLOW
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    fill_bg(s14)
    add_top_nav(s14, "System Demonstration & Working Walkthrough", "IMPLEMENTATION PHASE", 14, "Visual user journey across dispatch planning and intelligence delivery")

    demo_screens = [
        ("Screen 1 : Dispatch Order Form", ACC_CYAN, [
            "• Dispatcher inputs Origin (e.g. Mumbai) & Destination (e.g. Pune/Raipur)",
            "• Sets payload weight in kg, priority (Express/Standard), and shipping mode",
            "• Built-in client validation & Nominatim autocomplete instant search"
        ]),
        ("Screen 2 : Dynamic Map & Corridor Preview", ACC_BLUE, [
            "• Leaflet map displays real-world highway polyline route",
            "• Highlights computed road distance (e.g., 148.5 km) & transit baseline",
            "• Overlays live corridor congestion index and local weather alerts"
        ]),
        ("Screen 3 : AI ETA Prediction & SLM Badge", ACC_GREEN, [
            "• Displays formatted ETA (e.g., '3 Hours 42 Mins') with confidence bar",
            "• Renders Laya SLM chosen model badge with physical reason log",
            "• Multi-modal transit comparison (Truck vs Train vs Air Freight)"
        ]),
        ("Screen 4 : Shipment History & Audit Logs", ACC_AMBER, [
            "• Complete historical log of executed predictions in MySQL",
            "• Error variance tracking comparing predicted ETA vs actual arrival time",
            "• Performance analytics across major Indian intercity corridors"
        ])
    ]

    for i, (title, col, items) in enumerate(demo_screens):
        col_idx = i % 2
        row_idx = i // 2
        left_pos = Inches(0.8 + col_idx * 5.98)
        top_pos = Inches(1.75 + row_idx * 2.65)
        add_modern_card(s14, left_pos, top_pos, Inches(5.78), Inches(2.45), title, col, col)
        tb = s14.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.38), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, it in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = it
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_BODY
            p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 15: CURRENT STATUS & FUTURE ROADMAP
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    fill_bg(s15)
    add_top_nav(s15, "Project Progress Status & Future Roadmap", "RESULTS & ROADMAP", 15, "Completed deliverables for Review 3 vs planned enhancements for Final Review")

    add_modern_card(s15, Inches(0.8), Inches(1.75), Inches(5.7), Inches(5.1), "Completed Milestones (Review 3)", ACC_GREEN, ACC_GREEN)
    tb_done = s15.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.2), Inches(4.3))
    tf_d = tb_done.text_frame
    tf_d.word_wrap = True
    dones = [
        ("✔ Ingested & Merged 184,000+ Records : ", "Unified Delhivery, Amazon India, and Bangalore traffic datasets into standardized schema."),
        ("✔ 19-Model Machine Learning Benchmark : ", "Trained, tuned, and evaluated 19 algorithms (Peak R²: 0.9624, MAE: 1.28h)."),
        ("✔ Fine-Tuned Laya SLM Meta-Router : ", "Fine-tuned ModernBERT-421M on RTX 3050 CUDA GPU, jumping from 19.48% to 99.35% accuracy in 45ms."),
        ("✔ 4-Tier Self-Healing Resilience : ", "Zero-downtime cascading fallback (SLM ➔ Meta-Router ➔ LM Studio ➔ Heuristics)."),
        ("✔ Production Full-Stack Web App : ", "Working Flask + Leaflet system with live OSRM routing and multi-modal comparison.")
    ]
    for i, (k, v) in enumerate(dones):
        p = tf_d.paragraphs[0] if i == 0 else tf_d.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_GREEN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(6)

    add_modern_card(s15, Inches(6.833), Inches(1.75), Inches(5.7), Inches(5.1), "Roadmap for Final Review (Major Phase)", ACC_BLUE, ACC_BLUE)
    tb_fut = s15.shapes.add_textbox(Inches(7.083), Inches(2.35), Inches(5.2), Inches(4.3))
    tf_fut = tb_fut.text_frame
    tf_fut.word_wrap = True
    futures = [
        ("1. Real-Time GPS IoT Tracking : ", "Integrate live vehicle telematics to recalculate ETAs dynamically while the vehicle is in transit."),
        ("2. Automated MLOps Retraining : ", "Periodic pipeline triggered automatically when new shipment ground truth records are logged."),
        ("3. Progressive Web App (PWA) : ", "Mobile-first offline dispatch view for delivery drivers with SMS ETA alerts for customers."),
        ("4. Cloud Containerization : ", "Production deployment on cloud infrastructure using Docker and managed MySQL.")
    ]
    for i, (k, v) in enumerate(futures):
        p = tf_fut.paragraphs[0] if i == 0 else tf_fut.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_BLUE
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 16: CONCLUSION, REFERENCES & Q&A
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    fill_bg(s16)
    add_top_nav(s16, "Conclusion, References & Open Discussion", "CONCLUSION", 16)

    add_modern_card(s16, Inches(0.8), Inches(1.75), Inches(5.7), Inches(5.1), "Project Conclusions & Impact", ACC_CYAN, ACC_CYAN)
    tb_c = s16.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.2), Inches(4.3))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    concs = [
        ("• Intelligent ETA Engine : ", "Replaced error-prone heuristic assumptions with 19 benchmarked algorithms trained on 184k+ real Indian logistics records."),
        ("• High Prediction Precision : ", "Voting Regressor achieved 0.9624 R² accuracy with an average error of just 1.28 hours across long-haul interstate routes."),
        ("• Dynamic Neural Meta-Routing : ", "Fine-tuned ModernBERT-421M SLM achieves 99.35% routing accuracy, dispatching to specialized algorithms in ~45ms."),
        ("• Zero-Cost Self-Healing Stack : ", "Leverages OSRM, local CUDA GPU acceleration, and 4-tier fallbacks eliminating recurring commercial API fees.")
    ]
    for i, (k, v) in enumerate(concs):
        p = tf_c.paragraphs[0] if i == 0 else tf_c.add_paragraph()
        r1 = p.add_run(); r1.text = k; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = ACC_CYAN
        r2 = p.add_run(); r2.text = v; r2.font.size = Pt(9); r2.font.color.rgb = TEXT_BODY
        p.space_after = Pt(6)

    add_modern_card(s16, Inches(6.833), Inches(1.75), Inches(5.7), Inches(3.4), "Academic References & Citations", ACC_GREEN, ACC_GREEN)
    tb_ref = s16.shapes.add_textbox(Inches(7.083), Inches(2.35), Inches(5.2), Inches(2.6))
    tf_ref = tb_ref.text_frame
    tf_ref.word_wrap = True
    refs = [
        "1. Delhivery Logistics Open Dataset (Kaggle Indian Freight & Corridors).",
        "2. Luxen, D., & Vetter, C. 'Real-time routing with OpenStreetMap data' (OSRM).",
        "3. Pedregosa et al., 'Scikit-learn: Machine Learning in Python', JMLR 12.",
        "4. ModernBERT & Laya Architecture (ConvAI Innovations, 2025).",
        "5. Arik, S. O., & Pfister, T. 'TabNet: Attentive Interpretable Tabular Learning', AAAI."
    ]
    for i, r in enumerate(refs):
        p = tf_ref.paragraphs[0] if i == 0 else tf_ref.add_paragraph()
        p.text = r
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(2)

    # Q&A Invite Box
    qa_box = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.833), Inches(5.35), Inches(5.7), Inches(1.5))
    qa_box.fill.solid(); qa_box.fill.fore_color.rgb = BG_CARD
    qa_box.line.color.rgb = ACC_CYAN; qa_box.line.width = Pt(1.5)
    tb_qa = s16.shapes.add_textbox(Inches(7.0), Inches(5.5), Inches(5.366), Inches(1.2))
    tf_qa = tb_qa.text_frame
    p_q1 = tf_qa.paragraphs[0]
    p_q1.text = "THANK YOU!"
    p_q1.alignment = PP_ALIGN.CENTER
    p_q1.font.name = FONT_DISPLAY; p_q1.font.size = Pt(18); p_q1.font.bold = True; p_q1.font.color.rgb = ACC_CYAN
    p_q2 = tf_qa.add_paragraph()
    p_q2.text = "Open for Questions, Evaluation & Live System Demonstration"
    p_q2.alignment = PP_ALIGN.CENTER
    p_q2.font.name = FONT_BODY; p_q2.font.size = Pt(11); p_q2.font.color.rgb = TEXT_HERO

    # Save with fallback if open in PowerPoint
    out_file = "DeliverAI_Project_Review_3_SSIPMT.pptx"
    try:
        prs.save(out_file)
        print(f"Deck saved as '{out_file}' with {len(prs.slides)} slides.")
    except PermissionError:
        alt_file = "DeliverAI_Project_Review_3_SSIPMT_v2.pptx"
        prs.save(alt_file)
        print(f"Original locked; saved as '{alt_file}' with {len(prs.slides)} slides.")

if __name__ == "__main__":
    build_advanced_deck()
