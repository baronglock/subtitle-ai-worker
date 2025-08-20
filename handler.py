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
print("Configurando cliente R2...")
print(f"R2_ACCOUNT_ID presente: {bool(os.environ.get('R2_ACCOUNT_ID'))}")
print(f"R2_ACCESS_KEY_ID presente: {bool(os.environ.get('R2_ACCESS_KEY_ID'))}")
print(f"R2_SECRET_ACCESS_KEY presente: {bool(os.environ.get('R2_SECRET_ACCESS_KEY'))}")

s3_client = boto3.client(
    's3',
    endpoint_url=f"https://{os.environ.get('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY')
)
print("Cliente R2 configurado com sucesso.")

# --- FUNÇÕES AUXILIARES ---
def format_timestamp(seconds):
    """Converte segundos para formato SRT (hh:mm:ss,ms)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

# --- FUNÇÃO PRINCIPAL ---
# Esta função é chamada para cada job de transcrição
def handler(job):
    """
    Recebe um job, baixa o arquivo de áudio do R2, transcreve e retorna SRT com timestamps.
    """
    print("Recebido novo job:", job)
    job_input = job['input']

    # Pegamos os dados que nosso site enviou
    bucket_name = job_input.get('bucketName')
    file_name = job_input.get('fileName')
    target_language = job_input.get('targetLanguage')  # Para futura implementação de tradução

    if not bucket_name or not file_name:
        return {"error": "bucketName e fileName são obrigatórios."}

    # Baixa o arquivo do R2 para um local temporário dentro do pod
    local_file_path = f"/tmp/{file_name}"
    print(f"Baixando arquivo '{file_name}' do bucket '{bucket_name}'...")
    
    try:
        print(f"Tentando baixar do bucket: {bucket_name}, arquivo: {file_name}")
        s3_client.download_file(bucket_name, file_name, local_file_path)
        print(f"Download concluído. Tamanho do arquivo: {os.path.getsize(local_file_path)} bytes")
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        return {"error": f"Erro ao baixar arquivo do R2: {str(e)}. Verifique se o arquivo '{file_name}' existe no bucket '{bucket_name}'."}

    # Executa a transcrição
    print("Iniciando a transcrição...")
    try:
        segments, info = model.transcribe(local_file_path, beam_size=5)
        print(f"Transcrição detectou idioma: {info.language} com probabilidade {info.language_probability}")
        
        # Converte generator em lista para processar
        segments_list = list(segments)
        
        # Gera texto completo
        full_text = " ".join(segment.text.strip() for segment in segments_list)
        
        # Gera formato SRT
        srt_lines = []
        for i, segment in enumerate(segments_list, 1):
            srt_lines.append(str(i))
            srt_lines.append(f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}")
            srt_lines.append(segment.text.strip())
            srt_lines.append("")  # Linha em branco
        
        srt_content = "\n".join(srt_lines)
        
        # Prepara segmentos em formato JSON
        segments_json = [
            {
                "id": i,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            for i, segment in enumerate(segments_list, 1)
        ]
        
    except Exception as e:
        return {"error": f"Erro na transcrição: {str(e)}"}
    finally:
        # Sempre limpa o arquivo
        if os.path.exists(local_file_path):
            os.remove(local_file_path)

    print("Transcrição finalizada.")

    # Retorna o resultado completo
    return {
        "transcription": full_text,
        "srt": srt_content,
        "segments": segments_json,
        "detected_language": info.language,
        "duration": info.duration
    }


# --- INICIALIZAÇÃO ---
# Inicia o worker para que ele comece a ouvir por novos jobs
runpod.serverless.start({"handler": handler})
