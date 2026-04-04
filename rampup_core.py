# ARQUIVO: rampup_core.py
import asyncio
from playwright.async_api import async_playwright
import os
import re
from PIL import Image
import json

# ==============================================================================
# CONFIGURAÇÕES EXCLUSIVAS DO RAMP UP
# ==============================================================================
AREA_DE_CORTE_RAMPUP = (539, 47, 1548, 809) 

TARGETS_RAMPUP = {
    "PICKING_TTS_MULTI":  {14: 103, 15: 110, 16: 112, 17: 109, 18: 117, 19: 120, 20: 122, 21: 111, 22: 104},
    "PICKING_NTT_MULTI":  {14: 73,  15: 95,  16: 102, 17: 98,  18: 96,  19: 101, 20: 93,  21: 94,  22: 85},
    "PACKING_TT_MONO":    {14: 182, 15: 229, 16: 217, 17: 212, 18: 205, 19: 219, 20: 229, 21: 227, 22: 203},
    "PACKING_NTT_MONO":   {14: 192, 15: 187, 16: 173, 17: 180, 18: 163, 19: 173, 20: 175, 21: 166, 22: 172},
    "PACKING_TT_MULTI":   {14: 246, 15: 275, 16: 279, 17: 262, 18: 247, 19: 260, 20: 250, 21: 243, 22: 221},
    "PTW":                {14: 492, 15: 550, 16: 558, 17: 524, 18: 494, 19: 520, 20: 500, 21: 486, 22: 442}
}

async def ler_horario_preciso(page):
    print("   [CÉREBRO] Lendo data e a definir horário...")
    regex = re.compile(r"\d{1,2}\s+de\s+[a-zç]+\.?\s+de\s+\d{4},\s+(\d{2}):(\d{2}):\d{2}", re.IGNORECASE)
    try:
        el = page.get_by_text(regex).first
        await el.wait_for(timeout=5000)
        match = regex.search(await el.inner_text())
        if match: return int(match.group(1)), int(match.group(2))
    except: pass
    return None, None

def calcular_hora_referencia(hora, minuto):
    h_ref = hora if minuto >= 40 else hora - 1
    if h_ref < 14: return 14
    if h_ref > 22: return 22
    return h_ref

def calcular_horas_filtro(hora, minuto):
    if hora < 14: return []
    lista = []
    for h in range(14, hora + 1):
        if h == hora:
            if minuto >= 40: lista.append(str(h))
        else:
            lista.append(str(h))
    return lista

async def aplicar_filtros_rampup(page, nome_relatorio, lista_horas, target):
    print(f"   [AÇÃO] A aplicar Target de {target} e horas {lista_horas}...")
    
    try:
        caixa_target = page.get_by_role("textbox", name="Insira um valor").first
        await caixa_target.wait_for(state="visible", timeout=5000)
        await caixa_target.click()
        await caixa_target.dblclick()
        await page.wait_for_timeout(500)
        await caixa_target.fill(str(target))
        await caixa_target.press("Enter")
        await page.wait_for_timeout(2000)
        print("   -> Target inserido com sucesso.")
    except Exception as e:
        print(f"   [!] Erro ao preencher Target: {e}")

    if lista_horas:
        try:
            caixa_hora = page.locator('div').filter(has_text=re.compile(r"^Hora:?$")).last
            await caixa_hora.locator('..').get_by_role("button").first.click(force=True)
        except:
            await page.get_by_text(re.compile(r"Hora.*", re.IGNORECASE)).first.click(force=True)
            
        await page.wait_for_timeout(2000)
        
        busca = page.get_by_role("combobox", name="Digite para pesquisar")
        await busca.wait_for()
        
        for i, h in enumerate(lista_horas):
            await busca.click(force=True)
            await page.wait_for_timeout(500)
            await busca.fill(h)
            await page.wait_for_timeout(2500)
            
            if i == 0: 
                check = page.get_by_role("checkbox", name=re.compile(f"^{h}$"))
                await check.hover()
                await page.wait_for_timeout(500)
                await page.get_by_role("button", name="somente").click(force=True)
            else: 
                await page.get_by_role("checkbox", name=re.compile(f"^{h}$")).click(force=True)
                
            await page.wait_for_timeout(1000)
            
            try: await page.get_by_role("button", name="Clear Input").click(force=True)
            except: await busca.fill("")
            await page.wait_for_timeout(1000)

        backdrop = page.locator(".popup-backdrop")
        if await backdrop.is_visible(): await backdrop.click(force=True)
        else: await page.mouse.click(600, 50)
        await page.wait_for_timeout(2000)

