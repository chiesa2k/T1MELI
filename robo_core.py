# ARQUIVO: robo_core.py
import asyncio
from playwright.async_api import async_playwright
import os
import re
from PIL import Image
import alfaiate

# Coordenadas originais validadas
AREA_DE_CORTE = (330, 145, 1920, 1080) 

async def ler_horario_preciso(page):
    print("   [CÉREBRO] Lendo data...")
    regex = re.compile(r"\d{1,2}\s+de\s+[a-zç]+\.?\s+de\s+\d{4},\s+(\d{2}):(\d{2}):\d{2}", re.IGNORECASE)
    try:
        el = page.get_by_text(regex).first
        await el.wait_for(timeout=5000)
        match = regex.search(await el.inner_text())
        if match: return int(match.group(1)), int(match.group(2))
    except: pass
    return None, None

def calcular_horas(hora, minuto):
    if hora < 14: return []
    lista = []
    for h in range(14, hora + 1):
        if h == hora:
            if minuto >= 40: lista.append(str(h))
        else:
            lista.append(str(h))
    return lista

async def aguardar_carregamento(page):
    """Verifica se os indicadores de carregamento do Looker sumiram."""
    print("   [AÇÃO] Aguardando estabilização dos gráficos...")
    try:
        loading_selector = ".md-progress-circular, .spinner, .loading-indicator"
        await page.wait_for_selector(loading_selector, state="hidden", timeout=10000)
        await page.wait_for_timeout(3000)
    except:
        await page.wait_for_timeout(5000)

async def aplicar_filtro(page, lista):
    if not lista: return
    print("   [AÇÃO] Aplicando filtros de forma mais lenta...")
    
    await page.get_by_role("button", name=re.compile("Hora", re.IGNORECASE)).first.click(force=True)
    await page.wait_for_timeout(2000)
    
    busca = page.get_by_role("combobox", name="Digite para pesquisar")
    await busca.wait_for()
    
    for i, h in enumerate(lista):
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

async def detectar_erro_looker(page):
    """Procura por mensagens de erro na tela após aplicar os filtros."""
    # ==============================================================================
    # ADIÇÃO: Ignora gráficos vazios ("Não foi possível") e foca em erros reais
    # ==============================================================================
    erros_comuns = ["System Error", "Erro de sistema", "Ocorreu um erro fatal"]
    for erro in erros_comuns:
        try:
            # exact=True e timeout menor para não travar o robô
            if await page.get_by_text(erro, exact=True).first.is_visible(timeout=1000):
                return True
        except: pass
    return False

async def iniciar_robo(links_dict):
    user_data_path = os.path.join(os.getcwd(), 'user_data')
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            channel="chrome",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            device_scale_factor=1
        )

        for nome, link in links_dict.items():
            
            # ==============================================================================
            # REINÍCIO DE SISTEMA PARA OS ÚLTIMOS RELATÓRIOS
            # Fecha totalmente o navegador e abre de novo para limpar a memória RAM
            # ==============================================================================
            if nome in ["PACKING_NTT", "PTW"]:
                print(f"\n   [SISTEMA] Iniciando '{nome}' como um novo sistema para limpar a memória...")
                await context.close()
                await asyncio.sleep(2) # Pausa rápida para garantir que o Chrome fechou
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_path,
                    channel="chrome",
                    headless=False,
                    viewport={"width": 1920, "height": 1080},
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
                    device_scale_factor=1
                )
            # ==============================================================================

            sucesso = False
            tentativas = 3 
            
            while tentativas > 0 and not sucesso:
                page = await context.new_page()
                try:
                    print(f"\n>>> PROCESSANDO: {nome} (Tentativa {4 - tentativas}/3)")
                    
                    try:
                        await page.goto(link, wait_until='domcontentloaded')
                    except Exception as goto_err:
                        if "Download is starting" in str(goto_err):
                            print("   [!] Aviso: Bug de download detectado. Tentando contornar...")
                            await page.wait_for_timeout(5000)
                            await page.reload(wait_until='domcontentloaded')
                        else:
                            raise goto_err 

                    await page.wait_for_timeout(15000)
                    
                    hora, minuto = await ler_horario_preciso(page)
                    if hora:
                        lista_h = calcular_horas(hora, minuto)
                        
                        try:
                            await asyncio.wait_for(aplicar_filtro(page, lista_h), timeout=70.0)
                        except asyncio.TimeoutError:
                            print("   [!] TIMEOUT: O Looker travou ao aplicar os filtros (>70s). Atualizando a página...")
                            if not page.is_closed(): await page.close()
                            tentativas -= 1
                            continue 

                        await page.wait_for_timeout(3000) 
                        if await detectar_erro_looker(page):
                            print("   [!] Looker apresentou erro com os filtros. Fechando e abrindo o link novamente...")
                            if not page.is_closed(): await page.close()
                            tentativas -= 1
                            continue 
                        
                        await aguardar_carregamento(page)
                        
                        temp = "temp.png"
                        await page.screenshot(path=temp)
                        
                        with Image.open(temp) as img:
                            corte = img.crop(AREA_DE_CORTE)
                            destino = f"prints_finais/{nome}.png"
                            if not os.path.exists('prints_finais'): os.makedirs('prints_finais')
                            corte.save(destino, quality=100, optimize=True)
                            print(f"   -> Salvo: {destino}")
                            alfaiate.processar_imagem(destino)
                        
                        if os.path.exists(temp): os.remove(temp)
                        
                        sucesso = True 
                except Exception as e:
                    print(f"   -> ERRO em {nome}: {e}")
                    tentativas -= 1
                
                if not page.is_closed():
                    await page.close()
                    
        await context.close()