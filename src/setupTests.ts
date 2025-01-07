import '@jest/globals';

// Mock global fetch if needed
global.fetch = jest.fn();

// Reset all mocks before each test
beforeEach(() => {
  jest.resetAllMocks();
  jest.clearAllMocks();
  (global.fetch as jest.Mock).mockClear();
});

// Clean up after each test
afterEach(() => {
  jest.restoreAllMocks();
});

// Add custom matchers if needed
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
});

// Add custom environment variables for testing
process.env.NODE_ENV = 'test';

// Increase timeout for async operations if needed
jest.setTimeout(10000);

// Suppress console output during tests
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};
