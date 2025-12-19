/**
 * Test Type Definitions
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:41 MST
 */

import '@types/jest';

declare global {
    const describe: jest.Describe;
    const test: jest.It;
    const expect: jest.Expect;
    const beforeEach: jest.Lifecycle;
    const afterEach: jest.Lifecycle;
    const beforeAll: jest.Lifecycle;
    const afterAll: jest.Lifecycle;
    const jest: jest.Jest;
}