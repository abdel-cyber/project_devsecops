# SecNotes (version vulnérable)

**Usage strictement pédagogique et local/lab.**
Ne jamais exposer cette application sur Internet ou dans un environnement de production.

## Objectif
SecNotes est une mini API Express + MongoDB conçue pour accompagner un support DevSecOps :
- GitLab CI/CD
- GitLab Runner local
- SonarQube local
- Docker
- Kubernetes local
- Terraform / AWS

## Vulnérabilités pédagogiques incluses
- V1: NoSQL Injection
- V2: Secrets en dur
- V3: Absence de validation d'entrée
- V4: IDOR / contrôle d'accès insuffisant
- V5: Dépendances obsolètes / vulnérables
- V6: Hashage faible (MD5)
- V7: Dockerfile non sécurisé
- V8: Logs trop verbeux
- V9: Secrets Kubernetes en clair (base64)
- V10: CORS trop permissif

## Démarrage rapide
```bash
npm install
docker run -d --name secnotes-mongo -p 27017:27017 mongo:6
npm start
```

API disponible sur `http://localhost:3000`

## Endpoints
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/notes`
- `POST /api/notes`
- `GET /api/notes/:id`
- `PUT /api/notes/:id`
- `DELETE /api/notes/:id`
- `GET /api/notes/search?q=...`

## Exemple
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"azerty123","role":"admin"}'
```

## Remarque importante
Le code est volontairement faible pour que SonarQube, la revue de code et l'analyse manuelle aient de la matière.
