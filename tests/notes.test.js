const request = require('supertest');
const { MongoMemoryServer } = require('mongodb-memory-server');
const { connectDB, disconnectDB, setMongoUri } = require('../src/config/db');
const User = require('../src/models/User');
const Note = require('../src/models/Note');

let mongod;
let app;
let token;
let createdNoteId;

beforeAll(async () => {
  mongod = await MongoMemoryServer.create();
  setMongoUri(mongod.getUri('secnotes_test_notes'));
  await connectDB();
  app = require('../src/app');
});

beforeEach(async () => {
  await User.deleteMany({});
  await Note.deleteMany({});

  await request(app).post('/api/auth/register').send({
    username: 'charlie',
    email: 'charlie@example.com',
    password: 'azerty123',
    role: 'user'
  });

  const login = await request(app).post('/api/auth/login').send({
    username: 'charlie',
    password: 'azerty123'
  });

  token = login.body.token;
});

afterAll(async () => {
  await disconnectDB();
  if (mongod) {
    await mongod.stop();
  }
});

describe('Notes routes', () => {
  test('create and retrieve a note', async () => {
    const create = await request(app)
      .post('/api/notes')
      .set('Authorization', `Bearer ${token}`)
      .send({
        title: 'Note 1',
        content: 'Contenu de test',
        isPublic: true
      });

    expect(create.statusCode).toBe(201);
    createdNoteId = create.body._id;

    const get = await request(app)
      .get(`/api/notes/${createdNoteId}`)
      .set('Authorization', `Bearer ${token}`);

    expect(get.statusCode).toBe(200);
    expect(get.body.title).toBe('Note 1');
  });

  test('search should return notes by title', async () => {
    await request(app)
      .post('/api/notes')
      .set('Authorization', `Bearer ${token}`)
      .send({
        title: 'Projet Terraform',
        content: 'Cluster EKS',
        isPublic: false
      });

    const search = await request(app)
      .get('/api/notes/search?q=Terraform')
      .set('Authorization', `Bearer ${token}`);

    expect(search.statusCode).toBe(200);
    expect(Array.isArray(search.body)).toBe(true);
    expect(search.body.length).toBeGreaterThanOrEqual(1);
  });
});
