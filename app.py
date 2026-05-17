# ==========================================
# 2. GESTIÓN DE SESIÓN Y URL INTERACTIVA
# ==========================================
if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "mohamed": {"clave": "admin2026", "rol": "MOHAMED (ADMIN)"},
        "profesora": {"clave": "tribunal10", "rol": "PROFESORA (EVALUADOR)"},
        "invitado": {"clave": "invitado123", "rol": "INVITADO"}
    }

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = ""

if "historial" not in st.session_state:
    st.session_state.historial = []

if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

# ==========================================
# CONTROL DE IDIOMA Y LOGOUT
# ==========================================
if "lang_btn" not in st.session_state:
    st.session_state.lang_btn = None

if "logout_click" not in st.session_state:
    st.session_state.logout_click = False

if st.session_state.lang_btn:
    st.session_state.idioma = st.session_state.lang_btn
    st.session_state.lang_btn = None

if st.session_state.logout_click:
    st.session_state.autenticado = False
    st.session_state.rol_usuario = ""
    st.session_state.logout_click = False
    st.rerun()


# ── LOGIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.autenticado:

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:

        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <div style="font-family:'Space Mono',monospace; font-size:2rem; font-weight:700; color:#fff;">
                Object<span style="color:#0066ff">Vision</span>
                <span style="color:#4a6080; font-size:1rem;">AI</span>
            </div>

            <div style="
                font-size:0.72rem;
                color:#2a3a54;
                letter-spacing:2px;
                text-transform:uppercase;
                margin-top:8px;
                font-family:'Space Mono',monospace;
            ">
                Portal de acceso · 2026
            </div>

            <div style="height:1px; background:#1a2744; margin:24px 0;"></div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs([
            "🔑   Iniciar Sesión",
            "📝   Crear Cuenta"
        ])

        # LOGIN
        with tab_login:

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            usuario_input = st.text_input(
                "Usuario",
                placeholder="Tu ID de usuario",
                key="li_u"
            ).strip().lower()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            contrasena_input = st.text_input(
                "Contraseña",
                type="password",
                placeholder="••••••••",
                key="li_p"
            )

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            if st.button(
                "Acceder al Sistema",
                key="btn_login",
                use_container_width=True
            ):

                db = st.session_state.usuarios_db

                if usuario_input in db and db[usuario_input]["clave"] == contrasena_input:

                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = db[usuario_input]["rol"]

                    st.success("✅ Acceso autorizado.")

                    time.sleep(0.4)

                    st.rerun()

                else:
                    st.error("❌ Credenciales incorrectas.")

        # REGISTRO
        with tab_reg:

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            nuevo_u = st.text_input(
                "Nombre de usuario",
                placeholder="Ej: pedro99",
                key="r_u"
            ).strip().lower()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            nueva_p = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Mínimo 4 caracteres",
                key="r_p"
            )

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            confirmar_p = st.text_input(
                "Repite la contraseña",
                type="password",
                placeholder="••••••••",
                key="r_p2"
            )

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            if st.button(
                "Crear Cuenta",
                key="btn_reg",
                use_container_width=True
            ):

                if not nuevo_u or not nueva_p:
                    st.warning("Rellena todos los campos.")

                elif len(nueva_p) < 4:
                    st.error("Mínimo 4 caracteres.")

                elif nueva_p != confirmar_p:
                    st.error("Las contraseñas no coinciden.")

                elif nuevo_u in st.session_state.usuarios_db:
                    st.error("Usuario ya existe.")

                else:

                    st.session_state.usuarios_db[nuevo_u] = {
                        "clave": nueva_p,
                        "rol": f"{nuevo_u.upper()} (CLIENTE)"
                    }

                    st.success(
                        f"✅ Cuenta '{nuevo_u}' creada. Ya puedes iniciar sesión."
                    )

    st.stop()


# ── NAVBAR ORIGINAL CORREGIDA ────────────────────────────────────────────────
idm_curr = st.session_state.idioma

st.markdown(f"""
<div style="
    width:100%;
    background:#060a12;
    border-bottom:1px solid #1a2744;
    padding:0 60px;
    height:62px;
    display:flex;
    align-items:center;
    justify-content:space-between;
">

    <div style="
        font-family:'Space Mono',monospace;
        font-size:1rem;
        font-weight:700;
        color:#fff;
        letter-spacing:3px;
        text-transform:uppercase;
    ">
        Object<span style="color:#0066ff">Vision</span>
    </div>

    <div style="display:flex; gap:10px;">

        <span style="
            font-size:0.65rem;
            letter-spacing:1px;
            text-transform:uppercase;
            color:#4a6080;
            background:rgba(26,39,68,0.5);
            border:1px solid #1a2744;
            padding:5px 12px;
            border-radius:6px;
            font-family:'Space Mono',monospace;
            font-weight:700;
        ">
            MobileNetV2
        </span>

        <span style="
            font-size:0.65rem;
            letter-spacing:1px;
            text-transform:uppercase;
            color:#4a6080;
            background:rgba(26,39,68,0.5);
            border:1px solid #1a2744;
            padding:5px 12px;
            border-radius:6px;
            font-family:'Space Mono',monospace;
            font-weight:700;
        ">
            PyTorch
        </span>

        <span style="
            font-size:0.65rem;
            letter-spacing:1px;
            text-transform:uppercase;
            color:#4a6080;
            background:rgba(26,39,68,0.5);
            border:1px solid #1a2744;
            padding:5px 12px;
            border-radius:6px;
            font-family:'Space Mono',monospace;
            font-weight:700;
        ">
            ImageNet
        </span>

    </div>

    <div class="nav-right-container">

        <div style="
            font-family:'Space Mono',monospace;
            font-size:0.72rem;
            color:#00d4aa;
            letter-spacing:1px;
            margin-right:10px;
        ">
            <span style="color:#00d4aa; margin-right:6px;">●</span>
            {st.session_state.rol_usuario}
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# ── BOTONES DE IDIOMA Y LOGOUT ───────────────────────────────────────────────
col_space, col_es, col_en, col_fr, col_logout = st.columns([8,1,1,1,2])

with col_es:
    if st.button("ES", key="btn_es"):
        st.session_state.lang_btn = "es"
        st.rerun()

with col_en:
    if st.button("EN", key="btn_en"):
        st.session_state.lang_btn = "en"
        st.rerun()

with col_fr:
    if st.button("FR", key="btn_fr"):
        st.session_state.lang_btn = "fr"
        st.rerun()

with col_logout:
    if st.button("🔴 SALIR", key="btn_logout"):
        st.session_state.logout_click = True
        st.rerun()


# Asignación de idioma activo tras renderizar
idioma = st.session_state.idioma