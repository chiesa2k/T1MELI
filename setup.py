"""
ASTROMETIC — Setup de instalação automática
Execute este arquivo UMA VEZ para configurar o ambiente completo:

    python setup.py
"""

import subprocess
import sys
import os

# ==============================================================================
# DEPENDÊNCIAS
# ==============================================================================
DEPENDENCIAS = [
    "playwright==1.57.0",
    "Pillow==12.1.0",
]

# ==============================================================================
# PASTAS QUE O SISTEMA PRECISA
# ==============================================================================
PASTAS = [
    "user_data",
    "sessao_zap",
    "prints_finais",
    "recortes",
    "rampup_brutos",
    "rampup_recortes",
]


def passo(numero, descricao):
    print(f"\n{'='*60}")
    print(f"  PASSO {numero}: {descricao}")
    print(f"{'='*60}")


def ok(msg):
    print(f"  [OK] {msg}")


def erro(msg):
    print(f"  [ERRO] {msg}")


def instalar_dependencias():
    passo(1, "Instalando dependências Python")
    for pacote in DEPENDENCIAS:
        print(f"  Instalando {pacote}...")
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", pacote],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            ok(f"{pacote} instalado.")
        else:
            erro(f"Falha ao instalar {pacote}:\n{resultado.stderr}")
            sys.exit(1)


def instalar_chromium():
    passo(2, "Instalando o browser Chromium (Playwright)")
    print("  Isso pode demorar alguns minutos na primeira vez...")
    resultado = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=False
    )
    if resultado.returncode == 0:
        ok("Chromium instalado com sucesso.")
    else:
        erro("Falha ao instalar o Chromium.")
        sys.exit(1)


def criar_pastas():
    passo(3, "Criando estrutura de pastas")
    for pasta in PASTAS:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            ok(f"Pasta criada: {pasta}/")
        else:
            print(f"  [--] Pasta já existe: {pasta}/")


def instrucoes_login():
    passo(4, "Próximos passos — Login (necessário uma vez por membro)")
    print("""
  O sistema precisa de dois logins antes de funcionar:

  ─────────────────────────────────────────────────────
  LOGIN 1: Looker Studio (renova diariamente)
  ─────────────────────────────────────────────────────
  1. Execute:  python rodar_tudo.py
  2. Um browser vai abrir pedindo login Google corporativo
  3. Faça o login normalmente
  4. A sessão fica salva em user_data/
  5. Feche o script (Ctrl+C) — já está configurado

  ATENÇÃO: Como o token da empresa renova todo dia,
  na primeira execução de cada dia pode ser necessário
  logar novamente se o browser pedir.

  ─────────────────────────────────────────────────────
  LOGIN 2: WhatsApp Web (só uma vez)
  ─────────────────────────────────────────────────────
  1. Execute:  python carteiro.py
  2. Um browser vai abrir com o QR Code do WhatsApp Web
  3. Escaneie com seu celular
  4. A sessão fica salva em sessao_zap/
  5. Não precisa repetir (até trocar de celular)

  ─────────────────────────────────────────────────────
  RESOLUÇÃO DO MONITOR
  ─────────────────────────────────────────────────────
  OBRIGATÓRIO: 1920x1080 (Full HD)
  Os recortes das imagens são calibrados para esse tamanho.
  Em outra resolução as imagens sairão erradas.
""")


def main():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║         ASTROMETIC — SETUP               ║")
    print("  ║   Automação de Relatórios Looker Studio  ║")
    print("  ╚══════════════════════════════════════════╝")
    print(f"\n  Python detectado: {sys.version}")
    print(f"  Diretório:        {os.getcwd()}")

    instalar_dependencias()
    instalar_chromium()
    criar_pastas()
    instrucoes_login()

    print("="*60)
    print("  SETUP CONCLUÍDO! Siga os passos de login acima.")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
