# ARQUIVO: carteiro.py
import asyncio
from playwright.async_api import async_playwright
import os

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
NOME_DO_GRUPO = 'ID/EA | Indicadores'
PASTA_PRINTS = 'recortes'

# Mapeamento: Nome do Arquivo -> Legenda em Negrito
LEGENDAS = {
    "PICKING_TTS_MULTI": "*EFICIÊNCIA OPERACIONAL PICKING TTS MULTI*",
    "PICKING_NTT_MULTI": "*EFICIÊNCIA OPERACIONAL PICKING NTT*",
    "PACKING_TT_MONO": "*EFICIÊNCIA OPERACIONAL PACKING TT MONO*",
    "PACKING_TT_MULTI": "*EFICIÊNCIA OPERACIONAL PACKING TT MULTI*",
    "PACKING_NTT": "*EFICIÊNCIA OPERACIONAL PACKING NTT*",
    "PTW": "*EFICIENCIA OPERACIONAL PTW*"
}

# Ordem de execução
ORDEM_RELATORIOS = [
    "PICKING_TTS_MULTI",
    "PICKING_NTT_MULTI",
    "PACKING_TT_MONO",
    "PACKING_TT_MULTI",
    "PACKING_NTT",
    "PTW"
]

async def enviar_mensagens():
    print("--- INICIANDO MENSAGEIRO (LEGENDAS EM NEGRITO) ---")
    
    user_data_path = os.path.abspath(os.path.join(os.getcwd(), 'sessao_zap'))
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            headless=False,
            no_viewport=True,
            args=["--start-maximized", "--force-device-scale-factor=1"]
        )
        
        page = await context.new_page()
        await page.goto('https://web.whatsapp.com')
        
        try:
            # 1. Busca o grupo
            print(f"   [ZAP] Localizando grupo: '{NOME_DO_GRUPO}'")
            await page.wait_for_selector('div[aria-label="Caixa de texto de pesquisa"]', timeout=60000)
            
            busca = page.get_by_label("Caixa de texto de pesquisa")
            await busca.click()
            await busca.fill(NOME_DO_GRUPO)
            await page.wait_for_timeout(2000)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000)

            # 2. Loop Sequencial (Texto -> Anexo -> Envio)
            for nome in ORDEM_RELATORIOS:
                caminho_img = os.path.abspath(f"{PASTA_PRINTS}/{nome}_RECORTE.png")
                
                if not os.path.exists(caminho_img):
                    print(f"   [!] Arquivo não encontrado: {nome}_RECORTE.png")
                    continue

                try:
                    # Recupera a legenda do dicionário
                    legenda_formatada = LEGENDAS.get(nome, f"*Relatório: {nome}*")
                    print(f"   [ZAP] Preparando: {nome}")

                    # PASSO 1: Digitar o texto no chat principal primeiro
                    caixa_mensagem = page.locator('footer div[contenteditable="true"]').first
                    await caixa_mensagem.click()
                    await page.keyboard.type(legenda_formatada, delay=50)
                    await page.wait_for_timeout(1000)

                    # PASSO 2: Abrir o anexo
                    await page.get_by_label("Anexar").click()
                    await page.wait_for_timeout(1000)

                    # PASSO 3: Inserir a imagem COM A CORREÇÃO DE STRICT MODE
                    async with page.expect_file_chooser() as fc_info:
                        await page.get_by_text("Fotos e vídeos", exact=True).first.click()
                    
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(caminho_img)

                    # PASSO 4: Enviar na tela de edição
                    print(f"      -> Enviando com legenda em negrito...")
                    await page.wait_for_timeout(5000) 
                    await page.keyboard.press("Enter")
                    
                    print(f"      [OK] Enviado: {legenda_formatada}")
                    await page.wait_for_timeout(4000)

                except Exception as e:
                    print(f"      [ERRO] Falha ao enviar {nome}: {e}")

            print("\n--- TODOS OS RELATÓRIOS FORAM ENVIADOS COM SUCESSO ---")
            
            # --- ADIÇÃO: PAUSA DE 60 SEGUNDOS NO FINAL ---
            print("   -> Aguardando 60 segundos antes de fechar para garantir o envio completo da última mensagem...")
            await page.wait_for_timeout(60000) 

        except Exception as e:
            print(f"   [ERRO CRÍTICO]: {e}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(enviar_mensagens())