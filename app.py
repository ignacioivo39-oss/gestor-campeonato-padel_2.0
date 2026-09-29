import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(
    page_title="Gestor de Campeonato de Pádel",
    page_icon="🎾",
    layout="wide"
)

# ---------------- CONFIGURACIÓN VISUAL ----------------

st.title("🎾 Gestor de Campeonato de Pádel")
st.caption("Administra inscripciones, fixture, resultados y posiciones.")

# ---------------- DATOS DE SESIÓN ----------------

if "parejas" not in st.session_state:
    st.session_state.parejas = []

if "partidos" not in st.session_state:
    st.session_state.partidos = []

if "config" not in st.session_state:
    st.session_state.config = {
        "nombre": "Campeonato de Pádel",
        "canchas": 2,
        "puntos_ganar": 3
    }

# ---------------- MENÚ ----------------

menu = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "⚙️ Configuración",
        "👥 Inscripciones",
        "📅 Fixture",
        "🏆 Resultados",
        "📊 Tabla de posiciones"
    ]
)

# ---------------- FUNCIONES ----------------

def generar_fixture(parejas):
    partidos = []

    grupos = {}
    for pareja in parejas:
        clave = (pareja["Categoría"], pareja["Grupo"])
        grupos.setdefault(clave, []).append(pareja)

    numero = 1

    for (categoria, grupo), integrantes in grupos.items():
        for p1, p2 in combinations(integrantes, 2):
            partidos.append({
                "ID": numero,
                "Categoría": categoria,
                "Grupo": grupo,
                "Pareja 1": p1["Pareja"],
                "Pareja 2": p2["Pareja"],
                "Jugador(es) 1": f'{p1["Jugador 1"]} / {p1["Jugador 2"]}',
                "Jugador(es) 2": f'{p2["Jugador 1"]} / {p2["Jugador 2"]}',
                "Cancha": ((numero - 1) % st.session_state.config["canchas"]) + 1,
                "Puntos 1": None,
                "Puntos 2": None,
                "Estado": "Pendiente"
            })
            numero += 1

    return partidos


def calcular_tabla():
    filas = []

    for pareja in st.session_state.parejas:
        pj = pg = pp = puntos = favor = contra = 0

        for partido in st.session_state.partidos:
            if partido["Estado"] != "Jugado":
                continue

            if partido["Pareja 1"] == pareja["Pareja"]:
                pj += 1
                favor += partido["Puntos 1"]
                contra += partido["Puntos 2"]

                if partido["Puntos 1"] > partido["Puntos 2"]:
                    pg += 1
                    puntos += st.session_state.config["puntos_ganar"]
                else:
                    pp += 1

            elif partido["Pareja 2"] == pareja["Pareja"]:
                pj += 1
                favor += partido["Puntos 2"]
                contra += partido["Puntos 1"]

                if partido["Puntos 2"] > partido["Puntos 1"]:
                    pg += 1
                    puntos += st.session_state.config["puntos_ganar"]
                else:
                    pp += 1

        filas.append({
            "Categoría": pareja["Categoría"],
            "Grupo": pareja["Grupo"],
            "Pareja": pareja["Pareja"],
            "PJ": pj,
            "PG": pg,
            "PP": pp,
            "Puntos": puntos,
            "Favor": favor,
            "Contra": contra,
            "Diferencia": favor - contra
        })

    tabla = pd.DataFrame(filas)

    if not tabla.empty:
        tabla = tabla.sort_values(
            by=["Categoría", "Grupo", "Puntos", "PG", "Diferencia", "Favor"],
            ascending=[True, True, False, False, False, False]
        )

    return tabla


# ---------------- PÁGINAS ----------------

if menu == "🏠 Inicio":
    st.header(st.session_state.config["nombre"])
    st.write("Panel general del campeonato.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Parejas inscritas", len(st.session_state.parejas))
    c2.metric("Partidos programados", len(st.session_state.partidos))
    jugados = sum(
        1 for p in st.session_state.partidos if p["Estado"] == "Jugado"
    )
    c3.metric("Partidos jugados", jugados)

    st.info(
        "Comienza configurando el campeonato, registra las parejas "
        "y luego genera el fixture."
    )

elif menu == "⚙️ Configuración":
    st.header("⚙️ Configuración del campeonato")

    with st.form("configuracion"):
        nombre = st.text_input(
            "Nombre del campeonato",
            value=st.session_state.config["nombre"]
        )
        canchas = st.number_input(
            "Cantidad de canchas",
            min_value=1,
            max_value=20,
            value=st.session_state.config["canchas"]
        )
        puntos = st.number_input(
            "Puntos por partido ganado",
            min_value=1,
            max_value=10,
            value=st.session_state.config["puntos_ganar"]
        )

        guardar = st.form_submit_button("Guardar configuración")

        if guardar:
            st.session_state.config = {
                "nombre": nombre,
                "canchas": int(canchas),
                "puntos_ganar": int(puntos)
            }
            st.success("Configuración guardada.")

