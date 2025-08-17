# handler.py
import runpod
import boto3
import os
from faster_whisper import WhisperModel

# --- CONFIGURAÇÃO INICIAL ---
# Isso é executado uma vez quando o pod inicia
print("Iniciando o worker...")
# Carregamos o modelo de IA na memória da GPU.
# 'base' é um modelo pequeno e rápido para testes. Mude para 'medium' ou 'large' para mais precisão.
# 'device="cuda"' garante que estamos usando a GPU.
model = WhisperModel("base", device="cuda", compute_type="float16")
print("Modelo Whisper carregado com sucesso.")

# Configura o cliente para conectar ao Cloudflare R2
s3_client = boto3.client(
    's3',
    endpoint_url=f"https://{os.environ.get('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY')
)
print("Cliente R2 configurado.")

# --- FUNÇÃO PRINCIPAL ---
# Esta função é chamada para cada job de transcrição
def handler(job):
    """
    Recebe um job, baixa o arquivo de áudio do R2, transcreve e retorna o texto.
    """
    print("Recebido novo job:", job)
    job_input = job['input']

    # Pegamos os dados que nosso site enviou
    bucket_name = job_input.get('bucketName')
    file_name = job_input.get('fileName')

    if not bucket_name or not file_name:
        return {"error": "bucketName e fileName são obrigatórios."}

    # Baixa o arquivo do R2 para um local temporário dentro do pod
    local_file_path = f"/tmp/{file_name}"
    print(f"Baixando arquivo '{file_name}' do bucket '{bucket_name}'...")
    s3_client.download_file(bucket_name, file_name, local_file_path)
    print("Download concluído.")

    # Executa a transcrição
    print("Iniciando a transcrição...")
    segments, info = model.transcribe(local_file_path, beam_size=5)
    print(f"Transcrição detectou idioma: {info.language} com probabilidade {info.language_probability}")

    # Junta todos os segmentos de texto em um único texto
    full_text = "".join(segment.text for segment in segments)

    # Limpa o arquivo baixado para liberar espaço
    os.remove(local_file_path)

    print("Transcrição finalizada.")

    # Retorna o resultado. Isso será o output do job.
    return {"transcription": full_text}


# --- INICIALIZAÇÃO ---
# Inicia o worker para que ele comece a ouvir por novos jobs
runpod.serverless.start({"handler": handler})
