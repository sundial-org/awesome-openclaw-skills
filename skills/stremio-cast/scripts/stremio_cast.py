import asyncio
import sys
import subprocess
import time
from playwright.async_api import async_playwright

async def cast_stremio(query, device="Living Room"):
    print(f"[Moltbot] Iniciando Stremio para buscar: {query}")
    
    stremio_url = "https://app.strem.io/shell-v4.4/?streamingServer=https%3A%2F%2F192-168-15-162.519b6502d940.stremio.rocks%3A12470#/"
    stream_url = None

    async with async_playwright() as p:
        # Lançar navegador
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'])
        context = await browser.new_context()
        page = await context.new_page()

        # Interceptar requisições para encontrar a URL do stream
        async def handle_request(request):
            nonlocal stream_url
            url = request.url
            if 'stremio.rocks' in url and ('/stream/' in url or url.endswith('.mp4')):
                stream_url = url
                print(f"[Moltbot] URL de stream encontrada: {stream_url}")

        page.on("request", handle_request)

        try:
            # 1. Navegar para o Stremio
            await page.goto(stremio_url, wait_until="load", timeout=60000)

            # 2. Buscar conteúdo
            # Esperar pelo input de busca (seletor genérico baseado no rascunho)
            await page.wait_for_selector('input[type="text"]', timeout=10000)
            await page.fill('input[type="text"]', query)
            await page.keyboard.press("Enter")

            # 3. Selecionar o primeiro resultado
            # Seletor baseado no rascunho (.poster-container)
            await page.wait_for_selector('.poster-container', timeout=10000)
            await page.click('.poster-container')

            # 4. Selecionar o stream
            # Seletor baseado no rascunho (.stream-item)
            await page.wait_for_selector('.stream-item', timeout=15000)
            await page.click('.stream-item')

            # 5. Aguardar a URL do stream ser capturada
            start_time = time.time()
            while not stream_url and (time.time() - start_time < 45):
                await asyncio.sleep(1)

            if not stream_url:
                print("Erro: Não foi possível extrair a URL do stream dentro do tempo limite.")
                return False

            # 6. Executar o casting via CATT
            print(f"[Moltbot] Transmitindo para {device}...")
            try:
                # Nota: Assume que 'catt' está instalado no ambiente
                subprocess.Popen(['catt', '-d', device, 'cast', stream_url])
                print(f"Sucesso: Reproduzindo '{query}' em {device}.")
                # Mantemos o script rodando por um tempo para garantir que o stream inicie
                # No ambiente real, o processo pai deve gerenciar o ciclo de vida do navegador
                await asyncio.sleep(10) 
                return True
            except Exception as e:
                print(f"Erro ao executar CATT: {e}")
                return False

        except Exception as e:
            print(f"Erro durante a automação: {e}")
            return False
        finally:
            # Nota: Fechar o navegador pode interromper o servidor local de streaming do Stremio
            # se ele depender da aba aberta. Em uso real, pode ser necessário manter aberto.
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python stremio_cast.py <query> [device]")
        sys.exit(1)
    
    query_arg = sys.argv[1]
    device_arg = sys.argv[2] if len(sys.argv) > 2 else "Living Room"
    
    asyncio.run(cast_stremio(query_arg, device_arg))
