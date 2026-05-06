from config import setup_page, init_session
from ui.sidebar import sidebar_menu
from ui.pages import page_dashboard, page_manual, page_file

# ==========================================
# 4. MAIN APP
# ==========================================
def main():
    setup_page()
    init_session()

    menu = sidebar_menu()

    if menu == "Dashboard":
        page_dashboard()
    elif menu == "Enkripsi/Dekripsi Manual":
        page_manual()
    elif menu == "Proses File":
        page_file()


if __name__ == "__main__":
    main()