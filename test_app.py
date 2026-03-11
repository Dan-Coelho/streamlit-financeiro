from streamlit.testing.v1 import AppTest


def test_clique_no_botao():
    # 1. Carrega e roda o app inicial
    at = AppTest.from_file("app.py").run()

    # 2. Verifica se o valor inicial da tela é 0
    assert at.markdown.values[0] == "Valor: 0"

    # 3. Clica no primeiro (e único) botão da tela e recarrega o app
    at.button[0].click().run()

    # 4. Verifica se a tela atualizou o valor para 1
    assert at.markdown.values[0] == "Valor: 1"
