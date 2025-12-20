# Migrare Date MongoDB Atlas → Docker

## Opțiunea 1: Export/Import Manual

### 1. Export din MongoDB Atlas
```bash
# Export toate colecțiile
# Înlocuiește cu credențialele tale din .env
mongodump --uri="mongodb+srv://USERNAME:PASSWORD@YOUR_CLUSTER.mongodb.net/YOUR_DATABASE" --out=./backup
```

### 2. Import în MongoDB Docker
```bash
# Pornește Docker
docker-compose up -d mongodb

# Import datele
# Folosește credențialele din .env (MONGO_USERNAME și MONGO_PASSWORD)
mongorestore --uri="mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@localhost:27017/${DB_NAME}?authSource=admin" ./backup/${DB_NAME}
```

---

## Opțiunea 2: Folosește MongoDB Atlas (Cloud)

Dacă vrei să continui cu Atlas, modifică `.env`:

```env
# Comentează MongoDB local
# MONGO_USERNAME=admin
# MONGO_PASSWORD=your_password
# MONGO_URL=mongodb://admin:your_password@mongodb:27017/mediconnect_db?authSource=admin

# Decomentează MongoDB Atlas
MONGO_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/YOUR_DATABASE?retryWrites=true&w=majority
DB_NAME=your_database_name
```

Și modifică `docker-compose.yml` să nu depindă de MongoDB:

```yaml
backend:
  depends_on:
    redis:
      condition: service_healthy
  # Șterge dependența de mongodb
```

---

## Recomandare

**Pentru Development:** Folosește MongoDB în Docker (mai rapid, offline, gratuit)
**Pentru Production:** Folosește MongoDB Atlas (managed, backup automat, scalabil)

---

## Test Conexiune

După ce pornești Docker:

```bash
# Test MongoDB
# Folosește credențialele din .env
docker exec -it mediconnect-mongodb-1 mongosh -u ${MONGO_USERNAME} -p ${MONGO_PASSWORD} --authenticationDatabase admin

# În mongosh:
use ${DB_NAME}
show collections
db.users.countDocuments()
```
