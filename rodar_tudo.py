# ARQUIVO: rodar_tudo.py
import asyncio
import robo_core
import subprocess  # Adicionado para poder executar o carteiro.py
import os          # Adicionado para checar se o arquivo existe

# FILA COMPLETA COM SEUS LINKS ORIGINAIS
LINKS_RELATORIOS = {
    "PICKING_TTS_MULTI": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580picking%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22,%22df638%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580RS%25EE%2580%2580MZ-3%25EE%2580%2580HV%25EE%2580%2580BL%22%7D",
    
    "PICKING_NTT_MULTI": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580picking%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22,%22df638%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580RK-L-P2S%25EE%2580%2580RK-L%25EE%2580%2580RK-H%22%7D",
    
    "PACKING_TT_MONO": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df628%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580TOT_SINGLE_SKU%25EE%2580%2580N%252FA%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22%7D",
    
    "PACKING_TT_MULTI": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df628%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580TOT_MULTI_BATCH%25EE%2580%2580N%252FA%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22%7D",
    
    "PACKING_NTT": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580packing%22,%22df628%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580NON_TOT_SINGLE_SKU%25EE%2580%2580N%252FA%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22%7D",
    
    "PTW": "https://lookerstudio.google.com/reporting/9c31074a-88e5-4cbe-baae-9372d6dae0ad/page/p_960xu7q98c?pli=1&params=%7B%22df623%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580putwallin%22,%22df628%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%2580N%252FA%22,%22df630%22:%22include%25EE%2580%25800%25EE%2580%2580IN%25EE%2580%25802%25C2%25BA%2520turno%22%7D"
}

async def loop_eterno():
    while True:
        print("\n=== INICIANDO RODADA DE ATUALIZAÇÃO ===")
        await robo_core.iniciar_robo(LINKS_RELATORIOS)
        
        # --- INÍCIO DA ADIÇÃO: Disparo do Carteiro ---
        print("\n=== TODOS OS RELATÓRIOS PROCESSADOS. DISPARANDO CARTEIRO... ===")
        try:
            if os.path.exists("carteiro.py"):
                # Roda o carteiro.py e espera ele terminar (com os 60s embutidos nele)
                subprocess.run(["python", "carteiro.py"], check=True)
                print("   -> Carteiro finalizado com sucesso!")
            else:
                print("   -> AVISO: Arquivo 'carteiro.py' não encontrado na pasta.")
        except Exception as e:
            print(f"   -> ERRO ao executar Carteiro: {e}")
        # --- FIM DA ADIÇÃO ---
        
        print("\n=== RODADA FINALIZADA. AGUARDANDO 1 HORA... ===")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(loop_eterno())