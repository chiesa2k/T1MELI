# ARQUIVO: carteiro_rampup.py
import asyncio
from playwright.async_api import async_playwright
import os
import json

# ==============================================================================
# CONFIGURAÇÃO DO RAMP UP
# ==============================================================================
NOME_DO_GRUPO = 'ID/EA | Indicadores'
PASTA_PRINTS = 'rampup_recortes'

LEGENDAS_BASE = {
    "PICKING_TTS_MULTI": "*RAMP UP TL PICKING TT HXH*",
    "PICKING_NTT_MULTI": "*RAMP UP TL PICKING NTT HXH*",
    "PACKING_TT_MONO": "*RAMP UP TL PACKING TT HXH*",
    "PACKING_NTT_MONO": "*RAMP UP TL PACKING NTT HXH*",
    "PACKING_TT_MULTI": "*RAMP UP TL PTW HXH*",
    "PTW": "*RAMP UP TL WALL IN HXH*"
}

ORDEM_RELATORIOS = [
    "PICKING_TTS_MULTI",
    "PICKING_NTT_MULTI",
    "PACKING_TT_MONO",
    "PACKING_NTT_MONO",
    "PACKING_TT_MULTI",
    "PTW"
]

async def enviar_mensagens_rampup():
    print("--- INICIANDO MENSAGEIRO RAMP UP (FLUXO APROVADO) ---")
    
    targets_utilizados = {}
    if os.path.exists('targets_rampup.json'):
        try:
            with open('targets_rampup.json', 'r') as f:
                targets_utilizados = json.load(f)
        except: pass
    
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
                caminho_img = os.path.abspath(f"{PASTA_PRINTS}/{nome}_RAMPUP.png")
                
                if not os.path.exists(caminho_img):
                    print(f"   [!] Arquivo não encontrado: {nome}_RAMPUP.png")
                    continue

                try:
                    titulo = LEGENDAS_BASE.get(nome, f"*{nome}*")
                    target_usado = targets_utilizados.get(nome, "N/A") 
                    # Monta a legenda dinâmica com o Target
                    legenda_formatada = f"{titulo}\n🎯 TARGET: *{target_usado}*"
                    
                    print(f"   [ZAP] Preparando envio: {nome} (Target: {target_usado})")

                    # PASSO 1: Digitar o texto no chat principal primeiro
                    caixa_mensagem = page.locator('footer div[contenteditable="true"]').first
                    await caixa_mensagem.click()
                    await page.keyboard.insert_text(legenda_formatada) 
                    await page.wait_for_timeout(1000)

                    # PASSO 2: Abrir o anexo
                    await page.get_by_label("Anexar").click()
                    await page.wait_for_timeout(1000)

                    # PASSO 3: Inserir a imagem (Com a correção do exact=True)
                    async with page.expect_file_chooser() as fc_info:
                        await page.get_by_text("Fotos e vídeos", exact=True).first.click()
                    
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(caminho_img)

                    # PASSO 4: Enviar na tela de edição
                    print(f"      -> Enviando com legenda dinâmica...")
                    await page.wait_for_timeout(5000) 
                    await page.keyboard.press("Enter")
                    
                    print(f"      [OK] Enviado com sucesso.")
                    await page.wait_for_timeout(4000)

                except Exception as e:
                    print(f"      [ERRO] Falha ao enviar {nome}: {e}")

            print("\n--- TODOS OS RELATÓRIOS DE RAMP UP FORAM ENVIADOS COM SUCESSO ---")
            
            print("   -> Aguardando 60 segundos antes de fechar para garantir o envio completo...")
            await page.wait_for_timeout(60000) 

        except Exception as e:
            print(f"   [ERRO CRÍTICO]: {e}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(enviar_mensagens_rampup())