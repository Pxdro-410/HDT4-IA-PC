import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

FAQ_PATH = os.path.join(os.path.dirname(__file__), "data", "FAQs_Parachute_SA_Guatemala_2026.txt")

SYSTEM_PROMPT_TEMPLATE = """Eres un agente de preguntas frecuentes para Parachute S.A.
Tu trabajo es responder ÚNICAMENTE usando la información contenida en el siguiente documento de FAQs.
No inventes ni completes con conocimiento externo.
Si la pregunta del usuario no puede responderse con la información del documento, responde
exactamente que no cuentas con esa información y que recomiendas contactar a Parachute S.A.

--- INICIO DEL DOCUMENTO DE FAQs ---
{faq_content}
--- FIN DEL DOCUMENTO DE FAQs ---
"""


def load_faq(path: str) -> str:
    if not os.path.exists(path):
        print(f"Error: no se encontró el archivo de FAQs en '{path}'.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    base_url = os.getenv("NVIDIA_BASE_URL")
    if not api_key:
        print("Error: falta NVIDIA_API_KEY en el archivo .env.")
        sys.exit(1)
    return OpenAI(api_key=api_key, base_url=base_url)


def main() -> None:
    client = build_client()
    model = os.getenv("NVIDIA_MODEL")
    faq_content = load_faq(FAQ_PATH)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(faq_content=faq_content)}
    ]

    print("Agente de FAQs - Parachute S.A.")
    print("Escribe tu pregunta (o 'Bye' / Ctrl-C para salir).\n")

    try:
        while True:
            user_input = input("Tú: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "bye":
                print("Agente: ¡Hasta luego!")
                break

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})

            print(f"Agente: {answer}\n")
    except KeyboardInterrupt:
        print("\nAgente: ¡Hasta luego!")


if __name__ == "__main__":
    main()