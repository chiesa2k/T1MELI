# ARQUIVO: primeiro_login.py
# Abre o Chrome com a sessão do sistema para o usuário fazer o login
# do dia na conta Google. Após logar, feche o terminal com Ctrl+C.
import asyncio
from playwright.async_api import async_playwright
import os

URL_LOOKER = "https://lookerstudio.google.com/"

async def abrir_login():
    user_data_path = os.path.join(os.getcwd(), 'user_data')
    os.makedirs(user_data_path, exist_ok=True)

    print("\n=== PRIMEIRO LOGIN DO DIA ===")
    print("   O Chrome vai abrir com a página do Looker Studio.")
    print("   Faça o login com a conta Google corporativa.")
    print("   Quando terminar, feche o terminal com Ctrl+C.\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            channel="chrome",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            args=["--start-maximized"],
            device_scale_factor=1
        )

        page = await context.new_page()
        await page.goto(URL_LOOKER, wait_until='domcontentloaded')

        print("   [AGUARDANDO] Faça o login e pressione Ctrl+C quando terminar...")

        # Mantém o browser aberto até o usuário fechar manualmente
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass

        await context.close()
        print("\n   [OK] Sessão salva em 'user_data/'. Pode fechar.")

if __name__ == "__main__":
    try:
        asyncio.run(abrir_login())
    except KeyboardInterrupt:
        print("\n   [OK] Login concluído. Sessão guardada.")
