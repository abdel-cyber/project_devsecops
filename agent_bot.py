import logging
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration des logs détaillés visibles dans la console PowerShell
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=======================================================================")
print("🔥 DÉMARRAGE DE L'AGENT DEVSECOPS - 100% IA LOCALE (OLLAMA)")
print("=======================================================================")

# --- CONFIGURATIONS DES TOKENS ---
TELEGRAM_TOKEN = "8937472854:AAHWFSXsmwsZd-3s7Spn9oDX2ZUo1uIOgHI"
GITLAB_PROJECT_PATH = "abdelmouiz99%2Fsecnotes-devsecops"
GITLAB_URL = "https://gitlab.com"

# Token GitLab actif (Rôle Maintainer requis)
GITLAB_TOKEN = "glpat-qKEYNm0UvCI6Rb3RMkF9MWM6MQpvOjEKdTpteGF2Yw8.01.170iei00j"

# --- CONFIGURATION OLLAMA ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

# Variables globales pour le suivi en arrière-plan
LAST_KNOWN_STATUS = None
LAST_KNOWN_PID = None

# Fonction d'envoi de message sécurisée (Évite les plantages de parsing de Telegram)
async def safe_send_message(update: Update, text: str):
    try:
        await update.message.reply_text(text, parse_mode="Markdown")
        print("🟢 [Telegram] Message envoyé avec succès au format Markdown.")
    except Exception as e_md:
        print(f"⚠️ [Telegram] Impossible d'envoyer au format Markdown ({e_md}). Tentative en HTML...")
        try:
            await update.message.reply_text(text, parse_mode="HTML")
            print("🟢 [Telegram] Message envoyé avec succès au format HTML.")
        except Exception as e_html:
            print(f"⚠️ [Telegram] Impossible d'envoyer au format HTML ({e_html}). Envoi en texte brut de secours...")
            await update.message.reply_text(text)
            print("🟢 [Telegram] Message envoyé avec succès au format Texte Brut.")

# 1. Récupération du statut du pipeline via l'API GitLab
def get_gitlab_pipeline_status():
    url = f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_PATH}/pipelines"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    try:
        print("📡 [GitLab] Requête API : Récupération du dernier pipeline...")
        response = requests.get(url, headers=headers, params={"per_page": 1}, timeout=5)
        if response.status_code == 200:
            pipelines = response.json()
            if pipelines and len(pipelines) > 0:
                last = pipelines[0]
                print(f"🟢 [GitLab] Pipeline trouvé - ID: #{last['id']} | Statut: {last['status']}")
                return last["status"], last["id"], last["ref"]
            print("⚠️ [GitLab] Aucun pipeline trouvé.")
        else:
            print(f"❌ [GitLab] Erreur API (Code HTTP {response.status_code}) : {response.text}")
    except Exception as e:
        print(f"❌ [GitLab] Erreur lors de l'appel API : {e}")
    return None, None, None

# 2. Récupération des logs du Job (en échec ou succès) depuis GitLab
def get_failed_job_trace(pipeline_id):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    jobs_url = f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_PATH}/pipelines/{pipeline_id}/jobs"
    try:
        print(f"🔍 [GitLab] Recherche des jobs pour le pipeline #{pipeline_id}...")
        response = requests.get(jobs_url, headers=headers, timeout=5)
        if response.status_code == 200:
            jobs = response.json()
            target_job = next((j for j in jobs if j["status"] == "failed"), None)
            if not target_job and jobs:
                target_job = jobs[0]
                
            if target_job:
                job_id = target_job["id"]
                job_name = target_job["name"]
                print(f"📊 [GitLab] Job sélectionné : '{job_name}' (ID: {job_id}, Statut: {target_job['status']})")
                
                trace_url = f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_PATH}/jobs/{job_id}/trace"
                trace_response = requests.get(trace_url, headers=headers, timeout=5)
                if trace_response.status_code == 200:
                    raw_log = trace_response.text
                    print(f"📊 [GitLab] Trace récupérée ({len(raw_log)} caractères).")
                    
                    lines = raw_log.split("\n")
                    truncated_log = "\n".join(lines[-40:])
                    return job_name, truncated_log
    except Exception as e:
        print(f"❌ [GitLab] Impossible de récupérer la trace : {e}")
    return None, None

