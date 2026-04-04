from PIL import Image
import os

# ==============================================================================
# COORDENADAS FINAIS
# ==============================================================================
# Esquerda: 255 | Topo: 30 | Direita: 1180 | Baixo: 580
AREA_DE_CORTE = (255, 30, 1180, 580)

def processar_imagem(caminho_original):
    """
    1. Lê a imagem da pasta 'prints_finais'.
    2. Recorta.
    3. Salva na pasta 'recortes'.
    """
    if not os.path.exists(caminho_original):
        print(f"   [ALFAIATE] ❌ Erro: Arquivo '{caminho_original}' não encontrado.")
        return

    try:
        # 1. Cria a pasta 'recortes' se ela não existir
        pasta_destino = "recortes"
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        with Image.open(caminho_original) as img:
            # 2. Faz o recorte
            img_recortada = img.crop(AREA_DE_CORTE)
            
            # 3. Monta o novo caminho
            # Pega apenas o nome do arquivo (ex: "PICKING.png") tirando o caminho da pasta antiga
            nome_arquivo = os.path.basename(caminho_original)
            
            # Adiciona o sufixo _RECORTE (opcional, ajuda a identificar)
            novo_nome = nome_arquivo.replace(".png", "_RECORTE.png")
            
            # Cria o caminho final: recortes/PICKING_RECORTE.png
            caminho_final = os.path.join(pasta_destino, novo_nome)
            
            # 4. Salva com qualidade máxima
            img_recortada.save(caminho_final, quality=100, subsampling=0)
            
            print(f"   [ALFAIATE] ✅ Recorte salvo na nova pasta: '{caminho_final}'")
            
    except Exception as e:
        print(f"   [ALFAIATE] ❌ Erro ao processar: {e}")