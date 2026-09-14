import '@testing-library/jest-dom';

// Polyfill window.fetch for jsdom environment if needed
if (!globalThis.fetch) {
  // @ts-ignore
  globalThis.fetch = vi.fn().mockImplementation(() =>
    Promise.resolve({
      ok: true,
      headers: {
        get: () => 'application/json',
      },
      json: () =>
        Promise.resolve({
          status: 'ok',
          version: '0.1.0',
          environment: 'test',
          database: 'connected',
          redis: 'connected',
        }),
    })
  );
}
