const request = require('supertest');
const { MongoMemoryServer } = require('mongodb-memory-server');
const { connectDB, disconnectDB, setMongoUri } = require('../src/config/db');
const User = require('../src/models/User');

let mongod;
let app;

beforeAll(async () => {
  mongod = await MongoMemoryServer.create();
  setMongoUri(mongod.getUri('secnotes_test_auth'));
  await connectDB();
  app = require('../src/app');
});

afterEach(async () => {
  await User.deleteMany({});
});

afterAll(async () => {
  await disconnectDB();
  if (mongod) {
    await mongod.stop();
  }
});

describe('Auth routes', () => {
  test('register should create a user', async () => {
    const response = await request(app).post('/api/auth/register').send({
      username: 'alice',
      email: 'alice@example.com',
      password: 'azerty123',
      role: 'user'
    });

    expect(response.statusCode).toBe(201);
    expect(response.body.user.username).toBe('alice');
    expect(response.body.user.password).not.toBe('azerty123');
  });

  test('login should return a token after register', async () => {
    await request(app).post('/api/auth/register').send({
      username: 'bob',
      email: 'bob@example.com',
      password: 'azerty123',
      role: 'admin'
    });

    const login = await request(app).post('/api/auth/login').send({
      username: 'bob',
      password: 'azerty123'
    });

    expect(login.statusCode).toBe(200);
    expect(login.body.token).toBeDefined();
    expect(login.body.user.role).toBe('admin');
  });
});