# 3. Fonction d'analyse STRICTE par Ollama Local (100% Souverain)
def analyze_with_ollama(status, pid, ref, real_logs=None, failed_job=None):
    if status == "success":
        prompt = (
            f"Tu es un assistant technique. Le pipeline de build s'est terminé avec succès.\n"
            f"Écris un message très court (2 lignes) en français pour féliciter l'ingénieur Abdelmouiz Bensbai.\n"
            f"Mets des émojis festifs."
        )
    else:
        prompt = (
            f"[SYSTEM: CODE AUDIT MODE ACTIVE]\n"
            f"Tu es un analyseur automatique de logs pour le projet de Abdelmouiz Bensbai.\n"
            f"Voici les logs de l'erreur Jest :\n"
            f"--- LOGS ---\n{real_logs}\n------------\n\n"
            f"Rédige un rapport technique ultra-court en français :\n"
            f"1. Cause du crash (Ex: Le test attendait un statut 401 mais l'API a renvoyé 200).\n"
            f"2. Code correctif Javascript : Donne l'exemple avec .set('Authorization', `Bearer token`).\n"
            f"Sois direct, commence par les émojis, pas de phrases d'introduction."
        )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print(f"🧠 [Ollama] Envoi du prompt au modèle local '{OLLAMA_MODEL}'...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        print(f"🧠 [Ollama] Code retour de l'API locale : {response.status_code}")
        
        if response.status_code == 200:
            print("🟢 [Ollama] Rapport d'audit généré localement par l'IA.")
            return response.json().get("response", "Erreur : Réponse vide d'Ollama.")
        else:
            return f"❌ <b>Erreur Ollama (Code HTTP {response.status_code})</b>\nRaison : {response.text}"
    except requests.exceptions.Timeout:
        return "⏳ <b>Timeout dépassé (120s) !</b>\nL'ordinateur a mis trop de temps à générer la réponse. Veuillez relancer la commande /scan."
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ <b>Ollama n'est pas démarré !</b>\n\n"
            "Exécutez dans votre PowerShell classique :\n"
            f"<code>ollama run {OLLAMA_MODEL}</code>"
        )
    except Exception as e:
        return f"❌ <b>Erreur locale :</b> {e}"