async def aguardar_carregamento(page):
    print("   [AÇÃO] Aguardando estabilização dos gráficos do Ramp Up...")
    try:
        loading_selector = ".md-progress-circular, .spinner, .loading-indicator"
        await page.wait_for_selector(loading_selector, state="hidden", timeout=10000)
        await page.wait_for_timeout(3000)
    except:
        await page.wait_for_timeout(5000)

async def detectar_erro_looker(page):
    erros_comuns = ["Erro de configuração", "System Error", "Configuração do conjunto de dados", "Ocorreu um erro", "Não foi possível"]
    for erro in erros_comuns:
        try:
            if await page.get_by_text(erro).first.is_visible():
                return True
        except: pass
    return False

async def iniciar_robo_rampup(links_dict):
    user_data_path = os.path.join(os.getcwd(), 'user_data')
    targets_utilizados = {} 
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            headless=False,
            viewport={"width": 1920, "height": 1080}, 
            args=["--start-maximized"],
            device_scale_factor=1
        )
        
        for nome, link in links_dict.items():
            
            if nome in ["PACKING_TT_MULTI", "PTW"]:
                print(f"\n   [SISTEMA] A iniciar '{nome}' como um novo sistema para limpar a memória...")
                await context.close()
                await asyncio.sleep(2)
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_path,
                    headless=False,
                    viewport={"width": 1920, "height": 1080}, 
                    args=["--start-maximized"],
                    device_scale_factor=1
                )

            sucesso = False
            tentativas = 3 
            
            while tentativas > 0 and not sucesso:
                page = await context.new_page()
                try:
                    print(f"\n>>> PROCESSANDO RAMP UP: {nome} (Tentativa {4 - tentativas}/3)")
                    
                    try:
                        await page.goto(link, wait_until='domcontentloaded')
                    except Exception as goto_err:
                        if "Download is starting" in str(goto_err):
                            print("   [!] Aviso: Bug de download detetado. A recarregar...")
                            await page.wait_for_timeout(5000)
                            await page.reload(wait_until='domcontentloaded')
                        else:
                            raise goto_err 

                    await page.wait_for_timeout(15000)
                    
                    hora, minuto = await ler_horario_preciso(page)
                    if hora:
                        lista_h = calcular_horas_filtro(hora, minuto)
                        h_ref = calcular_hora_referencia(hora, minuto)
                        valor_target = TARGETS_RAMPUP[nome][h_ref]
                        
                        targets_utilizados[nome] = valor_target
                        
                        try:
                            await asyncio.wait_for(aplicar_filtros_rampup(page, nome, lista_h, valor_target), timeout=80.0)
                        except asyncio.TimeoutError:
                            print("   [!] TIMEOUT: O painel bloqueou nos filtros (>80s). A atualizar...")
                            if not page.is_closed(): await page.close()
                            tentativas -= 1
                            continue 

                        await page.wait_for_timeout(3000) 
                        if await detectar_erro_looker(page):
                            print("   [!] Looker apresentou erro com os filtros. A recarregar...")
                            if not page.is_closed(): await page.close()
                            tentativas -= 1
                            continue 
                        
                        await aguardar_carregamento(page)
                        
                        pasta_brutos = 'rampup_brutos'
                        pasta_recortes = 'rampup_recortes'
                        if not os.path.exists(pasta_brutos): os.makedirs(pasta_brutos)
                        if not os.path.exists(pasta_recortes): os.makedirs(pasta_recortes)
                        
                        temp_bruto = f"{pasta_brutos}/temp_bruto_{nome}.png"
                        await page.screenshot(path=temp_bruto)
                        
                        # Recorta e salva na pasta correta SEM chamar o alfaiate
                        with Image.open(temp_bruto) as img:
                            corte = img.crop(AREA_DE_CORTE_RAMPUP)
                            destino = f"{pasta_recortes}/{nome}_RAMPUP.png"
                            corte.save(destino, quality=100, optimize=True)
                            print(f"   -> Print RECORTADO guardado: {destino}")
                        
                        sucesso = True 
                except Exception as e:
                    print(f"   -> ERRO em {nome}: {e}")
                    tentativas -= 1
                
                if not page.is_closed():
                    await page.close()
                    
        await context.close()
        
        try:
            with open('targets_rampup.json', 'w') as f:
                json.dump(targets_utilizados, f)
        except Exception as e:
            print(f"   [!] Erro ao guardar o ficheiro de targets: {e}")