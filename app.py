# --- COLONNE CENTRALE : EXCLUSIF FOREX FACTORY RED NEWS ---
with col_center:
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.subheader("🔴 FOREX FACTORY — HIGH IMPACT ONLY")
    with col_hdr2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if ff_events:
        html_out = '<div class="ff-container">'
        current_cat = ""
        
        for ev in ff_events:
            if ev['category'] != current_cat:
                current_cat = ev['category']
                html_out += f'<div class="ff-day-header">{current_cat}</div>'
                
            # HTML condensé sur une ligne pour éviter le bug d'indentation Markdown
            html_out += (
                f'<div class="ff-row">'
                f'<span class="ff-time">{ev["time_str"]}</span>'
                f'<span class="ff-currency">{ev["currency"]}</span>'
                f'<span class="ff-title" title="{ev["title"]}">{ev["title"]}</span>'
                f'<div class="ff-val-box">'
                f'<span>Prév: <b class="ff-val">{ev["forecast"]}</b></span>'
                f'<span>Préc: <b class="ff-val">{ev["previous"]}</b></span>'
                f'</div>'
                f'</div>'
            )
            
        html_out += '</div>'
        st.markdown(html_out, unsafe_allow_html=True)
    else:
        st.info("Aucune annonce économique majeure à fort impact (Dossier Rouge) prévue pour Aujourd'hui ou Demain.")

    st.divider()
    
    st.subheader("⚡ Analyse IA du Prochain Événement")
    if st.button("🔍 Analyser le risque du prochain événement rouge"):
        if ff_events:
            nxt = ff_events[0]
            with st.spinner("Analyse par Gemini..."):
                prompt = f"L'événement économique '{nxt['title']}' sur la devise {nxt['currency']} a lieu à {nxt['time_str']}. Prévision: {nxt['forecast']}, Précédent: {nxt['previous']}. En 2 phrases, explique l'impact attendu si la donnée dépasse la prévision."
                st.info(query_gemini(prompt))
        else:
            st.write("Aucune annonce rouge à analyser.")
