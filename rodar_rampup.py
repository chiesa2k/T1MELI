# ARQUIVO: rodar_rampup.py
import asyncio
import rampup_core
import subprocess
import os
import sys # <-- ADIÇÃO: Garante o uso do Python correto!

# Fila de relatórios exclusiva do Ramp Up com as suas URLs
LINKS_RAMPUP = {
    "PICKING_TTS_MULTI": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22,%22df220%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580picking%22,%22df231%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580RS%25EE%2580%2580HV%25EE%2580%2580BL%22%7D",
    "PICKING_NTT_MULTI": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22,%22df231%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580RK-L-P2S%25EE%2580%2580RK-L%25EE%2580%2580RK-H%22%7D",
    "PACKING_TT_MONO": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df220%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df225%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580TOT_SINGLE_SKU%25EE%2580%2580N%252FA%22,%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22%7D",
    "PACKING_NTT_MONO": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22,%22df220%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df225%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580NON_TOT_SINGLE_SKU%25EE%2580%2580N%252FA%22%7D",
    "PACKING_TT_MULTI": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df220%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22,%22df225%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580TOT_MULTI_BATCH%25EE%2580%2580N%252FA%22%7D",
    "PTW": "https://lookerstudio.google.com/reporting/8ff27737-d826-4b0e-b807-0109bf51bd8f/page/p_za17uvx0bd?pli=1&params=%7B%22df225%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580N%252FA%22,%22df220%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580putwallin%22,%22df222%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580BRRJ02%22%7D"
}

async def rodar_teste_rampup():
    print("\n=== INICIANDO RAMP UP ===")
    
    # 1. Inicia o robô para gerar os recortes
    await rampup_core.iniciar_robo_rampup(LINKS_RAMPUP)
    
    # 2. Quando finalizar as imagens, dispara o Carteiro
    print("\n=== TODOS OS RELATÓRIOS PROCESSADOS. DISPARANDO CARTEIRO RAMP UP... ===")
    try:
        if os.path.exists("carteiro_rampup.py"):
            # sys.executable garante que o Python correto será usado
            subprocess.run([sys.executable, "carteiro_rampup.py"], check=True)
            print("   -> Carteiro Ramp Up finalizado com sucesso!")
        else:
            print("   -> AVISO: Arquivo 'carteiro_rampup.py' não encontrado na pasta.")
    except Exception as e:
        print(f"   -> ERRO ao executar Carteiro Ramp Up: {e}")

if __name__ == "__main__":
    asyncio.run(rodar_teste_rampup())