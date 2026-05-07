import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

models = client.models.list()

print("\n✅ CURRENTLY ACTIVE GROQ MODELS:\n")
for m in sorted(models.data, key=lambda x: x.id):
    print(f"  {m.id}")

    
"""
  llama-3.3-70b-versatile
  meta-llama/llama-4-scout-17b-16e-instruct
  meta-llama/llama-prompt-guard-2-22m
  meta-llama/llama-prompt-guard-2-86m
  openai/gpt-oss-120b
  openai/gpt-oss-20b
  openai/gpt-oss-safeguard-20b
  qwen/qwen3-32b
  whisper-large-v3
  whisper-large-v3-turbo

  | Model                                             | Limits                         
| ------------------------------------------ | --------------------------------
| llama-3.3-70b-versatile                    |  30 RPM, 1K RPD, 12K TPM, 100K TPD     |
| meta-llama/llama-4-scout-17b-16e-instruct  |  30 RPM, 1K RPD, 30K TPM, 500K TPD     |
| meta-llama/llama-prompt-guard-2-22m        |  30 RPM, 14.4K RPD, 15K TPM, 500K TPD  |
| meta-llama/llama-prompt-guard-2-86m        |  30 RPM, 14.4K RPD, 15K TPM, 500K TPD  |
| openai/gpt-oss-120b                        |  30 RPM, 1K RPD, 8K TPM, 200K TPD      |
| openai/gpt-oss-20b                         |  30 RPM, 1K RPD, 8K TPM, 200K TPD      |
| openai/gpt-oss-safeguard-20b               |  30 RPM, 1K RPD, 8K TPM, 200K TPD      |
| qwen/qwen3-32b                             |  60 RPM, 1K RPD, 6K TPM, 500K TPD      |
| whisper-large-v3                           |  20 RPM, 2K RPD, 7.2K ASH, 28.8K ASD   |
| whisper-large-v3-turbo                     |  20 RPM, 2K RPD, 7.2K ASH, 28.8K ASD   |

"""