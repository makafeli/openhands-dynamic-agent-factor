"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("@jest/globals");
// Increase timeout for all tests
jest.setTimeout(10000);
// Mock axios for HTTP requests
jest.mock('axios', () => ({
    create: jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
            request: { use: jest.fn(), eject: jest.fn() },
            response: { use: jest.fn(), eject: jest.fn() }
        }
    })),
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() }
    }
}));
// Mock cheerio
jest.mock('cheerio', () => ({
    load: jest.fn(() => ({
        find: jest.fn(),
        text: jest.fn(),
        html: jest.fn()
    }))
}));
// Global test setup
beforeAll(() => {
    // Clear all mocks before each test suite
    jest.clearAllMocks();
});
beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
});
afterEach(() => {
    // Clean up after each test
    jest.clearAllMocks();
});
afterAll(() => {
    // Clean up after all tests
    jest.clearAllMocks();
});
//# sourceMappingURL=setupTests.js.map