elif menu == "👥 Inscripciones":
    st.header("👥 Inscripción de parejas")

    with st.form("registro_pareja", clear_on_submit=True):
        categoria = st.text_input("Categoría", placeholder="Ej. 3ra, 4ta, Damas")
        grupo = st.text_input("Grupo", placeholder="Ej. A, B, C")
        nombre_pareja = st.text_input("Nombre de la pareja")
        jugador1 = st.text_input("Nombre del jugador 1")
        jugador2 = st.text_input("Nombre del jugador 2")

        registrar = st.form_submit_button("＋ Registrar pareja")

        if registrar:
            if not all([categoria, grupo, nombre_pareja, jugador1, jugador2]):
                st.error("Completa todos los campos.")
            elif any(
                p["Pareja"].lower() == nombre_pareja.lower()
                for p in st.session_state.parejas
            ):
                st.error("Ya existe una pareja con ese nombre.")
            else:
                st.session_state.parejas.append({
                    "Categoría": categoria.strip(),
                    "Grupo": grupo.strip(),
                    "Pareja": nombre_pareja.strip(),
                    "Jugador 1": jugador1.strip(),
                    "Jugador 2": jugador2.strip()
                })
                st.success(f"Pareja {nombre_pareja} registrada.")

    st.subheader("Parejas inscritas")

    if st.session_state.parejas:
        st.dataframe(
            pd.DataFrame(st.session_state.parejas),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Todavía no hay parejas inscritas.")

elif menu == "📅 Fixture":
    st.header("📅 Fixture de grupos")

    st.write(
        "Se generará una rueda de todos contra todos para cada combinación "
        "de categoría y grupo."
    )

    if st.button("Generar fixture", type="primary"):
        if len(st.session_state.parejas) < 2:
            st.error("Registra al menos dos parejas.")
        else:
            st.session_state.partidos = generar_fixture(
                st.session_state.parejas
            )
            st.success("Fixture generado correctamente.")

    if st.session_state.partidos:
        st.dataframe(
            pd.DataFrame(st.session_state.partidos),
            use_container_width=True,
            hide_index=True
        )

        csv = pd.DataFrame(st.session_state.partidos).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar fixture CSV",
            data=csv,
            file_name="fixture_padel.csv",
            mime="text/csv"
        )

elif menu == "🏆 Resultados":
    st.header("🏆 Ingreso de resultados")

    pendientes = [
        p for p in st.session_state.partidos if p["Estado"] == "Pendiente"
    ]

    if not st.session_state.partidos:
        st.info("Primero debes generar el fixture.")
    elif not pendientes:
        st.success("Todos los partidos tienen resultado.")
    else:
        opciones = {
            f'Partido {p["ID"]}: {p["Pareja 1"]} vs {p["Pareja 2"]} '
            f'(Cancha {p["Cancha"]})': p["ID"]
            for p in pendientes
        }

        seleccionado = st.selectbox("Selecciona un partido", list(opciones.keys()))
        partido_id = opciones[seleccionado]
        partido = next(
            p for p in st.session_state.partidos if p["ID"] == partido_id
        )

        st.write(f'**{partido["Pareja 1"]}** vs **{partido["Pareja 2"]}**')

        with st.form("resultado"):
            col1, col2 = st.columns(2)

            with col1:
                puntos1 = st.number_input(
                    f'Puntos - {partido["Pareja 1"]}',
                    min_value=0,
                    max_value=99,
                    value=0
                )

            with col2:
                puntos2 = st.number_input(
                    f'Puntos - {partido["Pareja 2"]}',
                    min_value=0,
                    max_value=99,
                    value=0
                )

            guardar_resultado = st.form_submit_button("Guardar resultado")

            if guardar_resultado:
                if puntos1 == puntos2:
                    st.error("El partido no puede terminar empatado.")
                else:
                    partido["Puntos 1"] = int(puntos1)
                    partido["Puntos 2"] = int(puntos2)
                    partido["Estado"] = "Jugado"
                    st.success("Resultado guardado.")

    st.subheader("Partidos")

    if st.session_state.partidos:
        st.dataframe(
            pd.DataFrame(st.session_state.partidos),
            use_container_width=True,
            hide_index=True
        )

elif menu == "📊 Tabla de posiciones":
    st.header("📊 Tabla de posiciones")

    tabla = calcular_tabla()

    if tabla.empty:
        st.info("Registra parejas para visualizar la tabla.")
    else:
        categorias = sorted(tabla["Categoría"].unique())
        categoria_sel = st.selectbox("Filtrar categoría", categorias)

        tabla_filtrada = tabla[tabla["Categoría"] == categoria_sel]

        grupos = ["Todos"] + sorted(tabla_filtrada["Grupo"].unique())
        grupo_sel = st.selectbox("Filtrar grupo", grupos)

        if grupo_sel != "Todos":
            tabla_filtrada = tabla_filtrada[
                tabla_filtrada["Grupo"] == grupo_sel
            ]

        st.dataframe(
            tabla_filtrada,
            use_container_width=True,
            hide_index=True
        )

        csv = tabla_filtrada.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar tabla CSV",
            data=csv,
            file_name="tabla_posiciones_padel.csv",
            mime="text/csv"
        )

st.sidebar.divider()
st.sidebar.caption("Gestor de Campeonato de Pádel · Versión inicial")
