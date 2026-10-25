# AI Hunter V3 — Render + iPhone

**Pesquisa, não recomendação financeira.** O relatório do modelo V3 é `NO_VALIDATED_SIGNAL`, logo a API retorna `AGUARDAR` para todos os ativos. A pontuação é apenas saída bruta do classificador e não uma probabilidade calibrada de ganho.

## Publicação usando iPhone

1. No GitHub, crie um **repositório novo** chamado `ai-hunter-api`. Envie `render.yaml` na raiz e os arquivos de `server/` dentro da pasta `server` (incluindo `model_v3.joblib`). Não use o GitHub Pages para executar Python.
2. Em https://dashboard.render.com/ escolha **New → Blueprint** e conecte o repositório `ai-hunter-api`. Confirme o serviço do arquivo `render.yaml`. O plano gratuito pode adormecer e demorar para acordar. Confirme preços e limites atuais no Render antes de ativar.
3. Depois da publicação, abra `https://SEU-SERVICO.onrender.com/health` e verifique `model_loaded:true`. Se `false`, leia `model_error`. A URL exata é exibida pelo Render; não use uma URL de exemplo.
4. Envie `site/ai.html` ao seu repositório GitHub Pages `btc-signal-lab`, na raiz. Abra `https://wellintonjunio78-rgb.github.io/btc-signal-lab/ai.html` e cole a URL real do Render. Toque em **Conectar e analisar**.

## Segurança e limitações

- Arquivos `.joblib` podem executar código ao carregar. **Só implante se você confia no arquivo treinado por você**. O projeto ativa `TRUST_MODEL_FILE=yes` explicitamente no Render. Não carregamos o arquivo nesta sessão.
- API pública sem autenticação, somente leitura e sem chaves da Binance. Não adicione API keys nem credenciais ao repositório.
- O servidor busca até 130 velas por ativo; calcula as mesmas 12 features de `ml_core.py`, usando apenas velas fechadas.
- Não há execução de ordens, notificações push, sinais de VENDA, garantia de antecedência ou validação ao vivo. O iPhone só atualiza com a página aberta.
- Se o serviço não iniciar, consulte logs no painel do Render. Os pacotes podem precisar de versões compatíveis com a versão Python da hospedagem.
- O modelo não foi executado ou testado no Render neste ambiente. Verifique a resposta de `/health` e `/scan` após publicar.
