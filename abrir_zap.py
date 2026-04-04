# ARQUIVO: abrir_zap.py
import asyncio
from playwright.async_api import async_playwright
import os

async def abrir_navegador():
    user_data_path = os.path.abspath(os.path.join(os.getcwd(), 'sessao_zap'))
    print("--- ABRINDO SESSÃO MANUAL DO WHATSAPP ---")
    print(f"Pasta de dados: {user_data_path}")
    
    async with async_playwright() as p:
        # Abre o Chromium exatamente com as mesmas configurações do Carteiro
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            headless=False,
            no_viewport=True,
            args=["--start-maximized"]
        )
        
        page = await context.new_page()
        await page.goto('https://web.whatsapp.com')
        
        print("\nNavegador aberto! Pode mexer à vontade.")
        print("Quando terminar, basta fechar a janela do navegador no 'X'.")
        
        # Isso faz o script ficar rodando até você fechar a aba do WhatsApp manualmente
        try:
            await page.wait_for_event("close", timeout=0)
        except:
            pass
            
        print("Navegador fechado. Encerrando script.")

if __name__ == "__main__":
    asyncio.run(abrir_navegador())