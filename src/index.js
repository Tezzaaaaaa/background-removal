import { Container, getContainer } from '@cloudflare/containers';

export class BackgroundRemovalContainer extends Container {
  defaultPort = 8000;
  sleepAfter = '10m';
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/remove' || url.pathname === '/health') {
      const container = getContainer(env.BACKGROUND_REMOVAL);
      return container.fetch(request);
    }

    return env.ASSETS.fetch(request);
  },
};
