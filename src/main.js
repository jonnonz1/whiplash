import { mount } from 'svelte';
import './theme.css';
import App from './App.svelte';
import { initAnalytics } from './lib/analytics.js';

initAnalytics();

const app = mount(App, {
  target: document.getElementById('app'),
});

export default app;
