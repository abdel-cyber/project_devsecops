# 🤖 Agent IA DevSecOps Souverain - ChatOps & Orchestration K8s

[![Pipeline Status](https://img.shields.io/badge/GitLab%20CI%2FCD-Pipeline--Automated-orange?logo=gitlab)](https://gitlab.com)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage%20Build-blue?logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Local%20Orchestration-blue?logo=kubernetes)](https://kubernetes.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama3.2%3A1b%20Sovereign%20AI-purple)](https://ollama.com)

## 📌 Présentation du Projet
Ce projet a été réalisé individuellement par **Abdelmouiz Bensbai** dans le cadre du Projet de Fin de Semestre de 4ème année en Cycle Ingénieur, Spécialité Cybersécurité (Session 2025-2026).

L'objectif est de concevoir un **Agent Intelligent DevSecOps** hébergé localement, pilotable à 100% via un bot **Telegram**, capable de superviser et d'interagir avec un pipeline d'intégration continue GitLab, d'isoler des vulnérabilités applicatives (OWASP Top 10) et de gérer le déploiement sécurisé sur un cluster **Kubernetes Local**.



---

## 🏗️ Architecture Technique Réelle
Le flux d'exécution et d'échange de données suit un modèle ChatOps hermétique et souverain :
`Utilisateur Telegram` ➔ `Telegram Bot (Python)` ➔ `Ollama (Llama 3.2:1b Local)` ➔ `API GitLab SaaS` ➔ `GitLab Runner (Shell Local)` ➔ `Docker Desktop (Kubernetes & SonarQube)`

---

## 🛠️ Fonctionnalités de l'Agent Conversationnel

### 1. Contrôle de l'Infrastructure & Pipelines
* `/start` : Initialise l'agent et active la file d'attente d'arrière-plan (*Background Polling*) pour les notifications.
* `/status` : Interroge l'API GitLab et retourne l'état précis du dernier pipeline.
* `/run_pipeline` : Déclenche à distance un nouveau cycle complet d'intégration continue CI/CD.
* `/logs` : Extrait et formate les 40 dernières lignes de la trace console brute du Runner GitLab.
* `/help` : Affiche le guide complet d'utilisation.

### 2. Audit IA SecOps & Analyse de Secrets (`/scan`)
En cas de statut `FAILED`, l'agent télécharge la trace du job en échec, recherche la présence de secrets compromis (patterns `glpat-`, `JWT_SECRET`), et transmet les logs d'erreur Jest à l'IA souveraine locale **Llama 3.2:1b** pour générer instantanément un rapport technique de crash et un code correctif.

### 3. Déploiement Sécurisé & Gatekeeping (`/deploy`)
L'agent vérifie la politique de sécurité. Si le dernier pipeline a échoué (tests de sécurité au rouge), le déploiement est **strictement bloqué**. Si le pipeline est valide (`SUCCESS`), l'agent déclenche l'orchestration Kubernetes de l'application `SecNotes`.

### 4. Notifications Actives d'Arrière-Plan
Le bot intègre une routine asynchrone qui vérifie l'état de l'infrastructure toutes les 10 secondes et pousse de manière autonome :
* Les notifications de succès applicatif.
* Les alertes critiques DevSecOps en cas de crash du pipeline avec détection immédiate des fuites de secrets.

---

## 🚀 Guide d'Installation Rapide

### 1. Prérequis Système
* **Docker Desktop** avec le module **Kubernetes** activé.
* **Ollama Engine** chargé avec le modèle : `ollama run llama3.2:1b`.
* **Python 3.10+**.

### 2. Déploiement du Laboratoire SecOps (SonarQube & MongoDB)
Lancez les conteneurs de l'infrastructure d'analyse depuis votre terminal :
```bash
# Lancement de la base de données de test et du serveur SAST
docker run -d --name mongodb -p 27017:27017 mongo:7.0
docker run -d --name sonarqube -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:lts-community