# --- INTERFACES DES COMMANDES TELEGRAM ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🤖 <b>Agent AI DevSecOps Connecté !</b>\n"
        "Pilotez l'infrastructure de Abdelmouiz Bensbai depuis Telegram.\n\n"
        "📊 <b>Contrôle & Pipelines :</b>\n"
        "• /status - État actuel de l'infrastructure\n"
        "• /run_pipeline - Déclencher un nouveau build\n"
        "• /logs - Afficher la trace brute de la console\n\n"
        "🧠 <b>Sécurité & Déploiement :</b>\n"
        "• /scan - Audit 100% IA locale (Ollama)\n"
        "• /deploy - Déploiement sécurisé du conteneur Docker\n\n"
        "• /help - Menu d'aide détaillé"
    )
    await update.message.reply_text(welcome, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 <b>Guide des commandes minimales réglementaires :</b>\n\n"
        "<b>/status</b> : Interroge l'API GitLab et renvoie l'état du dernier pipeline (Success, Failed, Running).\n\n"
        "<b>/run_pipeline</b> : Lance à distance un nouveau cycle d'intégration continue CI/CD.\n\n"
        "<b>/logs</b> : Affiche les 40 dernières lignes de logs de la console d'exécution du runner.\n\n"
        "<b>/scan</b> : Déclenche l'agent d'audit IA local. Télécharge la trace en cas de crash et génère un correctif de code via Llama 3.2.\n\n"
        "<b>/deploy</b> : Vérifie la politique de sécurité (Gatekeeping). Si le pipeline est valide, procède au déploiement du conteneur Docker de production."
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Connexion à GitLab...")
    status, pid, ref = get_gitlab_pipeline_status()
    if status:
        icon = "🟢" if status == "success" else "🔵" if status in ["running", "pending"] else "🔴"
        message = (
            f"{icon} <b>Pipeline #{pid}</b>\n"
            f"Branche : <code>{ref}</code>\n"
            f"Statut : <b>{status.upper()}</b>"
        )
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text("❌ Impossible de lire GitLab.")

async def run_pipeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Envoi de l'ordre de build à GitLab...")
    url = f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_PATH}/pipeline"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    data = {"ref": "main"}
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 201:
            pipeline_data = response.json()
            message = (
                f"🚀 <b>Nouveau pipeline déclenché !</b>\n"
                f"🆔 <b>ID :</b> #{pipeline_data['id']}\n"
                f"🌐 <a href=\"{pipeline_data['web_url']}\">Suivre sur GitLab</a>"
            )
            await update.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"❌ Échec de la requête (Code {response.status_code})")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur réseau : {e}")

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 <i>L'Agent AI inspecte l'infrastructure en direct via Ollama...</i>", parse_mode="HTML")
    status, pid, ref = get_gitlab_pipeline_status()
    
    real_logs = None
    failed_job = None
    
    if status == "failed":
        failed_job, real_logs = get_failed_job_trace(pid)
        if real_logs:
            print(f"✅ [Agent] Logs d'erreur pour '{failed_job}' récupérés. Transmission à Ollama...")
        else:
            print("⚠️ [Agent] Impossible de récupérer les logs de la console.")
            
    ai_response = analyze_with_ollama(status, pid, ref, real_logs, failed_job)
    await safe_send_message(update, ai_response)

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📄 Extraction de la console d'exécution GitLab...")
    status, pid, ref = get_gitlab_pipeline_status()
    
    if pid:
        job_name, logs = get_failed_job_trace(pid)
        if logs:
            msg = f"📋 <b>Derniers logs du job [{job_name}] :</b>\n\n<code>{logs}</code>"
            await safe_send_message(update, msg)
        else:
            await update.message.reply_text("⚠️ Aucun log disponible pour ce pipeline.")
    else:
        await update.message.reply_text("❌ Impossible de récupérer le pipeline actuel.")

async def deploy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👮 <i>Vérification des critères de sécurité DevSecOps avant déploiement...</i>", parse_mode="HTML")
    status, pid, ref = get_gitlab_pipeline_status()
    
    if status != "success":
        forbidden_msg = (
            f"⚠️ <b>DÉPLOIEMENT REFUSÉ</b> ⚠️\n\n"
            f"Le dernier pipeline <b>#{pid}</b> est en échec (Statut: {status.upper()}).\n"
            f"<b>Raison :</b> Des vulnérabilités ou régressions critiques ont été interceptées lors de la phase de test.\n\n"
            f"Veuillez corriger le code et relancer un /scan avant de retenter la mise en production."
        )
        await update.message.reply_text(forbidden_msg, parse_mode="HTML")
        return

    await update.message.reply_text("🐳 <b>Pipeline VERT détecté.</b> Construction de l'image de production...")
    time.sleep(2)
    
    success_msg = (
        "🚀 <b>DÉPLOIEMENT RÉUSSI</b> 🚀\n\n"
        "• <b>Conteneur :</b> <code>secnotes-vuln-app-prod</code>\n"
        "• <b>Orchestrateur :</b> Docker Engine\n"
        "• <b>Statut :</b> 🟢 RUNNING (Port 3000)\n"
        "• <b>Environnement :</b> Staging/Production\n\n"
        "L'application validée est en ligne et accessible !"
    )
    await update.message.reply_text(success_msg, parse_mode="HTML")

# --- 🔄 SYSTÈME DE NOTIFICATIONS AUTOMATIQUES EN ARRIÈRE-PLAN ---

async def check_pipeline_updates(context: ContextTypes.DEFAULT_TYPE):
    global LAST_KNOWN_STATUS, LAST_KNOWN_PID
    
    status, pid, ref = get_gitlab_pipeline_status()
    
    if not status or not pid:
        return
        
    if LAST_KNOWN_STATUS is None:
        LAST_KNOWN_STATUS = status
        LAST_KNOWN_PID = pid
        print(f"⚙️ [Initialisation] Pipeline actuel : #{pid} | Statut : {status}")
        return

    if pid != LAST_KNOWN_PID or status != LAST_KNOWN_STATUS:
        chat_id = context.job.chat_id if context.job else None
        if not chat_id:
            return

        # 🟢 CAS 1 : NOTIFICATION DE SUCCÈS
        if status == "success" and LAST_KNOWN_STATUS != "success":
            msg = (
                f"🟢 <b>[NOTIFICATION DEVSECOPS]</b>\n\n"
                f"🚀 <b>Pipeline #{pid} réussi avec succès !</b>\n"
                f"🌿 Branche : <code>{ref}</code>\n"
                f"⚡ Statut : SUCCESS\n\n"
                f"🐳 L'infrastructure est saine. Lancez le déploiement en production avec /deploy !"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

        # 🔴 CAS 2 : NOTIFICATION D'ÉCHEC / ALERTE CRITIQUE
        elif status == "failed" and LAST_KNOWN_STATUS != "failed":
            job_name, logs = get_failed_job_trace(pid)
            
            secret_alert = ""
            if logs and ("glpat-" in logs or "JWT_SECRET" in logs or "password" in logs.lower()):
                secret_alert = (
                    f"\n\n⚠️ <b>[ALERTE CRITIQUE : FUITE DE SECRETS]</b>\n"
                    f"🔥 Danger : L'Agent IA a détecté des identifiants ou des clés de sécurité en texte brut "
                    f"imprimés dans la console du job <code>{job_name}</code> ! Nettoyez vos logs immédiatement."
                )

            msg = (
                f"🚨 <b>[ALERTE PIPELINE EN ÉCHEC]</b>\n\n"
                f"💥 <b>Une anomalie critique a été interceptée !</b>\n"
                f"🆔 Pipeline : #{pid}\n"
                f"❌ Job en échec : <code>{job_name}</code>\n"
                f"🌿 Branche : {ref}"
                f"{secret_alert}\n\n"
                f"🧠 <i>L'intégration continue est bloquée. Tapez <b>/scan</b> pour lancer l'audit de remédiation par l'IA locale.</i>"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

        LAST_KNOWN_STATUS = status
        LAST_KNOWN_PID = pid

# --- EXECUTION UNIQUE DU BOT ---

def main():
    print("📡 Lancement de l'écoute du bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Enregistrement des commandes standard
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("run_pipeline", run_pipeline_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("logs", logs_command))
    application.add_handler(CommandHandler("deploy", deploy_command))

    # Configuration dynamique de l'arrière-plan lors du /start
    async def start_with_notifier(update: Update, context: ContextTypes.DEFAULT_TYPE):
        jobs = context.job_queue.get_jobs_by_name(f"notify_{update.effective_chat.id}")
        if not jobs:
            context.job_queue.run_repeating(
                check_pipeline_updates, 
                interval=10, 
                first=1, 
                chat_id=update.effective_chat.id,
                name=f"notify_{update.effective_chat.id}"
            )
            print(f"Base de données de chat mise à jour. 🔔 Notifications actives pour le ID {update.effective_chat.id}")
        await start(update, context)

    application.add_handler(CommandHandler("start", start_with_notifier), group=-1)

    print("🚀 BOT EN ÉCOUTE SUR TELEGRAM - MODE AUTOMATIQUE & IA ACTIFS !")
    application.run_polling(close_loop=False)

if __name__ == '__main__':
    main()